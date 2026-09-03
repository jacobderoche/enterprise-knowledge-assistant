#!/usr/bin/env python3
"""Mint a local HS256 JWT for testing the backend (no external dependencies).

The signing secret must match the backend's ``app.jwt-secret``.

Examples:
    python scripts/mint-jwt.py --sub alice --roles employee
    python scripts/mint-jwt.py --sub root --roles admin --scopes hr-confidential
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import json
import time

DEFAULT_SECRET = "local-dev-secret-change-me-please-32bytes-minimum!!"


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def mint(secret: str, sub: str, roles: list[str], scopes: list[str], ttl: int) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    now = int(time.time())
    payload = {
        "sub": sub,
        "roles": roles,
        "scopes": scopes,
        "iat": now,
        "exp": now + ttl,
    }
    signing_input = (
        _b64url(json.dumps(header, separators=(",", ":")).encode())
        + "."
        + _b64url(json.dumps(payload, separators=(",", ":")).encode())
    )
    signature = hmac.new(secret.encode(), signing_input.encode(), hashlib.sha256).digest()
    return signing_input + "." + _b64url(signature)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sub", default="dev-user")
    parser.add_argument("--roles", default="employee", help="comma-separated roles")
    parser.add_argument("--scopes", default="", help="comma-separated extra ACL scopes")
    parser.add_argument("--secret", default=DEFAULT_SECRET)
    parser.add_argument("--ttl", type=int, default=3600, help="token lifetime in seconds")
    args = parser.parse_args()

    roles = [r.strip() for r in args.roles.split(",") if r.strip()]
    scopes = [s.strip() for s in args.scopes.split(",") if s.strip()]
    print(mint(args.secret, args.sub, roles, scopes, args.ttl))


if __name__ == "__main__":
    main()
