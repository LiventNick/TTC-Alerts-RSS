# 🚇 TTC Service Alerts RSS Bridge

This project converts the official TTC (Toronto Transit Commission) JSON alerts into a clean, emoji-fied RSS feed served in real time by a Cloudflare Worker.

![Cloudflare Status](https://img.shields.io/github/deployments/LiventNick/TTC-Alerts-RSS/production?label=Cloudflare%20Worker&logo=cloudflare)
![Worker Hits](https://img.shields.io/endpoint?url=https%3A%2F%2Fttc-alerts-rss.liventnick.xyz%2Fstats.json)

## 📡 Feeds
- **Live (Real-time):** [https://ttc-alerts-rss.liventnick.xyz](https://ttc-alerts-rss.liventnick.xyz)

## ⚠️ GitHub Pages Feed Retired
The old GitHub Pages feed has been retired in favor of the Cloudflare Worker feed above.

Reason: GitHub never reliably updated every 10 minutes as intended, while the Cloudflare Worker provides more accurate and up-to-date alerts.

If you previously subscribed to the GitHub Pages URL, please switch to:

**https://ttc-alerts-rss.liventnick.xyz**

The legacy `ttc_feed.xml` path now serves a feed-moved notice so existing subscribers can discover the new URL.

## 🧰 Self-Hosting
`convert.py` remains in this repo for anyone who wants to generate and host their own RSS endpoint.

## ✨ Features
- **Real-Time Delivery:** Served directly from the live TTC alerts API through Cloudflare Workers.
- **Smart Titles:** Automatically replaces generic "WEBSITE" headers with descriptive text.
- **Emoji Support:**
  - 🚇 Subway
  - 🚌 Bus
  - 🚋 Streetcar
  - 🐢 Slow Zones (Reduced Speed)
  - ⚠️ General Alerts

## 🛠️ How it Works
1. A Cloudflare Worker fetches data from the TTC Live Alerts API on each request.
2. It parses the JSON and formats it into a valid RSS 2.0 XML response.
3. Subscribers always get fresh alerts from the live endpoint.

## 🤝 Contributing
Feel free to fork this repo or open an issue if you have suggestions for better emoji mapping or filtering!
