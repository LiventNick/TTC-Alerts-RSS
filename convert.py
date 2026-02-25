import requests
import json
from datetime import datetime

# TTC API URL
API_URL = "https://alerts.ttc.ca/api/alerts/live-alerts"
# Output file
OUTPUT_FILE = "ttc_feed.xml"

def create_rss():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()
        data = response.json()
        
        rss_items = ""
        routes = data.get('routes') if data.get('routes') is not None else []
        access = data.get('accessibility') if data.get('accessibility') is not None else []
        all_alerts = routes + access

        for alert in all_alerts:
            # 1. Get initial title and description
            title = alert.get('headerText') or alert.get('title') or ""
            desc = alert.get('description') or ""
            
            # 2. Fix the "WEBSITE" title issue
            if title.upper() == "WEBSITE":
                # Use the first 50 characters of description as a title instead
                title = f"Station Alert: {desc[:60]}..." if desc else "General Station Alert"

            # 3. Choose Emoji based on routeType or Alert content
            emoji = "⚠️" # Default
            r_type = str(alert.get('routeType', '')).lower()
            
            if "subway" in r_type: emoji = "🚇"
            elif "streetcar" in r_type: emoji = "🚋"
            elif "bus" in r_type: emoji = "🚌"
            elif "elevator" in r_type or "escalator" in r_type: emoji = "♿"
            
            # Special check for "Slower than usual" (Reduced Speed Zones)
            if "slower than usual" in title.lower():
                emoji = "🐢"

            full_title = f"{emoji} {title}"
            
            # 4. Finalize description logic
            # If description is empty or just the title again, provide context
            final_desc = desc if desc and len(desc) > 5 else title
                
            link = "https://www.ttc.ca/service-alerts"
            guid = str(alert.get('id'))
            pub_date = alert.get('lastUpdated')

            rss_items += f"""
        <item>
            <title><![CDATA[{full_title}]]></title>
            <description><![CDATA[{final_desc}]]></description>
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
        raise e

if __name__ == "__main__":
    create_rss()
