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
            # 1. Grab potential title sources in order of "cleanliness"
            # customHeaderText is usually the best for 'WEBSITE' style alerts
            api_title = alert.get('headerText') or alert.get('title') or ""
            api_custom = alert.get('customHeaderText') or ""
            api_desc = alert.get('description') or ""
            
            # 2. Logic to fix "WEBSITE" or missing titles
            if not api_title or api_title.upper() == "WEBSITE":
                # Use customHeaderText if available, otherwise take the description
                title = api_custom if api_custom else api_desc
            else:
                title = api_title

            # 3. Strip any HTML tags from the title (like <a> links)
            import re
            title = re.sub('<[^<]+?>', '', title).strip()
            
            # 4. Emoji Logic
            emoji = "⚠️"
            r_type = str(alert.get('routeType', '')).lower()
            
            if "subway" in r_type: emoji = "🚇"
            elif "streetcar" in r_type: emoji = "🚋"
            elif "bus" in r_type: emoji = "🚌"
            elif "elevator" in r_type or "escalator" in r_type: emoji = "♿"
            
            if "slower than usual" in title.lower():
                emoji = "🐢"

            full_title = f"{emoji} {title}"
            
            # 5. Description Logic (Keeping the HTML links here is fine)
            final_desc = api_desc if api_desc else title
                
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
