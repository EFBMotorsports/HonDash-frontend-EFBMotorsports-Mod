**HonDash Frontend — EFBMotorsports Mod**

This is a fork of HonDash-frontend, the browser-based dashboard for HonDash, a Raspberry Pi digital dash for Honda ECUs (Hondata S300 and similar). Full credit for the original project goes to Pablo Buenaposada.

This fork adds a new dashboard concept (src/cool.html) plus a few fixes and extra features on top of it.

What's different in this fork
src/cool.html — a redesigned dashboard: digital tiles or an analog cluster look, a settings menu (sensor layout, theme, tach/VTEC point, brightness), and live gauges fed by the real HonDash websocket.
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

**Installing this on a dashboard you already have running**

Don't worry — you will not break anything. This only adds one new screen file. Your existing dashboard, your ECU connection, everything else on the Pi stays exactly as it is.

What you're doing, in plain terms: there is one file, called cool.html, that has the new dashboard screen in it. You need to get a copy of that one file onto your Raspberry Pi, into the same folder where your other dashboard screens already live (a folder usually named HonDash-frontend/src). Then you tell the little screen/browser on your Pi to open that file instead of whichever one it currently opens.

**Step 1 — Get the file onto the Pi**

Pick whichever of these feels easiest — they all end with the same result.

Easiest: USB stick. Download cool.html (from this repo, or from whoever sent it to you) onto a laptop, put it on a USB stick, plug the stick into the Pi, and copy cool.html into the HonDash-frontend/src folder — right next to the other files already there (index.html, basic.html, etc).
If you're comfortable with a file-transfer program (like WinSCP, FileZilla, or Cyberduck): connect to your Pi the same way you normally do, and drag cool.html into the HonDash-frontend/src folder.
If you use a terminal / SSH: run this from your computer (not the Pi), swapping in your Pi's actual address and its real folder path:
  scp cool.html pi@<your-pi's-address>:/home/pi/Desktop/HonDash-frontend/src/cool.html
**Step 2 — Tell the Pi to show the new screen**

The Pi's screen shows a webpage in a browser running in "kiosk mode" (full screen, no address bar). Right now it's pointed at one of the old files (commonly basic.html); you need to point it at cool.html instead.

Where this setting lives varies by how your Pi was set up, but it's usually one line, somewhere that mentions chromium and a .html file — for example a startup script, a .desktop file, or a systemd service file. Find that line and change the filename in it from whatever it currently says (e.g. basic.html) to cool.html.
If you genuinely don't know where that is and nobody set it up for you, say so and we can go find it together, step by step.
**Step 3 — Restart**

Reboot the Pi, or just restart the browser (usually):

sudo systemctl restart chromium.service

Your dash should come up showing the new screen.

Bonus (optional): the "Exit to Linux" button

The new dashboard has a button to back out to the Pi's desktop. For that button to actually work, a couple of small helper files need to be installed too. This is optional — the dashboard works fine without it, you just won't be able to use that one button. If you want it, follow pi-setup/README.md — it's the same idea as above, just a few more small files to copy over.

**Running it**

Same as upstream — see the Makefile and Dockerfile:

bash
make docker/build
make docker/run       # serves the dashboard at http://localhost/

On a Raspberry Pi kiosk setup, point Chromium at the served address in kiosk mode (see make run_rpi in the Makefile), and follow pi-setup/README.md to enable the exit/relaunch flow.

License

Same license as upstream (ISC) — see package.json.
