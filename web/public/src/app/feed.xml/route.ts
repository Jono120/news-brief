import { getSiteInfo } from "@/lib/edition";
import { getPublicIssue, listPublicIssues } from "@/lib/issues";

function escapeXml(value: string): string {
  return value
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&apos;");
}

export async function GET(request: Request) {
  const site = getSiteInfo();
  const baseUrl = new URL(request.url).origin;
  const items = listPublicIssues(true)
    .map((summary) => getPublicIssue(summary.date))
    .filter((issue): issue is NonNullable<typeof issue> => issue !== null);

  const channelItems = items
    .map((issue) => {
      const title = issue.is_sample ? "Sample issue" : `Issue ${issue.date}`;
      const link = `${baseUrl}/issues/${issue.date}`;
      return `
    <item>
      <title>${escapeXml(title)}</title>
      <link>${escapeXml(link)}</link>
      <guid isPermaLink="true">${escapeXml(link)}</guid>
      <description>${escapeXml(issue.intro)}</description>
    </item>`;
    })
    .join("");

  const body = `<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>${escapeXml(site.title)}</title>
    <link>${escapeXml(baseUrl)}</link>
    <description>${escapeXml(site.description)}</description>
    ${channelItems}
  </channel>
</rss>`;

  return new Response(body, {
    headers: { "Content-Type": "application/rss+xml; charset=utf-8" },
  });
}
