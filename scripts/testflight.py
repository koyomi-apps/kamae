#!/usr/bin/env python3
# Kamae for iPhone
# SPDX-License-Identifier: GPL-3.0-or-later
"""Helps .github/workflows/testflight.yml put a build of Kamae for iPhone on TestFlight.

    python3 scripts/testflight.py notes [--markdown] VERSION BUILD
        Prints the build's section of ios/CHANGELOG.md, "## VERSION (BUILD)", as TestFlight's
        What to Test shows it: plain text, without Markdown. With --markdown, as it's written,
        for the GitHub release.

    python3 scripts/testflight.py what-to-test VERSION BUILD NOTES_FILE
        Waits until App Store Connect has processed the build, then fills in its What to Test
        from NOTES_FILE, in each of the app's TestFlight languages. Needs the environment
        variables APP_STORE_CONNECT_KEY_ID, APP_STORE_CONNECT_ISSUER_ID and
        APP_STORE_CONNECT_KEY_PATH, the API key's .p8 file.

Needs only Python's standard library, and the openssl command, which signs the API's tokens.
"""
from __future__ import annotations

import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

CHANGELOG = Path(__file__).resolve().parent.parent / "ios" / "CHANGELOG.md"
BUNDLE_ID = "ca.gureet.kitae"
API = "https://api.appstoreconnect.apple.com/v1"
# What to Test's limit.
LIMIT = 4000


def section(version: str, build: str) -> str:
    """The changelog's section for this build, as it's written."""
    heading = re.compile(rf"^## {re.escape(version)} \({re.escape(build)}\)(\s|$)")
    lines = CHANGELOG.read_text(encoding="utf-8").splitlines()
    for start, line in enumerate(lines):
        if heading.match(line):
            end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
            text = "\n".join(lines[start + 1 : end]).strip()
            if text:
                return text
            break
    sys.exit(f"ios/CHANGELOG.md has no section for {version} ({build}). Its heading would be "
             f'"## {version} ({build}) · YYYY-MM-DD", in place of "## Next build".')


def plain(markdown: str) -> str:
    """Markdown as TestFlight shows it: plain text."""
    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", r"\1 (\2)", markdown)
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)
    text = re.sub(r"(?<![\w*])\*([^*\n]+)\*(?![\w*])", r"\1", text)
    text = re.sub(r"`([^`\n]+)`", r"\1", text)
    text = re.sub(r"^- ", "• ", text, flags=re.MULTILINE)
    if len(text) > LIMIT:
        print(f"What to Test can only be {LIMIT} characters, so the end is cut off.", file=sys.stderr)
        text = text[: LIMIT - 1].rstrip() + "…"
    return text


def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def raw_signature(der: bytes) -> bytes:
    """An ECDSA signature as openssl writes it, SEQUENCE { INTEGER r, INTEGER s } in DER, as
    a JSON Web Token has it: r then s, 32 bytes each."""
    if der[0] != 0x30:
        raise ValueError("not an ECDSA signature")
    at = 2 if der[1] < 0x80 else 2 + (der[1] & 0x7F)
    numbers = []
    for _ in range(2):
        if der[at] != 0x02:
            raise ValueError("not an ECDSA signature")
        length = der[at + 1]
        numbers.append(int.from_bytes(der[at + 2 : at + 2 + length], "big").to_bytes(32, "big"))
        at += 2 + length
    return b"".join(numbers)


def token(key_id: str, issuer: str, key_path: str) -> str:
    """A token for the App Store Connect API, good for 15 minutes."""
    header = b64url(json.dumps({"alg": "ES256", "kid": key_id, "typ": "JWT"}).encode())
    now = int(time.time())
    claims = b64url(json.dumps({"iss": issuer, "iat": now, "exp": now + 15 * 60,
                                "aud": "appstoreconnect-v1"}).encode())
    signed = f"{header}.{claims}".encode()
    der = subprocess.run(["openssl", "dgst", "-sha256", "-sign", key_path], input=signed,
                         capture_output=True, check=True).stdout
    return f"{header}.{claims}.{b64url(raw_signature(der))}"


def call(method: str, path: str, query: dict | None = None, body: dict | None = None) -> dict:
    url = API + path + ("?" + urllib.parse.urlencode(query) if query else "")
    key = token(os.environ["APP_STORE_CONNECT_KEY_ID"], os.environ["APP_STORE_CONNECT_ISSUER_ID"],
                os.environ["APP_STORE_CONNECT_KEY_PATH"])
    request = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body else None,
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            data = response.read()
    except urllib.error.HTTPError as error:
        sys.exit(f"App Store Connect answered {error.code} to {method} {path}: "
                 f"{error.read().decode(errors='replace')}")
    return json.loads(data) if data else {}


def what_to_test(version: str, build: str, notes: str) -> None:
    apps = call("GET", "/apps", {"filter[bundleId]": BUNDLE_ID, "fields[apps]": "bundleId"})["data"]
    if not apps:
        sys.exit(f"App Store Connect has no app {BUNDLE_ID} that this key can see.")
    app = apps[0]["id"]
    # The build shows up a few minutes after the upload, and is processed some minutes later.
    deadline = time.time() + 45 * 60
    said = None
    while True:
        builds = call("GET", "/builds", {"filter[app]": app, "filter[version]": build,
                                         "filter[preReleaseVersion.version]": version,
                                         "fields[builds]": "version,processingState", "limit": "1"})["data"]
        state = builds[0]["attributes"]["processingState"] if builds else "not there yet"
        if state in ("VALID", "FAILED", "INVALID"):
            break
        if state != said:
            print(f"Build {version} ({build}) on App Store Connect: {state}. Waiting.", flush=True)
            said = state
        if time.time() > deadline:
            sys.exit(f"After 45 minutes, build {version} ({build}) is still {state} on App Store Connect. "
                     "Fill in What to Test on App Store Connect once it's processed.")
        time.sleep(30)
    if state != "VALID":
        sys.exit(f"App Store Connect couldn't process build {version} ({build}): {state}. "
                 "Apple emails the reason.")
    build_id = builds[0]["id"]
    print(f"Build {version} ({build}) is processed.")
    locales = [item["attributes"]["locale"] for item in
               call("GET", f"/apps/{app}/betaAppLocalizations", {"fields[betaAppLocalizations]": "locale"})["data"]]
    existing = {item["attributes"]["locale"]: item["id"] for item in
                call("GET", f"/builds/{build_id}/betaBuildLocalizations",
                     {"fields[betaBuildLocalizations]": "locale"})["data"]}
    for locale in sorted(set(locales or ["en-US"]) | set(existing)):
        if locale in existing:
            call("PATCH", f"/betaBuildLocalizations/{existing[locale]}", body={"data": {
                "type": "betaBuildLocalizations", "id": existing[locale], "attributes": {"whatsNew": notes}}})
        else:
            call("POST", "/betaBuildLocalizations", body={"data": {
                "type": "betaBuildLocalizations", "attributes": {"locale": locale, "whatsNew": notes},
                "relationships": {"build": {"data": {"type": "builds", "id": build_id}}}}})
        print(f"What to Test is filled in for {locale}.")


def main(args: list[str]) -> None:
    if len(args) >= 3 and args[0] == "notes":
        markdown = args[1] == "--markdown"
        rest = args[2:] if markdown else args[1:]
        if len(rest) == 2:
            text = section(*rest)
            print(text if markdown else plain(text))
            return
    if len(args) == 4 and args[0] == "what-to-test":
        what_to_test(args[1], args[2], Path(args[3]).read_text(encoding="utf-8").strip())
        return
    sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
