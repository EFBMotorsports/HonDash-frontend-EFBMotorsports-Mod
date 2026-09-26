HonDash Frontend — EFBMotorsports Mod

This is a fork of HonDash-frontend, the browser-based dashboard for HonDash, a Raspberry Pi digital dash for Honda ECUs (Hondata S300 and similar). Full credit for the original project goes to Pablo Buenaposada.

This fork adds a new dashboard concept (src/cool.html) plus a few fixes and extra features on top of it.

What's different in this fork
src/cool.html — a redesigned dashboard: digital tiles or an analog EF-cluster look, a settings menu (sensor layout, theme, tach/VTEC point, brightness), and live gauges fed by the real HonDash websocket.
Instant RPM and throttle — the tach and throttle bar track the live feed immediately instead of being smoothed like the other, noisier sensors.
No more stuck alarms — the red alarm border used to freeze on whatever a sensor last read the instant the ECU connection dropped (e.g. shutting the car off). Values now reset to safe defaults on disconnect, and the air/fuel reading no longer counts toward the alarm unless the engine is actually running above idle.
Tap-to-adjust thresholds — tap the Coolant, Intake air, Air/fuel, Battery, or Fuel level tile (or gauge, in analog mode) on the main screen to open +/- steppers for that sensor's amber/red warning points. Saved per-browser, with a reset-to-default option per sensor.
pi-setup/ — the OS-level pieces (not part of the web build) that let the dashboard's "Exit to Linux" button actually drop to the desktop and get back in. See pi-setup/README.md for install steps.

Screenshots
<img width="1024" height="600" alt="image" src="https://github.com/user-attachments/assets/7d76429e-979f-4a2f-98a0-edb00d34c897" />
<img width="1024" height="600" alt="image" src="https://github.com/user-attachments/assets/fcbe86e8-417a-47e6-9a21-802a500d665c" />
<img width="1024" height="600" alt="image" src="https://github.com/user-attachments/assets/1ab01f24-f517-413e-86d8-7bf2ad897f35" />
<img width="1024" height="600" alt="image" src="https://github.com/user-attachments/assets/530a440f-3a89-4674-b86c-fa2951020c15" />
<img width="1024" height="600" alt="image" src="https://github.com/user-attachments/assets/3462d83d-5144-434e-bfce-5ebf401d6d95" />

Installing on top of an existing HonDash install

You don't need to touch the HonDash backend, the Hondata connection, or anything else already running on your Pi — this fork only replaces/adds the frontend page. Pick whichever matches how your Pi is currently set up:

You deployed the frontend via Docker (the standard HonDash install)
On the Pi, clone this fork (instead of, or alongside, the original repo).
Rebuild the frontend image from it: make docker/build
Restart the container: make docker/run — this replaces the running hondash-frontend container on the same port/network, so nothing else in your existing setup needs to change.
Point the kiosk browser at http://hondash.local/cool.html instead of whatever page it currently loads (edit wherever the Chromium kiosk command/autostart entry lives on your Pi).
You're just swapping files by hand (no Docker rebuild)
Copy src/cool.html onto the Pi, into the same folder your existing HonDash frontend already serves from (next to index.html/basic.html).
Point the kiosk browser at that file's URL, e.g. http://hondash.local/cool.html.
If you don't already have an "Exit to Linux" helper set up from a previous HonDash install, follow pi-setup/README.md to add one.
Running it

Same as upstream — see the Makefile and Dockerfile:

bash
make docker/build
make docker/run       # serves the dashboard at http://localhost/

On a Raspberry Pi kiosk setup, point Chromium at the served address in kiosk mode (see make run_rpi in the Makefile), and follow pi-setup/README.md to enable the exit/relaunch flow.

License

Same license as upstream (ISC) — see package.json.
