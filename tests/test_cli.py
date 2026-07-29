from __future__ import annotations

from unittest.mock import MagicMock

from brief.cli import _run_web_server


def test_run_web_server_warns_when_api_binds_publicly_without_token(monkeypatch):
    messages: list[str] = []

    def capture_print(message: str, *args, **kwargs):
        messages.append(message)

    console = MagicMock()
    console.print = capture_print
    monkeypatch.setattr("brief.cli.console", console)
    monkeypatch.delenv("BRIEF_API_TOKEN", raising=False)
    monkeypatch.setattr(
        "brief.cli.resolve_tls_material",
        lambda **kwargs: (None, None),
    )
    monkeypatch.setattr(
        "brief.cli.run_uvicorn",
        lambda *args, **kwargs: None,
    )

    _run_web_server(
        label="API",
        app_factory=lambda require_https=False: MagicMock(),
        host="0.0.0.0",
        port=8787,
        https=False,
        ssl_certfile=None,
        ssl_keyfile=None,
        require_https=False,
    )

    assert any("BRIEF_API_TOKEN" in message for message in messages)
