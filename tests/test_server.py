from __future__ import annotations

from brief.server import _is_unsafe_forwarded_allow_ips, is_loopback_host, run_uvicorn


def test_is_loopback_host_recognises_local_addresses():
    assert is_loopback_host("127.0.0.1")
    assert is_loopback_host("localhost")
    assert is_loopback_host("::1")
    assert is_loopback_host("[::1]")


def test_is_loopback_host_rejects_public_bind_addresses():
    assert not is_loopback_host("0.0.0.0")
    assert not is_loopback_host("192.168.1.10")


def test_is_unsafe_forwarded_allow_ips_detects_wildcards():
    assert _is_unsafe_forwarded_allow_ips("*")
    assert _is_unsafe_forwarded_allow_ips("0.0.0.0/0")
    assert not _is_unsafe_forwarded_allow_ips("127.0.0.1")


def test_run_uvicorn_warns_on_wide_forwarded_allow_ips(monkeypatch):
    monkeypatch.setenv("BRIEF_FORWARDED_ALLOW_IPS", "*")
    warnings: list[str] = []

    def capture_warning(message, *args):
        warnings.append(message % args if args else message)

    monkeypatch.setattr("brief.server.logger.warning", capture_warning)
    monkeypatch.setattr(
        "uvicorn.run",
        lambda *args, **kwargs: None,
    )

    run_uvicorn(lambda: None, host="127.0.0.1", port=8787)

    assert warnings
    assert "BRIEF_FORWARDED_ALLOW_IPS" in warnings[0]
    assert "X-Forwarded-Proto" in warnings[0]
