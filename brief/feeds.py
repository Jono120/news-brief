from __future__ import annotations

from dataclasses import dataclass

from rich.console import Console
from rich.table import Table

from brief.ingest import fetch_feed
from brief.models import load_sources_config


@dataclass
class FeedCheckResult:
    name: str
    url: str
    status: str
    entry_count: int
    sample_title: str
    error: str | None = None


def check_all_sources() -> list[FeedCheckResult]:
    results: list[FeedCheckResult] = []
    for source in load_sources_config():
        name = source.get("name", "Unknown")
        url = source.get("url", "")
        try:
            feed = fetch_feed(url)
            entries = feed.entries or []
            sample = ""
            if entries:
                sample = (entries[0].get("title") or "").strip()[:80]
            results.append(
                FeedCheckResult(
                    name=name,
                    url=url,
                    status="ok",
                    entry_count=len(entries),
                    sample_title=sample,
                )
            )
        except Exception as exc:
            results.append(
                FeedCheckResult(
                    name=name,
                    url=url,
                    status="error",
                    entry_count=0,
                    sample_title="",
                    error=str(exc),
                )
            )
    return results


def print_feed_check_table(
    results: list[FeedCheckResult],
    console: Console | None = None,
) -> int:
    console = console or Console()
    table = Table(title="Feed health check")
    table.add_column("Source", style="bold")
    table.add_column("Status")
    table.add_column("Entries", justify="right")
    table.add_column("Sample title")

    error_count = 0
    for result in results:
        if result.status == "error":
            error_count += 1
            status_cell = f"[red]error[/red]"
            sample = result.error or ""
        else:
            status_cell = "[green]ok[/green]"
            sample = result.sample_title or "[dim]—[/dim]"

        table.add_row(result.name, status_cell, str(result.entry_count), sample)

    console.print(table)
    if error_count:
        console.print(f"[red]{error_count} feed(s) failed[/red]")
    else:
        console.print(f"[green]All {len(results)} feeds OK[/green]")
    return error_count
