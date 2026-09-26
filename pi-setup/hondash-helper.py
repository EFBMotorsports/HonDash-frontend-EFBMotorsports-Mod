#!/usr/bin/env python3
"""
Tiny local helper for HonDash's "Exit to Linux" button and its "Update now"
button.

Runs on the Pi itself, bound to 127.0.0.1 only (never reachable from the
network), and does exactly two fixed things on request - nothing here is
built from whatever the page sends:

  POST /exit    stops the kiosk browser so the plain desktop shows through.
                No "relaunch" endpoint on purpose - coming back to HonDash is
                done from a desktop icon instead (see hondash-relaunch.desktop),
                since once this stops the browser there's no webpage left for
                a button to live on.

  POST /update  downloads the current cool.html from a fixed GitHub repo/
                branch/path (the UPDATE_* constants below - not taken from
                the request) and drops it into the running frontend
                container with `docker cp`, so the dashboard can update
                itself with one tap, no computer needed. This only replaces
                that one file inside the *running* container; it does not
                touch the copy on disk or rebuild the image, so a full
                `docker rebuild`/`make docker/run` will still bring back
                whatever was last actually built into the image.
"""

import json
import os
import re
import subprocess
import tempfile
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
PORT = 8765

# only ever run this exact, hardcoded command - never anything derived from
# the request itself
STOP_KIOSK = ["sudo", "-n", "/usr/bin/systemctl", "stop", "chromium.service"]

# Where "Update now" pulls from and where it puts the result. Kept here,
# fixed, rather than taken from the page's request - edit these three lines
# if you fork this again or your setup differs.
UPDATE_REPO = "EFBMotorsports/HonDash-frontend-EFBMotorsports-Mod"
UPDATE_BRANCH = "main"
UPDATE_FILE_PATH = "src/cool.html"                    # path *inside* the repo
CONTAINER_NAME = "hondash-frontend"                   # `docker ps` name of the frontend container
CONTAINER_DEST = "/usr/share/nginx/html/cool.html"    # where nginx serves it from, inside that container

_REPO_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


def run_update():
    if not _REPO_RE.match(UPDATE_REPO):
        raise RuntimeError("UPDATE_REPO is misconfigured in hondash-helper.py")

    url = "https://raw.githubusercontent.com/{}/{}/{}".format(
        UPDATE_REPO, UPDATE_BRANCH, UPDATE_FILE_PATH
    )
    with urllib.request.urlopen(url, timeout=20) as resp:
        if resp.status != 200:
            raise RuntimeError("GitHub returned HTTP {}".format(resp.status))
        data = resp.read()
    if not data or b"<html" not in data[:2000].lower():
        raise RuntimeError("downloaded file didn't look like a dashboard page")

    fd, tmp_path = tempfile.mkstemp(prefix="cool-", suffix=".html")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        # mkstemp creates the file mode 600 (owner read/write only). docker cp
        # preserves that mode into the container, and nginx there runs as its
        # own unprivileged user - so left at 600 the copied file is unreadable
        # by nginx and every request for it 403s. World-readable like a normal
        # served file fixes it.
        os.chmod(tmp_path, 0o644)
        result = subprocess.run(
            ["docker", "cp", tmp_path, "{}:{}".format(CONTAINER_NAME, CONTAINER_DEST)],
            capture_output=True,
            text=True,
            timeout=20,
        )
        if result.returncode != 0:
            raise RuntimeError(
                "docker cp failed: " + (result.stderr or "unknown error").strip()
            )
        # belt-and-suspenders: also fix permissions *inside* the container,
        # in case some future docker version stops preserving/normalizing
        # mode bits the way it does today. A 403 here is a silent, ugly
        # failure mode, so this is worth the extra step.
        subprocess.run(
            ["docker", "exec", CONTAINER_NAME, "chmod", "644", CONTAINER_DEST],
            capture_output=True,
            text=True,
            timeout=10,
        )
    finally:
        try:
            os.remove(tmp_path)
        except OSError:
            pass


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def _json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        # a request body may be present (e.g. /update's {"repo": ...}) but is
        # always ignored - read and discard it so the connection doesn't hang
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)

        if self.path == "/exit":
            self.send_response(200)
            self._cors()
            self.end_headers()
            # respond first, then stop the browser we're currently answering
            # the request from - order matters here
            try:
                subprocess.Popen(STOP_KIOSK)
            except Exception:
                pass
            return

        if self.path == "/update":
            try:
                run_update()
            except Exception as e:
                self._json(500, {"error": str(e)})
                return
            self._json(200, {"ok": True})
            return

        self.send_response(404)
        self._cors()
        self.end_headers()

    def log_message(self, format, *args):
        pass  # keep the journal quiet


if __name__ == "__main__":
    HTTPServer((HOST, PORT), Handler).serve_forever()
