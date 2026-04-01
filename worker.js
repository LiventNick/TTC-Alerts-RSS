export default {
  async fetch(request, env, ctx) {
    const COUNTER_NAMESPACE = "liventnick-ttc-alerts";
    const COUNTER_KEY = "worker-feed-hits";
    const url = new URL(request.url);
    const API_URL = "https://alerts.ttc.ca/api/alerts/live-alerts";
    const headers = { 
      "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36" 
    };

    if (url.pathname === "/stats.json") {
      try {
        const statsRes = await fetch(`https://api.countapi.xyz/get/${COUNTER_NAMESPACE}/${COUNTER_KEY}`);
        const stats = await statsRes.json();
        const count = typeof stats.value === "number" ? stats.value : 0;

        return new Response(
          JSON.stringify({
            schemaVersion: 1,
            label: "worker hits",
            message: count.toLocaleString(),
            color: "orange"
          }),
          { headers: { "Content-Type": "application/json;charset=UTF-8" } }
        );
      } catch {
        return new Response(
          JSON.stringify({
            schemaVersion: 1,
            label: "worker hits",
            message: "unavailable",
            color: "lightgrey"
          }),
          { headers: { "Content-Type": "application/json;charset=UTF-8" } }
        );
      }
    }

    // Count feed requests without blocking the feed response path.
    ctx.waitUntil(fetch(`https://api.countapi.xyz/hit/${COUNTER_NAMESPACE}/${COUNTER_KEY}`).catch(() => {}));

    try {
      const response = await fetch(API_URL, { headers });
      const data = await response.json();
      
      const allAlerts = [...(data.routes || []), ...(data.accessibility || [])];

      let rssItems = "";
      for (const alert of allAlerts) {
        let title = alert.headerText || alert.title || "";
        let custom = alert.customHeaderText || "";
        let desc = alert.description || "";

        // Fix "WEBSITE" title logic
        if (!title || title.toUpperCase() === "WEBSITE") {
          title = custom || desc;
        }

        // Clean HTML from title
        let cleanTitle = title.replace(/<[^>]*>?/gm, '').trim();

        // Emoji Logic
        let emoji = "⚠️";
        const type = String(alert.routeType || "").toLowerCase();
        if (type.includes("subway")) emoji = "🚇";
        else if (type.includes("streetcar")) emoji = "🚋";
        else if (type.includes("bus")) emoji = "🚌";
        else if (type.includes("elevator") || type.includes("escalator")) emoji = "♿";
        if (cleanTitle.toLowerCase().includes("slower than usual")) emoji = "🐢";

        rssItems += `
        <item>
          <title><![CDATA[${emoji} ${cleanTitle}]]></title>
          <description><![CDATA[${desc || cleanTitle}]]></description>
          <link>https://www.ttc.ca/service-alerts</link>
          <guid isPermaLink="false">${alert.id}</guid>
          <pubDate>${alert.lastUpdated}</pubDate>
        </item>`;
      }

      const rssFeed = `<?xml version="1.0" encoding="UTF-8" ?>
<rss version="2.0">
  <channel>
    <title>TTC Service Alerts (Live)</title>
    <link>https://www.ttc.ca/service-alerts</link>
    <description>Live real-time feed for TTC Alerts via Cloudflare Workers</description>
    <lastBuildDate>${new Date().toUTCString()}</lastBuildDate>
    ${rssItems}
  </channel>
</rss>`;

      return new Response(rssFeed, {
        headers: { "Content-Type": "application/rss+xml;charset=UTF-8" },
      });
    } catch (e) {
      return new Response(`Error: ${e.message}`, { status: 500 });
    }
  }
};
