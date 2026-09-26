# Pi kiosk-exit setup

These three files aren't part of the web frontend build — they're small OS-level
pieces that live directly on the Raspberry Pi, next to the kiosk browser, so an
"Exit to Linux" button on the dashboard can actually drop you to the desktop
and you can get back into HonDash afterward.

- **`hondash-helper.py`** — a tiny local HTTP server (bound to `127.0.0.1:8765`,
  never reachable from the network) that does exactly one thing when it
  receives a POST to `/exit`: stops the kiosk browser (`chromium.service`).
  It intentionally has no "relaunch" endpoint, since once it stops the
  browser there's no webpage left for a button to live on.
- **`hondash-helper.service`** — a systemd unit that runs the helper script
  automatically on boot and restarts it if it ever dies.
- **`hondash-relaunch.desktop`** — a desktop shortcut (shows up as a "HonDash"
  icon on the Pi's desktop) that starts `chromium.service` back up, so you
  can get back into the dashboard after exiting to the desktop.

## Installing on the Pi

```bash
# copy the helper script
sudo cp hondash-helper.py /home/pi/Desktop/hondash-helper.py

# install and enable the systemd service
sudo cp hondash-helper.service /etc/systemd/system/hondash-helper.service
sudo systemctl daemon-reload
sudo systemctl enable --now hondash-helper.service

# install the relaunch shortcut on the desktop
cp hondash-relaunch.desktop /home/pi/Desktop/hondash-relaunch.desktop
chmod +x /home/pi/Desktop/hondash-relaunch.desktop
```

You'll also need to let the `pi` user run the one exact command the helper
calls without a password prompt (since the helper runs as `pi`, not root):

```bash
echo 'pi ALL=(root) NOPASSWD: /usr/bin/systemctl stop chromium.service' | sudo tee /etc/sudoers.d/hondash-helper
```

After that, the dashboard's "Exit to Linux" button in `src/cool.html` (which
POSTs to `http://127.0.0.1:8765/exit`) will actually stop the kiosk, and the
desktop "HonDash" icon will bring it back.
