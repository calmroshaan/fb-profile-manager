# 🛡️ FB Profile Manager

A free, open-source browser profile manager that generates unique browser fingerprints for each profile. Built with Python + Playwright.

> Manage multiple browser profiles on the same PC — each with a completely isolated identity: unique canvas fingerprint, WebGL, timezone, language, screen resolution, and cookie storage.

---

## Features

- 🔏 Unique browser fingerprint per profile (canvas, WebGL, audio, navigator)
- 🌍 VPN city assignment — timezone & language auto-match your VPN location
- 🍪 100% isolated cookie & localStorage per profile
- ⚠️ Pre-launch VPN reminder so you never forget which city to connect
- 🖥️ Comfortable browser window (no more off-screen launching)
- ⚡ Bulk create & bulk assign VPN cities across 10+ profiles
- 🆓 Completely free — only needs Python + Playwright

---

## What Gets Spoofed Per Profile

| Signal | Spoofed |
|---|---|
| User Agent | ✅ |
| Screen Resolution | ✅ |
| Timezone | ✅ Matches VPN city |
| Language | ✅ Matches VPN city |
| Platform (Win/Mac/Linux) | ✅ |
| CPU Core Count | ✅ |
| RAM Amount | ✅ |
| WebGL Vendor & Renderer | ✅ |
| Canvas Fingerprint | ✅ Unique pixel noise |
| Audio Fingerprint | ✅ Unique buffer noise |
| Cookies & Storage | ✅ 100% isolated |
| webdriver detection flag | ✅ Removed |

---

## Requirements

- Windows 10/11
- Python 3.9+ → https://python.org
- That's it — everything else installs automatically

---

## Installation & Run

### Option A — Double click (easiest)
1. Download or clone this repo
2. Double-click **`START.bat`**
3. First run installs Playwright + Chromium automatically

### Option B — Manual
```bash
pip install -r requirements.txt
playwright install chromium
python main.py
```

---

## Quick Start

```
[8] Bulk create profiles
    → Base name: fb
    → Count: 10
    → Auto-assign VPN cities: y

[6] Launch profile
    → Enter: fb_01
    → Tool reminds you which VPN city to connect
    → Browser opens with unique fingerprint
```

---

## VPN Cities Supported (32 cities)

🇺🇸 USA · 🇬🇧 UK · 🇨🇦 Canada · 🇦🇺 Australia · 🇩🇪 Germany · 🇫🇷 France · 🇳🇱 Netherlands · 🇸🇬 Singapore · 🇯🇵 Japan · 🇮🇳 India · 🇦🇪 UAE · 🇵🇰 Pakistan · 🇧🇷 Brazil · 🇿🇦 South Africa

---

## Project Structure

```
fb-profile-manager/
├── main.py                  ← Main menu dashboard
├── fingerprint_engine.py    ← Fingerprint generator + VPN city database
├── browser_launcher.py      ← Playwright browser launcher with stealth JS
├── START.bat                ← Windows one-click launcher
├── requirements.txt
└── profiles/                ← Created on first run (gitignored)
    ├── fb_01.json           ← Per-profile fingerprint config
    └── browser_data_fb_01/  ← Isolated browser storage
```

---

## Notes

- `profiles/` folder is gitignored — your profile data stays private
- Each profile's fingerprint is deterministic (same name = same fingerprint every run)
- Browser window size is fixed at 1280×800 for comfort — the spoofed screen size reported to JS is separate and unique per profile

---

## License

MIT — free to use, modify, and share.
