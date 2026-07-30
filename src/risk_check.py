"""
Taiwan Strait Risk Monitor — standalone, no external dependencies.

Fetches China-Taiwan conflict probabilities from Polymarket's public Gamma API,
applies alert thresholds, and sends a daily brief via ntfy.sh push notification.
Nominal days send at low priority (quiet); threshold breaches send as urgent.

Runs on GitHub Actions (see .github/workflows/risk_check.yml).
Requires env var: NTFY_TOPIC (your secret ntfy.sh topic name).
"""

import json
import os
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timezone

# ---------------- Config ----------------
MARKETS = [
    {"slug": "china-x-taiwan-military-clash-before-2027", "label": "Clash before 2027"},
    {"slug": "will-china-invade-taiwan-by-june-30-2027", "label": "Invasion by Jun 2027"},
]
FALLBACK_URL = ("https://gamma-api.polymarket.com/events"
                "?tag_slug=taiwan&active=true&closed=false&limit=10&order=volume&ascending=false")

# Alert rules
ABS_THRESHOLD = 0.15      # any Yes probability >= 15%
DAY_MOVE = 0.03           # 1-day move >= +3 points
WEEK_MOVE = 0.05          # 1-week move >= +5 points

HISTORY_FILE = "data/risk_history.json"
GAMMA = "https://gamma-api.polymarket.com/events?slug={}"


def http_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "taiwan-risk-monitor/1.0"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def open_market(event):
    """First non-closed market in an event, or None."""
    for m in event.get("markets", []):
        if not m.get("closed"):
            return m
    return None


def fetch_market(slug, label):
    try:
        events = http_json(GAMMA.format(urllib.parse.quote(slug)))
        if events:
            m = open_market(events[0])
            if m:
                return parse_market(m, label, substituted=False)
    except Exception as e:
        print(f"WARN: {slug} fetch failed: {e}")
    return None


def parse_market(m, label, substituted):
    return {
        "label": label,
        "question": m.get("question", label),
        "yes": float(json.loads(m["outcomePrices"])[0]),
        "d1": m.get("oneDayPriceChange") or 0.0,
        "d7": m.get("oneWeekPriceChange") or 0.0,
        "d30": m.get("oneMonthPriceChange") or 0.0,
        "vol24": m.get("volume24hr") or 0.0,
        "ends": m.get("endDateIso", "?"),
        "substituted": substituted,
    }


def fetch_fallback(needed):
    """If configured slugs are dead (markets roll over), find successors by keyword."""
    out = []
    try:
        events = http_json(FALLBACK_URL)
        for ev in events:
            title = (ev.get("title") or "").lower()
            if any(k in title for k in ("invade", "invasion", "clash", "attack", "blockade")):
                m = open_market(ev)
                if m:
                    out.append(parse_market(m, ev.get("title", "Taiwan market"), substituted=True))
            if len(out) >= needed:
                break
    except Exception as e:
        print(f"WARN: fallback fetch failed: {e}")
    return out


def check_alerts(markets):
    alerts = []
    for m in markets:
        p = m["yes"] * 100
        if m["yes"] >= ABS_THRESHOLD:
            alerts.append(f"{m['label']} at {p:.1f}% (>= {ABS_THRESHOLD*100:.0f}% threshold)")
        if m["d1"] >= DAY_MOVE:
            alerts.append(f"{m['label']} jumped +{m['d1']*100:.1f}pts in 24h")
        if m["d7"] >= WEEK_MOVE:
            alerts.append(f"{m['label']} up +{m['d7']*100:.1f}pts in 7 days")
    return alerts


def fmt_delta(x):
    pts = x * 100
    return f"{'+' if pts >= 0 else ''}{pts:.1f}pt"


def build_message(markets, alerts):
    lines = []
    if alerts:
        for a in alerts:
            lines.append(f"⚠ {a}")
        lines.append("")
        lines.append("Verify before acting: markets can gap and misprice. "
                     "Check taiwantracker.org and primary reporting. Not financial advice.")
        lines.append("")
    for m in markets:
        sub = " (substituted market)" if m["substituted"] else ""
        lines.append(
            f"{m['label']}{sub}: {m['yes']*100:.1f}%  "
            f"(1d {fmt_delta(m['d1'])} | 1w {fmt_delta(m['d7'])} | 1m {fmt_delta(m['d30'])})"
        )
    lines.append(f"Vol 24h: ${sum(m['vol24'] for m in markets):,.0f} · polymarket.com")
    return "\n".join(lines)


def send_ntfy(title, text, urgent):
    topic = os.environ.get("NTFY_TOPIC")
    if not topic:
        print("ERROR: NTFY_TOPIC not set")
        sys.exit(1)
    # JSON API: UTF-8 titles/emoji go in the body, not HTTP headers
    payload = json.dumps({
        "topic": topic,
        "title": title,
        "message": text,
        "priority": 5 if urgent else 2,
        "tags": ["rotating_light", "warning"] if urgent else ["green_circle"],
    }).encode("utf-8")
    req = urllib.request.Request(
        "https://ntfy.sh/",
        data=payload,
        headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        print("ntfy:", r.status)


def append_history(markets):
    os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    history = []
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, encoding="utf-8") as f:
                history = json.load(f)
        except Exception:
            history = []
    history.append({
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        **{m["label"]: round(m["yes"], 4) for m in markets},
    })
    history = history[-730:]  # keep ~2 years
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=1)


def main():
    markets = [m for m in (fetch_market(x["slug"], x["label"]) for x in MARKETS) if m]
    if len(markets) < len(MARKETS):
        markets += fetch_fallback(len(MARKETS) - len(markets))
    if not markets:
        send_ntfy("Taiwan risk monitor FAILED",
                  "No market data reachable. Check the workflow logs on GitHub.",
                  urgent=True)
        sys.exit(1)

    alerts = check_alerts(markets)
    msg = build_message(markets, alerts)
    date = datetime.now(timezone.utc).strftime("%d %b")
    title = "🔴 TAIWAN RISK ALERT" if alerts else f"Taiwan risk nominal — {date}"
    print(title + "\n" + msg)
    send_ntfy(title, msg, urgent=bool(alerts))
    append_history(markets)


if __name__ == "__main__":
    main()
