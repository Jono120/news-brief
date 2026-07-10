import Link from "next/link";
import SiteShell from "@/components/SiteShell";
import { getCategoryLabels } from "@/lib/edition";
import { getFeaturedIssue, listPublicIssues } from "@/lib/issues";

export default function HomePage() {
  const featured = getFeaturedIssue();
  const recent = listPublicIssues(true).slice(0, 6);
  const categories = getCategoryLabels();

  return (
    <SiteShell currentPath="/">
      <section className="panel stack" aria-labelledby="featured-issue-heading">
        <div className="stack">
          {featured.is_sample ? (
            <p>
              <span className="badge badge-sample">Sample issue</span>
            </p>
          ) : (
            <p>
              <span className="badge badge-live">Latest issue</span>
            </p>
          )}

          <h1 id="featured-issue-heading" className="h1">
            {featured.is_sample ? "Preview the briefing" : `Issue for ${featured.date}`}
          </h1>

          <p>{featured.intro}</p>

          <ul className="meta-list" aria-label="Issue details">
            <li>{featured.stories.length} stories</li>
            <li>APAC relevance {Math.round(featured.apac_ratio * 100)}%</li>
          </ul>

          <div className="actions">
            <Link className="button button-primary" href={`/issues/${featured.date}`}>
              Read full issue
            </Link>
          </div>
        </div>
      </section>

      <div className="grid grid-sidebar">
        <section className="panel" aria-labelledby="top-stories-heading">
          <h2 id="top-stories-heading" className="h2">
            Top stories
          </h2>
          <ol className="story-list">
            {featured.stories.slice(0, 4).map((story, index) => (
              <li key={story.url} className="story-preview">
                <article aria-labelledby={`story-${index + 1}-title`}>
                  <ul className="meta-list" aria-label="Story details">
                    <li>{categories[story.category] ?? story.category}</li>
                    <li>{story.read_time_minutes} min read</li>
                  </ul>
                  <h3 id={`story-${index + 1}-title`} className="h3">
                    {story.title}
                  </h3>
                  <p>{story.summary}</p>
                </article>
              </li>
            ))}
          </ol>
        </section>

        <aside className="stack" aria-label="Sidebar">
          <section className="panel" aria-labelledby="recent-issues-heading">
            <h2 id="recent-issues-heading" className="h2">
              Recent issues
            </h2>
            <ul className="issue-list">
              {recent.map((item) => (
                <li key={item.date}>
                  <Link href={`/issues/${item.date}`}>
                    <span>
                      {item.is_sample ? "Sample preview" : item.date}
                    </span>
                    <span className="meta">{item.story_count} stories</span>
                  </Link>
                </li>
              ))}
            </ul>
            <div className="actions">
              <Link className="button button-secondary" href="/issues">
                View archive
              </Link>
            </div>
          </section>

          <section className="panel subscribe-box" aria-labelledby="subscribe-heading">
            <h2 id="subscribe-heading" className="h2">
              Get the weekday email
            </h2>
            <p className="meta">Free APAC tech briefing in your inbox. Launching soon.</p>
            <form className="subscribe-form" action="#" method="post" aria-describedby="subscribe-note">
              <label htmlFor="subscribe-email">Email address</label>
              <input
                id="subscribe-email"
                name="email"
                type="email"
                autoComplete="email"
                placeholder="you@company.com"
                disabled
                aria-disabled="true"
              />
              <button
                type="submit"
                className="button button-secondary is-disabled"
                disabled
                aria-disabled="true"
              >
                Subscribe — coming soon
              </button>
              <p id="subscribe-note" className="meta">
                Email signup is not active in this preview yet.
              </p>
            </form>
          </section>
        </aside>
      </div>
    </SiteShell>
  );
}
