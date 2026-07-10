from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

DEV_CERT_DIR = Path("data/certs")
DEV_CERT_FILE = DEV_CERT_DIR / "dev-cert.pem"
DEV_KEY_FILE = DEV_CERT_DIR / "dev-key.pem"


def _generate_with_openssl() -> None:
    openssl = shutil.which("openssl")
    if not openssl:
        return

    DEV_CERT_DIR.mkdir(parents=True, exist_ok=True)
    subject = "/CN=localhost"
    san = "subjectAltName=DNS:localhost,IP:127.0.0.1"
    command = [
        openssl,
        "req",
        "-x509",
        "-newkey",
        "rsa:2048",
        "-nodes",
        "-keyout",
        str(DEV_KEY_FILE),
        "-out",
        str(DEV_CERT_FILE),
        "-days",
        "825",
        "-subj",
        subject,
        "-addext",
        san,
    ]
    subprocess.run(command, check=True, capture_output=True, text=True)


def _generate_with_trustme() -> None:
    import trustme

    DEV_CERT_DIR.mkdir(parents=True, exist_ok=True)
    server_cert = trustme.CA().issue_cert("localhost", "127.0.0.1")
    DEV_CERT_FILE.write_bytes(server_cert.cert_chain_pems[0].bytes())
    DEV_KEY_FILE.write_bytes(server_cert.private_key_pem.bytes())


def ensure_dev_tls_certs() -> tuple[Path, Path]:
    """Create a local development TLS certificate if none exists."""
    if DEV_CERT_FILE.is_file() and DEV_KEY_FILE.is_file():
        return DEV_CERT_FILE, DEV_KEY_FILE

    try:
        _generate_with_openssl()
    except (OSError, subprocess.CalledProcessError):
        pass

    if DEV_CERT_FILE.is_file() and DEV_KEY_FILE.is_file():
        return DEV_CERT_FILE, DEV_KEY_FILE

    try:
        _generate_with_trustme()
    except Exception as exc:
        raise RuntimeError(
            "HTTPS requires TLS certificates. Install OpenSSL, add the trustme "
            "package, or pass --ssl-certfile and --ssl-keyfile."
        ) from exc

    return DEV_CERT_FILE, DEV_KEY_FILE
