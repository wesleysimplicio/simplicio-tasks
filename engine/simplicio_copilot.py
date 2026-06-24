"""Simplicio Copilot auth — native, stdlib-only GitHub Copilot OAuth manager.

Port of headroom's ``copilot-auth`` subsystem. Manages a GitHub Copilot OAuth
token via the GitHub **device-code flow** so Copilot CLI traffic can be routed
through the Simplicio capture proxy, then exchanges that OAuth token for the
short-lived Copilot API bearer used by the Copilot endpoints.

Stdlib only: urllib, json, os, time, stat, argparse, hashlib.

Subcommands:
  login   -> GitHub OAuth device flow, store the OAuth token to ~/.simplicio
  token   -> exchange the stored OAuth token for a short-lived Copilot bearer
  status  -> report whether an OAuth token is stored and if exchange works
  logout  -> delete the stored token

Network calls go ONLY to github.com / api.github.com. The token file lives under
~/.simplicio (or SIMPLICIO_HOME), chmod 600. Secrets are never printed except by
the explicit ``token`` command (which prints the short-lived Copilot bearer).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import sys
import time
from pathlib import Path
from urllib import error as urllib_error
from urllib import request as urllib_request

__version__ = "1.0.0"

# Well-known public client id of the GitHub Copilot CLI / Chat OAuth app.
COPILOT_CHAT_OAUTH_CLIENT_ID = "Iv1.b507a08c87ecfe98"
DEFAULT_GITHUB_HOST = "github.com"
DEVICE_CODE_URL = "https://github.com/login/device/code"
ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
TOKEN_EXCHANGE_URL = "https://api.github.com/copilot_internal/v2/token"
DEVICE_CODE_GRANT_TYPE = "urn:ietf:params:oauth:grant-type:device_code"
OAUTH_SCOPE = "read:user"

# Headers the Copilot endpoints expect on the token-exchange call.
_USER_AGENT = "GitHubCopilotChat/0.35.0"
_EDITOR_VERSION = "vscode/1.107.0"
_EDITOR_PLUGIN_VERSION = "copilot-chat/0.35.0"
_COPILOT_INTEGRATION_ID = "vscode-chat"

_TOKEN_EXPIRY_BUFFER_S = 60
_HTTP_TIMEOUT_S = 15.0

HOME = os.path.expanduser("~")
DATA_DIR = Path(os.environ.get("SIMPLICIO_HOME", Path(HOME) / ".simplicio"))


# --------------------------------------------------------------------------- #
# Paths + storage
# --------------------------------------------------------------------------- #
def auth_path() -> Path:
    """Path where the GitHub OAuth token is persisted."""
    override = os.environ.get("SIMPLICIO_COPILOT_AUTH_FILE", "").strip()
    if override:
        return Path(override).expanduser()
    return DATA_DIR / "copilot_oauth.json"


def token_cache_path() -> Path:
    """Path where the short-lived exchanged Copilot bearer is cached."""
    return auth_path().parent / "copilot_token_cache.json"


def token_fingerprint(token: str) -> str:
    """Stable non-secret fingerprint for safe logging/comparison."""
    digest = hashlib.sha256(token.encode("utf-8", errors="ignore")).hexdigest()
    return f"sha256:{digest[:12]}"


def _write_secret_file(path: Path, body: dict) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    try:
        path.chmod(stat.S_IRUSR | stat.S_IWUSR)  # 0o600
    except OSError:
        pass
    return path


def save_oauth_token(token: str, *, domain: str = DEFAULT_GITHUB_HOST) -> Path:
    token = token.strip()
    if not token:
        raise ValueError("Copilot OAuth token must not be empty.")
    return _write_secret_file(
        auth_path(),
        {
            "type": "oauth",
            "provider": "github-copilot",
            "token": token,
            "domain": domain,
            "created_at": int(time.time()),
        },
    )


def read_oauth_token() -> str | None:
    try:
        payload = json.loads(auth_path().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None
    if not isinstance(payload, dict) or payload.get("type") != "oauth":
        return None
    token = payload.get("token")
    return token.strip() if isinstance(token, str) and token.strip() else None


def delete_oauth_token() -> bool:
    """Delete both the OAuth token file and any cached exchanged bearer."""
    removed = False
    for path in (auth_path(), token_cache_path()):
        try:
            path.unlink()
            removed = True
        except FileNotFoundError:
            pass
        except OSError:
            pass
    return removed


def _read_cached_api_token() -> tuple[str, float] | None:
    try:
        payload = json.loads(token_cache_path().read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None
    if not isinstance(payload, dict):
        return None
    token = payload.get("token")
    expires_at = payload.get("expires_at")
    if not isinstance(token, str) or not token.strip():
        return None
    try:
        expires_at = float(expires_at)
    except (TypeError, ValueError):
        return None
    if time.time() >= (expires_at - _TOKEN_EXPIRY_BUFFER_S):
        return None
    return token.strip(), expires_at


def _cache_api_token(token: str, expires_at: float) -> None:
    _write_secret_file(
        token_cache_path(),
        {"token": token, "expires_at": expires_at, "cached_at": int(time.time())},
    )


# --------------------------------------------------------------------------- #
# HTTP helpers (stdlib urllib)
# --------------------------------------------------------------------------- #
def _post_json(url: str, body: dict) -> dict:
    data = json.dumps(body, separators=(",", ":")).encode("utf-8")
    request = urllib_request.Request(
        url,
        data=data,
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": _USER_AGENT,
        },
        method="POST",
    )
    with urllib_request.urlopen(request, timeout=_HTTP_TIMEOUT_S) as response:
        payload = json.loads(response.read().decode("utf-8", errors="replace"))
    if not isinstance(payload, dict):
        raise RuntimeError("GitHub returned an invalid (non-object) response.")
    return payload


def _exchange_headers(oauth_token: str) -> dict:
    return {
        "Accept": "application/json",
        "Authorization": f"Bearer {oauth_token}",
        "User-Agent": _USER_AGENT,
        "Editor-Version": _EDITOR_VERSION,
        "Editor-Plugin-Version": _EDITOR_PLUGIN_VERSION,
        "Copilot-Integration-Id": _COPILOT_INTEGRATION_ID,
    }


# --------------------------------------------------------------------------- #
# Device flow
# --------------------------------------------------------------------------- #
def start_device_authorization() -> dict:
    """POST device/code -> {user_code, device_code, verification_uri, ...}."""
    payload = _post_json(
        DEVICE_CODE_URL,
        {"client_id": COPILOT_CHAT_OAUTH_CLIENT_ID, "scope": OAUTH_SCOPE},
    )
    for key in ("device_code", "user_code", "verification_uri"):
        if not str(payload.get(key) or "").strip():
            raise RuntimeError("GitHub device authorization returned an incomplete response.")
    return payload


def poll_device_authorization(
    device_code: str, *, interval: int = 5, expires_in: int = 900
) -> str:
    """Poll the access-token endpoint until authorized; return the OAuth token."""
    deadline = time.time() + max(1, expires_in)
    poll_interval = max(1, interval)
    while time.time() < deadline:
        payload = _post_json(
            ACCESS_TOKEN_URL,
            {
                "client_id": COPILOT_CHAT_OAUTH_CLIENT_ID,
                "device_code": device_code,
                "grant_type": DEVICE_CODE_GRANT_TYPE,
            },
        )
        access_token = payload.get("access_token")
        if isinstance(access_token, str) and access_token.strip():
            return access_token.strip()

        error = str(payload.get("error") or "").strip()
        if error == "authorization_pending":
            time.sleep(poll_interval)
            continue
        if error == "slow_down":
            poll_interval += 5
            time.sleep(poll_interval)
            continue
        if error == "expired_token":
            raise RuntimeError("GitHub device authorization expired before you authorized it.")
        if error:
            desc = str(payload.get("error_description") or error).strip()
            raise RuntimeError(f"GitHub device authorization failed: {desc}")
        time.sleep(poll_interval)

    raise RuntimeError("GitHub device authorization timed out.")


# --------------------------------------------------------------------------- #
# Token exchange
# --------------------------------------------------------------------------- #
def exchange_copilot_token(oauth_token: str) -> dict:
    """GET copilot_internal/v2/token -> short-lived Copilot bearer payload."""
    request = urllib_request.Request(
        TOKEN_EXCHANGE_URL, headers=_exchange_headers(oauth_token), method="GET"
    )
    try:
        with urllib_request.urlopen(request, timeout=_HTTP_TIMEOUT_S) as response:
            payload = json.loads(response.read().decode("utf-8", errors="replace"))
    except urllib_error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Copilot token exchange failed (HTTP {exc.code}): {body}") from exc
    if not isinstance(payload, dict):
        raise RuntimeError("Copilot token exchange returned an invalid response.")
    token = str(payload.get("token") or "").strip()
    if not token:
        raise RuntimeError("Copilot token exchange returned an empty token.")
    return payload


def get_api_token() -> tuple[str, float]:
    """Return a valid short-lived Copilot bearer (cached) + its expiry."""
    cached = _read_cached_api_token()
    if cached is not None:
        return cached

    oauth_token = read_oauth_token()
    if not oauth_token:
        raise RuntimeError("No GitHub Copilot OAuth token is stored. Run `login` first.")

    payload = exchange_copilot_token(oauth_token)
    token = str(payload["token"]).strip()
    expires_at = payload.get("expires_at")
    try:
        expires_at = float(expires_at)
    except (TypeError, ValueError):
        expires_at = time.time() + 1800
    _cache_api_token(token, expires_at)
    return token, expires_at


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #
def cmd_login(_args: argparse.Namespace) -> int:
    try:
        device = start_device_authorization()
    except Exception as exc:
        print(f"error: unable to start GitHub device login: {exc}", file=sys.stderr)
        return 1

    verification_uri = str(device.get("verification_uri")).strip()
    user_code = str(device.get("user_code")).strip()
    device_code = str(device.get("device_code")).strip()
    interval = int(device.get("interval") or 5)
    expires_in = int(device.get("expires_in") or 900)

    print("GitHub Copilot OAuth login (device flow)")
    print(f"  1. Open: {verification_uri}")
    print(f"  2. Enter code: {user_code}")
    print("  Waiting for authorization... (Ctrl-C to abort)")

    try:
        token = poll_device_authorization(
            device_code, interval=interval, expires_in=expires_in
        )
    except KeyboardInterrupt:
        print("\naborted.", file=sys.stderr)
        return 130
    except Exception as exc:
        print(f"error: GitHub device login failed: {exc}", file=sys.stderr)
        return 1

    try:
        path = save_oauth_token(token)
    except Exception as exc:
        print(f"error: unable to save token: {exc}", file=sys.stderr)
        return 1

    print(f"  Saved: {path}")
    print(f"  Token fingerprint: {token_fingerprint(token)}")
    return 0


def cmd_token(_args: argparse.Namespace) -> int:
    try:
        token, _expires_at = get_api_token()
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(token)
    return 0


def cmd_status(_args: argparse.Namespace) -> int:
    path = auth_path()
    oauth_token = read_oauth_token()
    print(f"Auth file: {path}")
    if not oauth_token:
        print("Status: not authenticated (no OAuth token stored)")
        print("Hint: run `login` to authenticate via the GitHub device flow.")
        return 1

    print("Status: authenticated")
    print(f"OAuth token fingerprint: {token_fingerprint(oauth_token)}")
    try:
        api_token, expires_at = get_api_token()
    except Exception as exc:
        print(f"Copilot token exchange: FAILED ({exc})")
        return 1
    remaining = max(0, int(expires_at - time.time()))
    print(f"Copilot token exchange: OK (bearer {token_fingerprint(api_token)}, "
          f"expires in ~{remaining}s)")
    return 0


def cmd_logout(_args: argparse.Namespace) -> int:
    removed = delete_oauth_token()
    if removed:
        print("Logged out: stored Copilot token(s) deleted.")
    else:
        print("Already logged out: no stored Copilot token.")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="simplicio_copilot",
        description="Native GitHub Copilot OAuth manager (device flow + token exchange).",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("login", help="GitHub OAuth device flow; store the OAuth token").set_defaults(
        func=cmd_login
    )
    sub.add_parser("token", help="print a short-lived Copilot API bearer").set_defaults(
        func=cmd_token
    )
    sub.add_parser("status", help="show auth + token-exchange status").set_defaults(
        func=cmd_status
    )
    sub.add_parser("logout", help="delete the stored token").set_defaults(func=cmd_logout)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
