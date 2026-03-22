import os
import requests
import feedparser

print("--- Testing EIA API ---")
# Manually paste your key here just for testing
TEST_KEY = "s8qAje5U2kyrNO3uyypyFMT8PIlYzD1ghv1742WN" 

url = f"https://api.eia.gov/v2/petroleum/stoc/wstk/data/?api_key={TEST_KEY}&frequency=weekly&data[0]=value&facets[series][]=WCSSTUS1&sort[0][column]=period&sort[0][direction]=desc&offset=0&length=1"

try:
    res = requests.get(url, timeout=30)
    print(f"Status Code: {res.status_code}")
    if res.status_code == 200:
        data = res.json().get("response", {}).get("data", [])
        if data:
            print(f"Success! Latest Value: {data[0]['value']}")
        else:
            print("API connected, but returned empty data. The series ID might be wrong.")
    else:
        print(f"API Error: {res.text}")
except Exception as e:
    print(f"Connection Error: {e}")

print("\n--- Testing Google News RSS ---")
try:
    feed = feedparser.parse("https://news.google.com/rss/search?q=oil+supply+shortage+OPEC+embargo+SPR+release+when:1d&hl=en-US&gl=US&ceid=US:en")
    if feed.entries:
        print(f"Success! Top Headline: {feed.entries[0].title}")
    else:
        print("Failed to pull headlines. Google News might be blocking the request or the search returned no results.")
except Exception as e:
    print(f"RSS Error: {e}")