from __future__ import annotations

from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse

from brief.models import StoryStatus, get_story, list_stories, load_edition_config, update_story
from brief.server import add_server_middleware


def page_shell(title: str, body: str) -> str:
    return f"""<!doctype html>
<html lang=\"en-NZ\">
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>{title}</title>
  <style>
    :root {{
      font-family: Georgia, 'Times New Roman', serif;
      color: #1a1a1a;
      background: #f6f3ee;
    }}
    body {{ max-width: 920px; margin: 0 auto; padding: 24px; }}
    h1, h2 {{ font-family: ui-sans-serif, system-ui, sans-serif; }}
    .card {{
      background: white;
      border: 1px solid #ddd5c8;
      border-radius: 12px;
      padding: 16px 18px;
      margin: 14px 0;
      box-shadow: 0 1px 2px rgba(0,0,0,.04);
    }}
    .meta {{ color: #5c5c5c; font-size: 0.92rem; }}
    .score {{ display: inline-block; padding: 2px 8px; border-radius: 999px; background: #e8f1ea; }}
    textarea, input[type=text] {{ width: 100%; font: inherit; padding: 8px; }}
    .actions {{ display: flex; gap: 8px; flex-wrap: wrap; margin-top: 10px; }}
    button {{
      border: 0; border-radius: 8px; padding: 8px 12px; cursor: pointer;
      font: 600 0.92rem ui-sans-serif, system-ui, sans-serif;
    }}
    .approve {{ background: #1f6b3a; color: white; }}
    .reject {{ background: #8b1e1e; color: white; }}
    .save {{ background: #334155; color: white; }}
    .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 10px; }}
    .stat {{ background: #efe8dc; padding: 12px; border-radius: 10px; }}
  </style>
</head>
<body>
{body}
</body>
</html>"""


def create_review_app(*, require_https: bool = False) -> FastAPI:
    app = FastAPI(title="Brief APAC Review")

    @app.get("/", response_class=HTMLResponse)
    def review_home() -> str:
        edition = load_edition_config()["edition"]
        drafted = list_stories(StoryStatus.DRAFTED, limit=100)
        approved = list_stories(StoryStatus.APPROVED, limit=100)
        candidates = list_stories(StoryStatus.CANDIDATE, limit=20)

        cards = []
        for story in drafted:
            cards.append(
                f"""
                <div class=\"card\">
                  <div class=\"meta\">{story.source_name} · {story.category} · <span class=\"score\">APAC {story.apac_score:.2f}</span></div>
                  <h2><a href=\"/story/{story.id}\">{story.title}</a></h2>
                  <p>{story.summary}</p>
                  <p><em>{story.why_it_matters}</em></p>
                </div>
                """
            )

        body = f"""
        <h1>Brief APAC — review queue</h1>
        <p>{edition['tagline']}</p>
        <div class=\"stats\">
          <div class=\"stat\"><strong>{len(candidates)}</strong><br/>Candidates</div>
          <div class=\"stat\"><strong>{len(drafted)}</strong><br/>Drafted</div>
          <div class=\"stat\"><strong>{len(approved)}</strong><br/>Approved</div>
          <div class=\"stat\"><strong>{edition['stories_per_issue']}</strong><br/>Target / issue</div>
        </div>
        <h2>Drafted stories</h2>
        {''.join(cards) if cards else '<p>No drafted stories. Run <code>brief ingest</code> then <code>brief draft</code>.</p>'}
        <h2>Approved for next issue</h2>
      """
        approved_cards = []
        for story in approved:
            if story.issue_date:
                continue
            approved_cards.append(f"<li>{story.title} <span class=\"meta\">({story.apac_score:.2f})</span></li>")
        body += "<ul>" + ("".join(approved_cards) or "<li>None yet</li>") + "</ul>"
        return page_shell("Brief APAC Review", body)

    @app.get("/story/{story_id}", response_class=HTMLResponse)
    def review_story(story_id: int) -> HTMLResponse:
        story = get_story(story_id)
        if not story:
            return HTMLResponse("Story not found", status_code=404)

        body = f"""
        <p><a href=\"/\">← Back to queue</a></p>
        <div class=\"card\">
          <div class=\"meta\">{story.source_name} · {story.category} · APAC score {story.apac_score:.2f}</div>
          <h1>{story.title}</h1>
          <p><a href=\"{story.url}\" target=\"_blank\" rel=\"noopener\">Original article</a></p>
          <form method=\"post\" action=\"/story/{story.id}/save\">
            <label>Summary<br/><textarea name=\"summary\" rows=\"4\">{story.summary}</textarea></label><br/><br/>
            <label>Why it matters (APAC)<br/><textarea name=\"why_it_matters\" rows=\"3\">{story.why_it_matters}</textarea></label><br/><br/>
            <label>Category<br/><input type=\"text\" name=\"category\" value=\"{story.category}\" /></label><br/><br/>
            <label>Read time (minutes)<br/><input type=\"text\" name=\"read_time_minutes\" value=\"{story.read_time_minutes}\" /></label>
            <div class=\"actions\">
              <button class=\"save\" type=\"submit\">Save edits</button>
            </div>
          </form>
          <form method=\"post\" action=\"/story/{story.id}/approve\" class=\"actions\">
            <button class=\"approve\" type=\"submit\">Approve for issue</button>
          </form>
          <form method=\"post\" action=\"/story/{story.id}/reject\" class=\"actions\">
            <button class=\"reject\" type=\"submit\">Reject</button>
          </form>
        </div>
        """
        return HTMLResponse(page_shell(story.title, body))

    @app.post("/story/{story_id}/save")
    def save_story(
        story_id: int,
        summary: str = Form(...),
        why_it_matters: str = Form(...),
        category: str = Form(...),
        read_time_minutes: int = Form(...),
    ) -> RedirectResponse:
        update_story(
            story_id,
            summary=summary.strip(),
            why_it_matters=why_it_matters.strip(),
            category=category.strip(),
            read_time_minutes=read_time_minutes,
            status=StoryStatus.DRAFTED,
        )
        return RedirectResponse(url=f"/story/{story_id}", status_code=303)

    @app.post("/story/{story_id}/approve")
    def approve_story(story_id: int) -> RedirectResponse:
        update_story(story_id, status=StoryStatus.APPROVED)
        return RedirectResponse(url="/", status_code=303)

    @app.post("/story/{story_id}/reject")
    def reject_story(story_id: int) -> RedirectResponse:
        update_story(story_id, status=StoryStatus.REJECTED)
        return RedirectResponse(url="/", status_code=303)

    add_server_middleware(app, require_https=require_https)
    return app


app = create_review_app()
