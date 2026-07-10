import Link from "next/link";
import SiteShell from "@/components/SiteShell";
import { listPublicIssues } from "@/lib/issues";

export default function IssuesArchivePage() {
  const issues = listPublicIssues(true);

  return (
    <SiteShell currentPath="/issues">
      <section className="panel stack" aria-labelledby="archive-heading">
        <header className="stack">
          <h1 id="archive-heading" className="h1">
            Issue archive
          </h1>
          <p className="meta">Published briefings and the sample preview issue.</p>
        </header>

        {issues.length > 0 ? (
          <div role="list" aria-label="All issues">
            {issues.map((item, index) => (
              <article
                key={item.date}
                className="issue-row"
                role="listitem"
                aria-labelledby={`issue-${index + 1}-title`}
              >
                <div className="stack">
                  {item.is_sample ? (
                    <>
                      <p>
                        <span className="badge badge-sample">Sample</span>
                      </p>
                      <h2 id={`issue-${index + 1}-title`} className="h2">
                        Preview issue
                      </h2>
                      <p className="meta">Placeholder stories showing the intended format</p>
                    </>
                  ) : (
                    <>
                      <p>
                        <span className="badge badge-live">Published</span>
                      </p>
                      <h2 id={`issue-${index + 1}-title`} className="h2">
                        {item.date}
                      </h2>
                      <ul className="meta-list" aria-label="Issue details">
                        <li>{item.story_count} stories</li>
                        <li>APAC relevance {Math.round(item.apac_ratio * 100)}%</li>
                      </ul>
                    </>
                  )}
                </div>
                <div className="actions">
                  <Link
                    className="button button-secondary"
                    href={`/issues/${item.date}`}
                    aria-label={`Read ${item.is_sample ? "sample preview" : `issue ${item.date}`}`}
                  >
                    Read issue
                  </Link>
                </div>
              </article>
            ))}
          </div>
        ) : (
          <p>
            No issues published yet. <Link href="/issues/sample">View the sample preview</Link>.
          </p>
        )}
      </section>
    </SiteShell>
  );
}
