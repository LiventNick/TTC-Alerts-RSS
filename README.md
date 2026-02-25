# 🚇 TTC Service Alerts RSS Bridge

This project converts the official TTC (Toronto Transit Commission) JSON alerts into a clean, emoji-fied RSS feed. 

![Update Status](https://github.com/LiventNick/TTC-Alerts-RSS/actions/workflows/update_feed.yml/badge.svg)

## 📡 Live Feed URLs
- **Primary (GitHub Pages):** [https://liventnick.github.io/TTC-Alerts-RSS/ttc_feed.xml](https://liventnick.github.io/TTC-Alerts-RSS/ttc_feed.xml)
- **Failback (Cloudflare Worker):** COMING SOON

## ✨ Features
- **Auto-Updating:** Updates every 10 minutes via GitHub Actions.
- **Smart Titles:** Automatically replaces generic "WEBSITE" headers with descriptive text.
- **Emoji Support:**
  - 🚇 Subway
  - 🚌 Bus
  - 🚋 Streetcar
  - 🐢 Slow Zones (Reduced Speed)
  - ⚠️ General Alerts

## 🛠️ How it Works
1. A Python script (`convert.py`) fetches data from the TTC Live Alerts API.
2. It parses the JSON and formats it into a valid RSS 2.0 XML file.
3. GitHub Actions runs the script on a schedule and pushes the updated `ttc_feed.xml` to this repository.
4. GitHub Pages hosts the XML file as a static RSS feed.

## 🤝 Contributing
Feel free to fork this repo or open an issue if you have suggestions for better emoji mapping or filtering!
