import requests
import json
from datetime import datetime

# TTC API URL
API_URL = "https://alerts.ttc.ca/api/alerts/live-alerts"
# Output file
OUTPUT_FILE = "ttc_feed.xml"

def create_rss():
    try:
        response = requests.get(API_URL)
        data = response.json()
        
        rss_items = ""
        # Combine routes and accessibility alerts
        all_alerts = data.get('routes', []) + data.get('accessibility', [])

        for alert in all_alerts:
            title = alert.get('headerText') or alert.get('title')
            desc = alert.get('description') or "No detailed description available."
            link = "https://www.ttc.ca/service-alerts"
            guid = alert.get('id')
            pub_date = alert.get('lastUpdated')

            rss_items += f"""
        <item>
            <title><![CDATA[{title}]]></title>
            <description><![CDATA[{desc}]]></description>
            <link>{link}</link>
            <guid isPermaLink="false">{guid}</guid>
            <pubDate>{pub_date}</pubDate>
        </item>"""

        rss_feed = f"""<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
    <channel>
        <title>TTC Service Alerts</title>
        <link>https://www.ttc.ca/service-alerts</link>
        <description>Live service alerts for the Toronto Transit Commission</description>
        <lastBuildDate>{datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')}</lastBuildDate>
        {rss_items}
    </channel>
</rss>"""

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            f.write(rss_feed)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    create_rss()
