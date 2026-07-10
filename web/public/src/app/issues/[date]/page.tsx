import Link from "next/link";
import { notFound } from "next/navigation";
import SiteShell from "@/components/SiteShell";
import { getCategoryLabels, getEditionInfo } from "@/lib/edition";
import { getPublicIssue, listPublicIssues } from "@/lib/issues";

interface IssuePageProps {
  params: Promise<{ date: string }>;
}

export default async function IssuePage({ params }: IssuePageProps) {
  const { date } = await params;
  const issue = getPublicIssue(date);
  if (!issue) notFound();

  const edition = getEditionInfo();
  const categories = getCategoryLabels();
  const allIssues = listPublicIssues(true);

  return (
    <SiteShell currentPath="/issues">
      <header className="panel stack issue-header">
        {issue.is_sample ? (
          <p>
            <span className="badge badge-sample">Sample issue — placeholder content</span>
          </p>
        ) : (
          <p>
            <span className="badge badge-live">Published</span>
          </p>
        )}

        <h1 className="h1">
          {issue.is_sample ? "What Brief APAC looks like" : edition.tagline}
        </h1>

        <ul className="meta-list" aria-label="Issue details">
          <li>{issue.is_sample ? "Preview" : issue.date}</li>
          <li>{issue.stories.length} stories</li>
          <li>APAC relevance {Math.round(issue.apac_ratio * 100)}%</li>
        </ul>

        <p>{issue.intro}</p>
      </header>

      <div className="grid grid-sidebar">
        <section className="panel" aria-labelledby="stories-heading">
          <h2 id="stories-heading" className="sr-only">
            Stories in this issue
          </h2>
          <ol className="story-list">
            {issue.stories.map((story, index) => (
              <li key={story.url} className="story">
                <article aria-labelledby={`issue-story-${index + 1}-title`}>
                  <ul className="meta-list" aria-label="Story details">
                    <li>{categories[story.category] ?? story.category}</li>
                    <li>{story.source_name}</li>
                    <li>{story.read_time_minutes} min read</li>
                  </ul>

                  <h3 id={`issue-story-${index + 1}-title`} className="h2">
                    {issue.is_sample ? (
                      story.title
                    ) : (
                      <a
                        href={story.url}
                        className="external-link"
                        rel="noopener noreferrer"
                      >
                        {story.title}
                        <span className="sr-only">(opens in new tab)</span>
                      </a>
                    )}
                  </h3>

                  <p>{story.summary}</p>
                  <p className="why">
                    <strong>Why it matters:</strong> {story.why_it_matters}
                  </p>

                  {!issue.is_sample && (
                    <p>
                      <a
                        href={story.url}
                        className="external-link"
                        rel="noopener noreferrer"
                      >
                        Read original article
                        <span className="sr-only">(opens in new tab)</span>
                      </a>
                    </p>
                  )}
                </article>
              </li>
            ))}
          </ol>
        </section>

        <aside className="stack" aria-label="Issue navigation">
          <section className="panel">
            <h2 className="h2">More issues</h2>
            <nav aria-label="Issue archive">
              <ul className="sidebar-list">
                {allIssues.map((item) => (
                  <li key={item.date}>
                    <Link
                      href={`/issues/${item.date}`}
                      aria-current={item.date === issue.date ? "page" : undefined}
                    >
                      {item.is_sample ? "Sample preview" : item.date}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          </section>

          {issue.is_sample && (
            <section className="panel notice" role="note" aria-label="Sample content notice">
              <p className="meta">
                These are placeholder stories for design and workflow testing. Real issues
                will link to source articles once publishing begins.
              </p>
            </section>
          )}
        </aside>
      </div>
    </SiteShell>
  );
}
