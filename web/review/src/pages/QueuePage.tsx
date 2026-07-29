import { useEffect, useState } from "react";
import { Link } from "react-router";
import { fetchQueueStats, fetchStories, type QueueStats, type Story } from "../api";

export default function QueuePage() {
  const [stats, setStats] = useState<QueueStats | null>(null);
  const [drafted, setDrafted] = useState<Story[]>([]);
  const [approved, setApproved] = useState<Story[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    async function load() {
      try {
        const [statsData, draftedData, approvedData] = await Promise.all([
          fetchQueueStats(),
          fetchStories("drafted"),
          fetchStories("approved"),
        ]);
        if (!cancelled) {
          setStats(statsData);
          setDrafted(draftedData);
          setApproved(approvedData.filter((s) => !s.issue_date));
          setError(null);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load queue");
        }
      } finally {
        if (!cancelled) setLoading(false);
      }
    }
    void load();
    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) return <p className="meta">Loading queue…</p>;
  if (error) {
    return (
      <div className="panel panel-error stack">
        <h1>Cannot reach API</h1>
        <p>{error}</p>
        <p className="meta">
          Start the API with <code>brief review --no-https</code> (matches the Vite
          proxy), or set <code>VITE_API_PROXY</code> if using HTTPS.
        </p>
      </div>
    );
  }

  return (
    <div className="stack">
      <section className="panel stack" aria-labelledby="queue-heading">
        <h1 id="queue-heading">Review queue</h1>
        {stats && <p className="meta">{stats.tagline}</p>}
        {stats && (
          <div className="stat-grid" aria-label="Queue statistics">
            <div className="stat">
              <strong>{stats.candidates}</strong>
              <span>Candidates</span>
            </div>
            <div className="stat">
              <strong>{stats.drafted}</strong>
              <span>Drafted</span>
            </div>
            <div className="stat">
              <strong>{stats.approved}</strong>
              <span>Approved</span>
            </div>
            <div className="stat">
              <strong>{stats.stories_per_issue}</strong>
              <span>Target / issue</span>
            </div>
          </div>
        )}
      </section>

      <section className="panel stack" aria-labelledby="drafted-heading">
        <h2 id="drafted-heading">Drafted stories</h2>
        {drafted.length === 0 ? (
          <p className="meta">
            No drafted stories. Run <code>brief ingest</code> then <code>brief draft</code>.
          </p>
        ) : (
          <ul className="story-cards">
            {drafted.map((story) => (
              <li key={story.id} className="story-card">
                <ul className="meta-list" aria-label="Story details">
                  <li>{story.source_name}</li>
                  <li>{story.category}</li>
                  <li>
                    <span className="badge badge-score">
                      APAC {story.apac_score.toFixed(2)}
                    </span>
                  </li>
                </ul>
                <h3>
                  <Link to={`/story/${story.id}`}>{story.title}</Link>
                </h3>
                <p>{story.summary}</p>
                {story.why_it_matters && (
                  <p className="why">{story.why_it_matters}</p>
                )}
              </li>
            ))}
          </ul>
        )}
      </section>

      <section className="panel stack" aria-labelledby="approved-heading">
        <h2 id="approved-heading">Approved for next issue</h2>
        {approved.length === 0 ? (
          <p className="meta">None yet</p>
        ) : (
          <ul className="meta-list">
            {approved.map((story) => (
              <li key={story.id}>
                {story.title}{" "}
                <span className="meta">({story.apac_score.toFixed(2)})</span>
              </li>
            ))}
          </ul>
        )}
      </section>
    </div>
  );
}
