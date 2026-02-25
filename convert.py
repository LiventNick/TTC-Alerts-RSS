import requests
import json
from datetime import datetime

# TTC API URL
API_URL = "https://alerts.ttc.ca/api/alerts/live-alerts"
# Output file
OUTPUT_FILE = "ttc_feed.xml"

def create_rss():
    # Adding a User-Agent makes us look like a real browser
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status() # This will stop the script if the API blocks us
        data = response.json()
        
        rss_items = ""
        # Combine routes and accessibility alerts
        # We use .get([],) to ensure it doesn't crash if one list is missing
        routes = data.get('routes') if data.get('routes') is not None else []
        access = data.get('accessibility') if data.get('accessibility') is not None else []
        all_alerts = routes + access

        for alert in all_alerts:
            title = alert.get('headerText') or alert.get('title') or "TTC Alert"
            desc = alert.get('description') or "View details on the TTC website."
            # Clean up the description if it's empty but headerText has info
            if desc == "" and title:
                desc = title
                
            link = "https://www.ttc.ca/service-alerts"
            guid = str(alert.get('id'))
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
        print("Successfully created ttc_feed.xml")
            
    except Exception as e:
        print(f"Error occurred: {e}")
        # Re-raise the error so the GitHub Action knows it failed
        raise e

if __name__ == "__main__":
    create_rss()
