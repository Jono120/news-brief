import { FormEvent, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router";
import {
  approveStory,
  fetchStory,
  rejectStory,
  saveStory,
  type Story,
} from "../api";

export default function StoryPage() {
  const { id } = useParams();
  const storyId = Number(id);
  const navigate = useNavigate();
  const [story, setStory] = useState<Story | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!Number.isFinite(storyId)) return;
    let cancelled = false;
    fetchStory(storyId)
      .then((data) => {
        if (!cancelled) setStory(data);
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Story not found");
        }
      });
    return () => {
      cancelled = true;
    };
  }, [storyId]);

  async function onSave(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!story) return;
    const form = new FormData(event.currentTarget);
    setSaving(true);
    try {
      const updated = await saveStory(story.id, {
        summary: String(form.get("summary") ?? ""),
        why_it_matters: String(form.get("why_it_matters") ?? ""),
        category: String(form.get("category") ?? ""),
        read_time_minutes: Number(form.get("read_time_minutes") ?? 3),
      });
      setStory(updated);
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function onApprove() {
    if (!story) return;
    await approveStory(story.id);
    navigate("/");
  }

  async function onReject() {
    if (!story) return;
    await rejectStory(story.id);
    navigate("/");
  }

  if (error) {
    return (
      <div className="panel panel-error stack">
        <p>{error}</p>
        <Link to="/">← Back to queue</Link>
      </div>
    );
  }

  if (!story) return <p className="meta">Loading story…</p>;

  return (
    <div className="stack">
      <p>
        <Link to="/">← Back to queue</Link>
      </p>
      <article className="panel stack" aria-labelledby="story-title">
        <ul className="meta-list" aria-label="Story details">
          <li>{story.source_name}</li>
          <li>{story.category}</li>
          <li>
            <span className="badge badge-score">
              APAC {story.apac_score.toFixed(2)}
            </span>
          </li>
        </ul>
        <h1 id="story-title">{story.title}</h1>
        <p>
          <a href={story.url} target="_blank" rel="noopener noreferrer">
            Original article
          </a>
        </p>

        <form className="stack" onSubmit={onSave}>
          <label className="field">
            Summary
            <textarea name="summary" rows={4} defaultValue={story.summary} />
          </label>
          <label className="field">
            Why it matters (APAC)
            <textarea
              name="why_it_matters"
              rows={3}
              defaultValue={story.why_it_matters}
            />
          </label>
          <label className="field">
            Category
            <input type="text" name="category" defaultValue={story.category} />
          </label>
          <label className="field">
            Read time (minutes)
            <input
              type="number"
              name="read_time_minutes"
              min={1}
              defaultValue={story.read_time_minutes}
            />
          </label>
          <div className="actions">
            <button type="submit" className="button button-neutral" disabled={saving}>
              {saving ? "Saving…" : "Save edits"}
            </button>
          </div>
        </form>

        <div className="actions">
          <button
            type="button"
            className="button button-success"
            onClick={() => void onApprove()}
          >
            Approve for issue
          </button>
          <button
            type="button"
            className="button button-danger"
            onClick={() => void onReject()}
          >
            Reject
          </button>
        </div>
      </article>
    </div>
  );
}
