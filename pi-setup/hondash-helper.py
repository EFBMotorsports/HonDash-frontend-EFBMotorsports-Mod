#!/usr/bin/env python3
"""
Tiny local helper for HonDash's "Exit to Linux" button.

Runs on the Pi itself, bound to 127.0.0.1 only (never reachable from the
network), and does exactly one thing on request: stop the kiosk browser so
the plain desktop shows through. It has no "relaunch" endpoint on purpose —
coming back to HonDash is done from a desktop icon instead (see the
hondash-relaunch.desktop file), since once this stops the browser there's no
webpage left for a button to live on.
"""

import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = "127.0.0.1"
PORT = 8765

# only ever run these exact, hardcoded commands - never anything derived from
# the request itself
STOP_KIOSK = ["sudo", "-n", "/usr/bin/systemctl", "stop", "chromium.service"]


class Handler(BaseHTTPRequestHandler):
    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.end_headers()

    def do_POST(self):
        if self.path != "/exit":
            self.send_response(404)
            self._cors()
            self.end_headers()
            return
        self.send_response(200)
        self._cors()
        self.end_headers()
        # respond first, then stop the browser we're currently answering the
        # request from - order matters here
        try:
            subprocess.Popen(STOP_KIOSK)
        except Exception:
            pass

    def log_message(self, format, *args):
        pass  # keep the journal quiet


if __name__ == "__main__":
    HTTPServer((HOST, PORT), Handler).serve_forever()
