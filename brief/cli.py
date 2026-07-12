from __future__ import annotations

import os
from datetime import date
from typing import Callable

import typer
from rich.console import Console
from rich.table import Table

from brief.draft import draft_candidates
from brief.feeds import check_all_sources, print_feed_check_table
from brief.ingest import ingest_sources
from brief.models import StoryStatus, count_stories, init_db, list_stories, load_edition_config
from brief.publish import publish_issue
from brief.server import resolve_tls_material, run_uvicorn, service_url

app = typer.Typer(help="Brief APAC MVP workflow CLI", no_args_is_help=True)
feeds_app = typer.Typer(help="RSS feed utilities")
app.add_typer(feeds_app, name="feeds")
console = Console()


@feeds_app.command("check")
def feeds_check() -> None:
    """Validate all RSS sources in config/sources.yaml (no database writes)."""
    results = check_all_sources()
    errors = print_feed_check_table(results, console=console)
    if errors:
        raise typer.Exit(code=1)


def _run_web_server(
    *,
    label: str,
    app_factory,
    host: str,
    port: int,
    https: bool,
    ssl_certfile: str | None,
    ssl_keyfile: str | None,
    require_https: bool | None,
    setup: Callable[[], None] | None = None,
) -> None:
    if setup is not None:
        setup()
    try:
        cert, key = resolve_tls_material(
            https=https,
            ssl_certfile=ssl_certfile,
            ssl_keyfile=ssl_keyfile,
        )
    except RuntimeError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc

    enforce_https = https if require_https is None else require_https
    web_app = app_factory(require_https=enforce_https)
    url = service_url(host, port, use_tls=bool(cert))
    console.print(f"{label}: [bold]{url}[/bold]")
    if label == "API":
        console.print(
            "[dim]Review UI (Vite): npm run dev:review in web/ → http://localhost:5173[/dim]"
        )
    if https and cert and key and not ssl_certfile and not ssl_keyfile:
        console.print("[dim]Using development TLS certificate in data/certs/[/dim]")
    run_uvicorn(web_app, host=host, port=port, ssl_certfile=cert, ssl_keyfile=key)


@app.command()
def init() -> None:
    """Initialise the database (SQLite or Supabase per BRIEF_DATABASE)."""
    import os

    init_db()
    backend = os.environ.get("BRIEF_DATABASE", "sqlite").strip().lower()
    if backend == "supabase":
        console.print("[green]Supabase database ready[/green]")
    else:
        console.print("[green]Database ready[/green] at data/brief.db")


@app.command()
def ingest(
    max_per_source: int = typer.Option(15, help="Max items to read per feed"),
    min_score: float | None = typer.Option(None, help="Override APAC score threshold"),
) -> None:
    """Fetch APAC RSS sources and store scored candidates."""
    init_db()
    stats = ingest_sources(max_per_source=max_per_source, min_score=min_score)
    table = Table(title="Ingest results")
    for key, value in stats.items():
        table.add_row(key, str(value))
    console.print(table)


@app.command()
def draft(
    limit: int | None = typer.Option(None, help="How many candidates to draft"),
    no_llm: bool = typer.Option(False, help="Skip OpenAI and use extractive summaries"),
) -> None:
    """Generate summaries for candidate stories."""
    init_db()
    count = draft_candidates(limit=limit, use_llm=not no_llm)
    console.print(f"[green]Drafted {count} stories[/green]")


@app.command(name="review")
def review_server(
    host: str = "127.0.0.1",
    port: int = 8787,
    https: bool = typer.Option(True, "--https/--no-https", help="Serve over HTTPS (default)."),
    ssl_certfile: str | None = typer.Option(None, help="TLS certificate PEM file"),
    ssl_keyfile: str | None = typer.Option(None, help="TLS private key PEM file"),
    require_https: bool | None = typer.Option(
        None,
        "--require-https/--allow-http",
        help="Redirect plain HTTP requests to HTTPS.",
    ),
) -> None:
    """Run the Brief APAC API (powers the TypeScript review UI)."""
    from brief.api_server import create_api_app

    _run_web_server(
        label="API",
        app_factory=create_api_app,
        host=host,
        port=port,
        https=https,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
        require_https=require_https,
        setup=init_db,
    )


@app.command()
def publish(
    issue_date: str | None = typer.Option(None, help="Issue date YYYY-MM-DD"),
) -> None:
    """Publish approved stories to markdown, HTML, email, and RSS outputs."""
    init_db()
    target = issue_date or date.today().isoformat()
    try:
        issue_dir = publish_issue(target)
    except ValueError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    console.print(f"[green]Published[/green] to {issue_dir}")

    leftover = [s for s in list_stories(StoryStatus.APPROVED, limit=100) if not s.issue_date]
    if leftover:
        console.print(
            f"[yellow]{len(leftover)} approved stor{'y' if len(leftover) == 1 else 'ies'} "
            "did not fit this issue and will roll into the next one.[/yellow]"
        )


@app.command()
def serve(
    host: str = "127.0.0.1",
    port: int = 8080,
) -> None:
    """Run the public issue viewer (Next.js dev server) for general readers."""
    import shutil
    import subprocess
    from pathlib import Path

    web_dir = Path(__file__).resolve().parent.parent / "web" / "public"
    if not (web_dir / "package.json").exists():
        console.print("[red]Next.js public app not found at web/public[/red]")
        raise typer.Exit(code=1)

    npm = shutil.which("npm")
    if not npm:
        console.print("[red]npm not found — install Node.js 20+[/red]")
        raise typer.Exit(code=1)

    console.print(f"Public site: [bold]http://{host}:{port}[/bold]")
    console.print("[dim]Starting Next.js (run npm run build in web/public for production)[/dim]")

    env = os.environ.copy()
    env["PORT"] = str(port)
    env["HOSTNAME"] = host
    try:
        subprocess.run(
            [npm, "run", "dev"],
            cwd=web_dir,
            env=env,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise typer.Exit(code=exc.returncode) from exc


@app.command()
def sync_public() -> None:
    """Rebuild issue.json files for published issues (public site data)."""
    from brief.publish import rebuild_issue_json

    init_db()
    dates = sorted(
        {
            story.issue_date
            for story in list_stories(StoryStatus.PUBLISHED, limit=500)
            if story.issue_date
        },
        reverse=True,
    )
    if not dates:
        console.print("[yellow]No published issues to sync[/yellow]")
        return
    for issue_date in dates:
        path = rebuild_issue_json(issue_date)
        if path:
            console.print(f"[green]Synced[/green] {path}")


@app.command()
def status() -> None:
    """Show queue counts."""
    init_db()
    edition = load_edition_config()["edition"]
    table = Table(title=f"{edition['name']} queue")
    for status in StoryStatus:
        table.add_row(status.value, str(count_stories(status)))
    console.print(table)


if __name__ == "__main__":
    app()
