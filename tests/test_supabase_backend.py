from __future__ import annotations

import base64
import json

import pytest

from brief.db.supabase_backend import _decode_supabase_key_role, _validate_supabase_key


def _fake_supabase_key(role: str) -> str:
    payload = base64.urlsafe_b64encode(json.dumps({"role": role}).encode()).decode().rstrip("=")
    return f"eyJhbGciOiJIUzI1NiJ9.{payload}.signature"


def test_decode_supabase_key_role_reads_role_claim():
    assert _decode_supabase_key_role(_fake_supabase_key("service_role")) == "service_role"
    assert _decode_supabase_key_role(_fake_supabase_key("anon")) == "anon"


def test_validate_supabase_key_rejects_anon_key():
    with pytest.raises(RuntimeError, match="service_role"):
        _validate_supabase_key(_fake_supabase_key("anon"))


def test_validate_supabase_key_accepts_service_role_key():
    _validate_supabase_key(_fake_supabase_key("service_role"))
