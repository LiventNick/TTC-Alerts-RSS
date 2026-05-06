// ---------------------------------------------------------------------------
// In-memory hit counter — batched KV writes to avoid exhausting the free tier.
//
// Cloudflare Workers reuse isolate instances across requests on the same PoP,
// so globalThis persists between requests within a single isolate lifetime.
// We accumulate hits in memory and only flush to KV:
//   • every FLUSH_EVERY hits, OR
//   • every FLUSH_INTERVAL_MS milliseconds
//
// This cuts KV writes by ~98 % vs. the previous per-request get+put approach.
// ---------------------------------------------------------------------------

const COUNTER_KEY       = "feed-hits";
const FLUSH_EVERY       = 50;          // flush after this many in-memory hits
const FLUSH_INTERVAL_MS = 5 * 60_000; // or at least once every 5 minutes

// Shared state across requests in the same isolate
if (!globalThis.__counter) {
  globalThis.__counter = {
    pending:      0,       // hits accumulated since last flush
    base:         null,    // last persisted value (null = not yet read from KV)
    lastFlushAt:  Date.now(),
  };
}

async function getTotal(env) {
  if (globalThis.__counter.base === null) {
    const stored = await env.STATS.get(COUNTER_KEY);
    globalThis.__counter.base = parseInt(stored || "0", 10);
  }
  return globalThis.__counter.base + globalThis.__counter.pending;
}

async function incrementAndMaybeFlush(env) {
  globalThis.__counter.pending += 1;

  const now = Date.now();
  const shouldFlush =
    globalThis.__counter.pending >= FLUSH_EVERY ||
    now - globalThis.__counter.lastFlushAt >= FLUSH_INTERVAL_MS;

  if (shouldFlush) {
    // Compute new total (read base from KV only if we haven't yet)
    const total = await getTotal(env);
    await env.STATS.put(COUNTER_KEY, String(total));

    // Reset in-memory state
    globalThis.__counter.base     = total;
    globalThis.__counter.pending  = 0;
    globalThis.__counter.lastFlushAt = now;
  }
}

// ---------------------------------------------------------------------------

export default {
  async fetch(request, env, ctx) {
    const url = new URL(request.url);
    const API_URL = "https://alerts.ttc.ca/api/alerts/live-alerts";
    const headers = {
      "User-Agent":
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    };

    // ── /stats.json endpoint ──────────────────────────────────────────────
    if (url.pathname === "/stats.json") {
      try {
        const count = await getTotal(env);
        return new Response(
          JSON.stringify({
            schemaVersion: 1,
            label: "worker hits",
            message: count.toLocaleString(),
            color: "orange",
          }),
          { headers: { "Content-Type": "application/json;charset=UTF-8" } }
        );
      } catch {
        return new Response(
          JSON.stringify({
            schemaVersion: 1,
            label: "worker hits",
            message: "unavailable",
            color: "lightgrey",
          }),
          { headers: { "Content-Type": "application/json;charset=UTF-8" } }
        );
      }
    }

    // ── Increment counter in background (non-blocking) ───────────────────
    ctx.waitUntil(
      incrementAndMaybeFlush(env).catch((e) =>
        console.error("Failed to update counter:", e)
      )
    );

    // ── Fetch & serve the RSS feed ────────────────────────────────────────
    try {
      const response = await fetch(API_URL, { headers });
      const data = await response.json();

      const allAlerts = [...(data.routes || []), ...(data.accessibility || [])];

      let rssItems = "";
      for (const alert of allAlerts) {
        let title  = alert.headerText || alert.title || "";
        let custom = alert.customHeaderText || "";
        let desc   = alert.description || "";

        // Fix "WEBSITE" title logic
        if (!title || title.toUpperCase() === "WEBSITE") {
          title = custom || desc;
        }

        // Clean HTML from title
        let cleanTitle = title.replace(/<[^>]*>?/gm, "").trim();

        // Emoji logic
        let emoji = "⚠️";
        const type = String(alert.routeType || "").toLowerCase();
        if (type.includes("subway"))                           emoji = "🚇";
        else if (type.includes("streetcar"))                   emoji = "🚋";
        else if (type.includes("bus"))                         emoji = "🚌";
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
  },
};
