# Pragmatic Assessment: GSN / Taiwan Strait Tracker & WhatsMyPolitics

*July 2026 — based on your repo, GA snapshots (17 Jun – 14 Jul), and current market scan.*

## The short answer

Neither project is on a credible path to $500–1k/mo at a few hours a week. GSN should be shut down. WhatsMyPolitics has a faint pulse and one plausible (cheap) experiment left before you kill it too. Neither solves a problem people will pay you for in your position.

## What the data says

**GSN / Taiwan Tracker: 9 active users in 28 days.** That is functionally zero. 116 auto-generated daily reports, 18 AI articles, daily posts to X/Bluesky with no followers — the machine runs perfectly and produces nothing, because it automates content supply when the scarce resource is attention.

**WhatsMyPolitics: 176 "active users" in 28 days, and it's worse than it looks.** Top cities include Singapore (19), Ashburn, Boardman, Council Bluffs, Prineville — AWS, Google and Meta data-centre towns. A meaningful chunk of your 103 "direct" users are bots and crawlers. Real humans are maybe 80–120/month.

The genuinely damning number: **1 Google organic user in a month**, against 30 from Bing and 14 from Ecosia. Google has effectively declined to rank the site. The ~70 AI guides produced 0–10 views each. The SEO-article strategy hasn't underperformed — it has failed outright, and it won't recover: Google is actively suppressing scaled AI content, and AI answers are eating informational search traffic anyway. More articles = more of zero.

The one positive signal: people who do arrive engage. ~3.4 min average engagement, 29% bounce on the test page. The AI questionnaire itself works as a product experience.

## Is there a genuine problem here?

**GSN: the problem is real, but you can't be the one paid to solve it.** Geopolitical risk monitoring has paying customers — funds and corporates — but they're buying analyst credibility and accountability ([Taiwan Risk](https://taiwanrisk.com/) sells exactly this as a B2B newsletter). What they will not buy is an anonymous automated dashboard synthesising public RSS feeds and yfinance data through Gemini. The free end is already served by [MacroMicro](https://en.macromicro.me/charts/55605/taiwan-strait-geopolitical-risk-index), [BlackRock's dashboard](https://www.blackrock.com/corporate/insights/blackrock-investment-institute/interactive-charts/geopolitical-risk-dashboard), and prediction-market aggregators like [Taiwan Tracker](https://taiwantracker.org/). The pivot from a focused Taiwan tracker to a generic "macro intelligence network" made this worse — it diluted the one specific thing the site was about.

**WMP: real itch, abundantly scratched for free.** "What are my politics?" is a genuine recurring curiosity, but [Political Compass](https://www.politicalcompass.org/test), [8values](https://8values.github.io/), [PolitiScales](https://politiscales.party/) and [iSideWith](https://politicaldna.org/best-political-quizzes/) own it with years of backlinks and meme-culture distribution. Your AI-conversation angle is a real differentiator in product terms — but it's a nice-to-have, not a painkiller, and it's trivially copyable.

## The monetisation math

$500/mo from display ads needs roughly 30–50k pageviews/month at quiz-content RPMs. WMP does ~400. That's a ~100x gap with no working acquisition channel. GSN's gap is unmeasurable. There is no subscription story for either at current trust/audience levels. A Buy Me a Coffee button on a site with 100 humans/month is a rounding error.

## Recommendations

**1. Kill GSN now.** Disable the cron job, stop the social broadcasts, let the domain lapse at renewal. Keep the repo public as a portfolio piece — a self-updating multi-source intelligence pipeline with LLM synthesis and multi-platform broadcast is legitimately impressive engineering to show. Its value is the résumé, not the audience.

**2. Give WMP one 90-day experiment, then decide.** The only channel that has ever worked for political quizzes is social sharing, not SEO. Quiz results are inherently shareable — that's how Political Compass and 8values spread. The experiment: make the result a beautiful, shareable card (image with your URL on it), add one-tap sharing, and seed it yourself in places quizzes spread (relevant subreddits, TikTok/shorts of "the AI guessed my politics"). Cost: your time plus ~$0. Stop writing articles entirely. Kill criterion: if shared-result referrals aren't visibly growing traffic by mid-October, shut it down without guilt.

**3. Don't add money.** Keep the $100 in your pocket. Neither project has a bottleneck that money fixes — the bottleneck is distribution, and paid acquisition into a free quiz with ad monetisation is negative-margin arithmetic.

## The transferable lesson

Both projects failed the same way: fully automated content supply pointed at channels where you had zero distribution. AI made publishing free, which made published content worthless as an acquisition strategy. Whatever you build next, invert it — find where attention already exists and make one thing people pull toward them, rather than pushing automated output into the void. The engineering skill on display here (the GSN pipeline especially) is worth more applied to someone else's distribution than to your own empty channels.

## Would I stop pursuing this altogether?

In their current form, yes. As a $500–1k/mo goal at a few hours a week, geopolitics dashboards and political quizzes are among the hardest possible categories — free-content expectations, entrenched incumbents, low ad RPMs, and trust-based paid tiers you can't access anonymously. Stopping isn't the hobby failing; the hobby did its job — it taught you to build automated pipelines end to end. That's the asset. Take it somewhere with a customer.
