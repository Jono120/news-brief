from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, Response
from fastapi.staticfiles import StaticFiles
from jinja2 import Environment, FileSystemLoader, select_autoescape

from brief.issues import (
    category_labels,
    edition_info,
    get_featured_issue,
    get_public_issue,
    list_public_issues,
)
from brief.server import add_server_middleware

TEMPLATE_DIR = Path(__file__).resolve().parent / "templates" / "public"
STATIC_DIR = Path(__file__).resolve().parent / "static" / "public"
FAVICON_PATH = STATIC_DIR / "favicon.ico"


def jinja_env() -> Environment:
    return Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "xml"]),
        trim_blocks=True,
        lstrip_blocks=True,
    )


def render(template_name: str, request: Request, **context) -> str:
    env = jinja_env()
    base_context = {
        "edition": edition_info(),
        "categories": category_labels(),
        "current_path": request.url.path,
        "site": {
            "title": edition_info()["name"],
            "tagline": edition_info()["tagline"],
            "description": "A concise weekday briefing on technology across the Asia-Pacific region, edited for APAC context.",
        },
    }
    base_context.update(context)
    return env.get_template(template_name).render(**base_context)


def create_public_app(*, require_https: bool = False) -> FastAPI:
    app = FastAPI(title="Brief APAC — Public")
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> str:
        featured = get_featured_issue()
        recent = list_public_issues(include_sample=True)[:6]
        return render("home.html.j2", request, featured=featured, recent=recent)

    @app.get("/issues", response_class=HTMLResponse)
    def issues_index(request: Request) -> str:
        issues = list_public_issues(include_sample=True)
        return render("issues.html.j2", request, issues=issues)

    @app.get("/issues/{issue_date}", response_class=HTMLResponse)
    def issue_detail(issue_date: str, request: Request) -> HTMLResponse:
        issue = get_public_issue(issue_date)
        if not issue:
            return HTMLResponse(
                content=render("not_found.html.j2", request),
                status_code=404,
            )
        all_issues = list_public_issues(include_sample=True)
        return HTMLResponse(content=render("issue.html.j2", request, issue=issue, all_issues=all_issues))

    @app.get("/accessibility", response_class=HTMLResponse)
    def accessibility(request: Request) -> str:
        return render("accessibility.html.j2", request)

    @app.get("/feed.xml", response_class=Response)
    def rss_feed(request: Request) -> Response:
        base_url = str(request.base_url).rstrip("/")
        issues = []
        for summary in list_public_issues(include_sample=True):
            issue = get_public_issue(summary.date)
            if issue:
                issues.append(issue)
        body = render(
            "rss.xml.j2",
            request,
            issues=issues,
            base_url=base_url,
        )
        return Response(content=body, media_type="application/rss+xml")

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> FileResponse:
        return FileResponse(FAVICON_PATH, media_type="image/x-icon")

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.exception_handler(404)
    async def not_found_handler(request: Request, exc: HTTPException) -> HTMLResponse:
        body = render("not_found.html.j2", request)
        return HTMLResponse(content=body, status_code=404)

    add_server_middleware(app, require_https=require_https)
    return app


app = create_public_app()
