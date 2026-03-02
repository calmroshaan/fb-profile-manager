"""
Fingerprint Engine v3 - Maximum GoLogin-level spoofing
Covers every detectable signal Facebook and fingerprint services check
"""

import json
import random
import hashlib
import os
from pathlib import Path

# ─── VPN City Database ────────────────────────────────────────────────────────

VPN_CITIES = {
    "New York, USA":        {"timezone": "America/New_York",    "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → New York"},
    "Los Angeles, USA":     {"timezone": "America/Los_Angeles", "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Los Angeles"},
    "Chicago, USA":         {"timezone": "America/Chicago",     "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Chicago"},
    "Dallas, USA":          {"timezone": "America/Chicago",     "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Dallas"},
    "Miami, USA":           {"timezone": "America/New_York",    "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Miami"},
    "Seattle, USA":         {"timezone": "America/Los_Angeles", "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Seattle"},
    "Phoenix, USA":         {"timezone": "America/Phoenix",     "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Phoenix"},
    "Denver, USA":          {"timezone": "America/Denver",      "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Denver"},
    "Atlanta, USA":         {"timezone": "America/New_York",    "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Atlanta"},
    "Boston, USA":          {"timezone": "America/New_York",    "languages": ["en-US", "en"], "flag": "🇺🇸", "hint": "Search 'United States' → Boston"},
    "London, UK":           {"timezone": "Europe/London",       "languages": ["en-GB", "en"], "flag": "🇬🇧", "hint": "Search 'United Kingdom' → London"},
    "Manchester, UK":       {"timezone": "Europe/London",       "languages": ["en-GB", "en"], "flag": "🇬🇧", "hint": "Search 'United Kingdom' → Manchester"},
    "Toronto, Canada":      {"timezone": "America/Toronto",     "languages": ["en-CA", "en"], "flag": "🇨🇦", "hint": "Search 'Canada' → Toronto"},
    "Vancouver, Canada":    {"timezone": "America/Vancouver",   "languages": ["en-CA", "en"], "flag": "🇨🇦", "hint": "Search 'Canada' → Vancouver"},
    "Montreal, Canada":     {"timezone": "America/Toronto",     "languages": ["en-CA", "fr-CA", "en"], "flag": "🇨🇦", "hint": "Search 'Canada' → Montreal"},
    "Sydney, Australia":    {"timezone": "Australia/Sydney",    "languages": ["en-AU", "en"], "flag": "🇦🇺", "hint": "Search 'Australia' → Sydney"},
    "Melbourne, Australia": {"timezone": "Australia/Melbourne", "languages": ["en-AU", "en"], "flag": "🇦🇺", "hint": "Search 'Australia' → Melbourne"},
    "Frankfurt, Germany":   {"timezone": "Europe/Berlin",       "languages": ["de-DE", "de", "en"], "flag": "🇩🇪", "hint": "Search 'Germany' → Frankfurt"},
    "Berlin, Germany":      {"timezone": "Europe/Berlin",       "languages": ["de-DE", "de", "en"], "flag": "🇩🇪", "hint": "Search 'Germany' → Berlin"},
    "Paris, France":        {"timezone": "Europe/Paris",        "languages": ["fr-FR", "fr", "en"], "flag": "🇫🇷", "hint": "Search 'France' → Paris"},
    "Amsterdam, NL":        {"timezone": "Europe/Amsterdam",    "languages": ["nl-NL", "en"], "flag": "🇳🇱", "hint": "Search 'Netherlands' → Amsterdam"},
    "Singapore":            {"timezone": "Asia/Singapore",      "languages": ["en-SG", "en"], "flag": "🇸🇬", "hint": "Search 'Singapore'"},
    "Tokyo, Japan":         {"timezone": "Asia/Tokyo",          "languages": ["ja-JP", "ja", "en"], "flag": "🇯🇵", "hint": "Search 'Japan' → Tokyo"},
    "Mumbai, India":        {"timezone": "Asia/Kolkata",        "languages": ["en-IN", "en"], "flag": "🇮🇳", "hint": "Search 'India' → Mumbai"},
    "Delhi, India":         {"timezone": "Asia/Kolkata",        "languages": ["en-IN", "en"], "flag": "🇮🇳", "hint": "Search 'India' → Delhi"},
    "Sao Paulo, Brazil":    {"timezone": "America/Sao_Paulo",   "languages": ["pt-BR", "pt", "en"], "flag": "🇧🇷", "hint": "Search 'Brazil' → Sao Paulo"},
    "Dubai, UAE":           {"timezone": "Asia/Dubai",          "languages": ["ar-AE", "en"], "flag": "🇦🇪", "hint": "Search 'UAE' → Dubai"},
    "Karachi, Pakistan":    {"timezone": "Asia/Karachi",        "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰", "hint": "Search 'Pakistan' → Karachi"},
    "Lahore, Pakistan":     {"timezone": "Asia/Karachi",        "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰", "hint": "Search 'Pakistan' → Lahore"},
    "Islamabad, Pakistan":  {"timezone": "Asia/Karachi",        "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰", "hint": "Search 'Pakistan' → Islamabad"},
    "Johannesburg, SA":     {"timezone": "Africa/Johannesburg", "languages": ["en-ZA", "en"], "flag": "🇿🇦", "hint": "Search 'South Africa' → Johannesburg"},
    "No VPN (Local)":       {"timezone": None, "languages": ["en-US", "en"], "flag": "🖥️",  "hint": "Run without VPN — use real local IP"},
}

# ─── Data Pools ───────────────────────────────────────────────────────────────

USER_AGENTS = [
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "120"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "121"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "119"},
    {"ua": "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",    "os": "Windows", "browser": "chrome",  "chrome_ver": "120"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36", "os": "Mac",  "browser": "chrome",  "chrome_ver": "120"},
    {"ua": "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",  "os": "Mac",  "browser": "chrome",  "chrome_ver": "121"},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",                                    "os": "Windows", "browser": "firefox", "chrome_ver": None},
    {"ua": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0", "os": "Windows", "browser": "edge", "chrome_ver": "120"},
    {"ua": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",              "os": "Linux",   "browser": "chrome",  "chrome_ver": "120"},
]

# OS → matching platform string
OS_PLATFORM = {
    "Windows": "Win32",
    "Mac":     "MacIntel",
    "Linux":   "Linux x86_64",
}

# OS → matching screen resolutions (Mac has different ones)
OS_SCREENS = {
    "Windows": [(1920,1080),(1920,1080),(1920,1080),(2560,1440),(1366,768),(1536,864),(1280,720),(1680,1050)],
    "Mac":     [(2560,1600),(2560,1440),(1440,900),(1680,1050),(3024,1964)],
    "Linux":   [(1920,1080),(1920,1080),(2560,1440),(1366,768),(1280,1024)],
}

HARDWARE_CONCURRENCY = [2, 4, 4, 4, 6, 8, 8, 8, 12, 16]
DEVICE_MEMORY        = [2, 4, 4, 8, 8, 8, 16]

# Realistic WebGL data — vendor/renderer/shading_lang/extensions all consistent
WEBGL_PROFILES = [
    {
        "vendor":   "Google Inc. (Intel)",
        "renderer": "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "shading":  "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
        "max_texture": 16384, "max_viewport": [32767, 32767], "aliased_line": [1, 1],
    },
    {
        "vendor":   "Google Inc. (NVIDIA)",
        "renderer": "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "shading":  "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
        "max_texture": 32768, "max_viewport": [32767, 32767], "aliased_line": [1, 1],
    },
    {
        "vendor":   "Google Inc. (NVIDIA)",
        "renderer": "ANGLE (NVIDIA, NVIDIA GeForce RTX 3060 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "shading":  "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
        "max_texture": 32768, "max_viewport": [32767, 32767], "aliased_line": [1, 1],
    },
    {
        "vendor":   "Google Inc. (AMD)",
        "renderer": "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "shading":  "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
        "max_texture": 16384, "max_viewport": [32767, 32767], "aliased_line": [1, 1],
    },
    {
        "vendor":   "Google Inc. (Intel)",
        "renderer": "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)",
        "shading":  "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
        "max_texture": 16384, "max_viewport": [32767, 32767], "aliased_line": [1, 1],
    },
    {
        "vendor":   "Apple Inc.",
        "renderer": "Apple GPU",
        "shading":  "WebGL GLSL ES 1.0 (OpenGL ES GLSL ES 1.0 Chromium)",
        "max_texture": 16384, "max_viewport": [16384, 16384], "aliased_line": [1, 1],
    },
]

# Realistic Chrome plugin sets per OS
PLUGIN_SETS = {
    "Windows": [
        [
            {"name": "PDF Viewer",              "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}, {"type": "text/pdf"}]},
            {"name": "Chrome PDF Viewer",        "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
            {"name": "Chromium PDF Viewer",      "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
            {"name": "Microsoft Edge PDF Viewer","filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
            {"name": "WebKit built-in PDF",      "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
        ],
        [
            {"name": "PDF Viewer",              "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
            {"name": "Chrome PDF Viewer",        "filename": "internal-pdf-viewer",     "description": "",                        "mimeTypes": [{"type": "application/pdf"}]},
        ],
    ],
    "Mac": [
        [
            {"name": "PDF Viewer",              "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}, {"type": "text/pdf"}]},
            {"name": "Chrome PDF Viewer",        "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
        ],
    ],
    "Linux": [
        [
            {"name": "PDF Viewer",              "filename": "internal-pdf-viewer",     "description": "Portable Document Format", "mimeTypes": [{"type": "application/pdf"}]},
        ],
    ],
}

# Realistic font sets per OS — mimics real installed fonts
FONT_SETS = {
    "Windows": [
        ["Arial", "Arial Black", "Calibri", "Cambria", "Comic Sans MS", "Courier New", "Georgia",
         "Impact", "Lucida Console", "Lucida Sans Unicode", "Microsoft Sans Serif", "Palatino Linotype",
         "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana", "Wingdings"],
        ["Arial", "Calibri", "Cambria", "Consolas", "Courier New", "Georgia", "Impact",
         "Segoe UI", "Tahoma", "Times New Roman", "Trebuchet MS", "Verdana"],
    ],
    "Mac": [
        ["Arial", "Arial Black", "Comic Sans MS", "Courier New", "Georgia", "Helvetica",
         "Helvetica Neue", "Impact", "Lucida Grande", "Monaco", "Palatino", "Times New Roman",
         "Trebuchet MS", "Verdana", "Menlo", "Optima", "Futura"],
        ["Arial", "Helvetica", "Helvetica Neue", "Times New Roman", "Courier New",
         "Georgia", "Verdana", "Menlo", "Monaco"],
    ],
    "Linux": [
        ["Arial", "Courier New", "DejaVu Sans", "DejaVu Serif", "FreeSerif", "Liberation Mono",
         "Liberation Sans", "Times New Roman", "Ubuntu", "Verdana"],
    ],
}

# Battery levels — realistic values (most laptops between 20-100%)
BATTERY_LEVELS    = [0.23, 0.45, 0.67, 0.78, 0.89, 0.92, 0.95, 1.0]
BATTERY_CHARGING  = [True, True, False, False, False, True]

# Connection types
CONNECTION_TYPES  = ["wifi", "wifi", "wifi", "ethernet", "4g"]
CONNECTION_DOWN   = [10, 50, 100, 100, 50, 25]   # Mbps downlink
CONNECTION_RTT    = [50, 50, 100, 100, 150, 200]  # ms


def generate_fingerprint(profile_name: str, vpn_city: str = "No VPN (Local)") -> dict:
    seed = int(hashlib.md5(profile_name.encode()).hexdigest()[:8], 16)
    rng  = random.Random(seed)

    ua_data    = rng.choice(USER_AGENTS)
    os_name    = ua_data["os"]
    browser    = ua_data["browser"]
    screen     = rng.choice(OS_SCREENS[os_name])
    webgl      = rng.choice(WEBGL_PROFILES)
    plugins    = rng.choice(PLUGIN_SETS.get(os_name, PLUGIN_SETS["Windows"]))
    fonts      = rng.choice(FONT_SETS.get(os_name, FONT_SETS["Windows"]))

    city_data  = VPN_CITIES.get(vpn_city, VPN_CITIES["No VPN (Local)"])
    timezone   = city_data["timezone"] or rng.choice([
        "America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London"])
    languages  = city_data["languages"]

    # Battery — desktops always charging at 1.0, laptops vary
    is_desktop = rng.random() < 0.4
    battery_level   = 1.0 if is_desktop else rng.choice(BATTERY_LEVELS)
    battery_charging = True if is_desktop else rng.choice(BATTERY_CHARGING)

    conn_idx = rng.randint(0, len(CONNECTION_TYPES) - 1)

    # Device pixel ratio — Mac retina = 2, most Windows = 1 or 1.25
    if os_name == "Mac":
        dpr = rng.choice([1.0, 2.0, 2.0])
    else:
        dpr = rng.choice([1.0, 1.0, 1.25, 1.5])

    return {
        # ── Identity ──────────────────────────────────────────────
        "profile_name":         profile_name,
        "vpn_city":             vpn_city,
        "vpn_flag":             city_data["flag"],
        "vpn_hint":             city_data["hint"],
        # ── Browser / OS ──────────────────────────────────────────
        "user_agent":           ua_data["ua"],
        "browser_type":         browser,
        "chrome_version":       ua_data.get("chrome_ver"),
        "os_name":              os_name,
        "platform":             OS_PLATFORM[os_name],
        # ── Screen ────────────────────────────────────────────────
        "screen_width":         screen[0],
        "screen_height":        screen[1],
        "color_depth":          rng.choice([24, 24, 32]),
        "device_pixel_ratio":   dpr,
        # ── Locale ────────────────────────────────────────────────
        "timezone":             timezone,
        "languages":            languages,
        # ── Hardware ──────────────────────────────────────────────
        "hardware_concurrency": rng.choice(HARDWARE_CONCURRENCY),
        "device_memory":        rng.choice(DEVICE_MEMORY),
        # ── WebGL ─────────────────────────────────────────────────
        "webgl_vendor":         webgl["vendor"],
        "webgl_renderer":       webgl["renderer"],
        "webgl_shading_lang":   webgl["shading"],
        "webgl_max_texture":    webgl["max_texture"],
        "webgl_max_viewport":   webgl["max_viewport"],
        # ── Noise Seeds ───────────────────────────────────────────
        "canvas_noise_seed":    rng.randint(1000, 9999),
        "audio_noise_seed":     rng.randint(1000, 9999),
        "webgl_noise_seed":     rng.randint(1000, 9999),
        # ── Plugins & Fonts ───────────────────────────────────────
        "plugins":              plugins,
        "fonts":                fonts,
        # ── Navigator ─────────────────────────────────────────────
        "do_not_track":         rng.choice([None, None, "1"]),
        "touch_points":         rng.choice([0, 0, 0, 1, 5]),
        "cookie_enabled":       True,
        "pdf_viewer_enabled":   rng.choice([True, True, False]),
        # ── Battery ───────────────────────────────────────────────
        "battery_level":        battery_level,
        "battery_charging":     battery_charging,
        # ── Network ───────────────────────────────────────────────
        "connection_type":      CONNECTION_TYPES[conn_idx],
        "connection_downlink":  CONNECTION_DOWN[conn_idx],
        "connection_rtt":       CONNECTION_RTT[conn_idx],
        # ── Misc ──────────────────────────────────────────────────
        "vendor_sub":           "",
        "product":              "Gecko",
        "product_sub":          "20030107" if browser == "chrome" else "20100101",
        "build_id":             None if browser == "chrome" else "20230112",
    }


def save_fingerprint(fp: dict, profiles_dir: str = "profiles"):
    Path(profiles_dir).mkdir(exist_ok=True)
    path = os.path.join(profiles_dir, f"{fp['profile_name']}.json")
    with open(path, "w") as f:
        json.dump(fp, f, indent=2)
    return path


def load_fingerprint(profile_name: str, profiles_dir: str = "profiles") -> dict:
    path = os.path.join(profiles_dir, f"{profile_name}.json")
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    fp = generate_fingerprint(profile_name)
    save_fingerprint(fp, profiles_dir)
    return fp


def assign_vpn_city(profile_name: str, vpn_city: str, profiles_dir: str = "profiles"):
    fp = load_fingerprint(profile_name, profiles_dir)
    city_data = VPN_CITIES.get(vpn_city, VPN_CITIES["No VPN (Local)"])
    fp["vpn_city"]  = vpn_city
    fp["vpn_flag"]  = city_data["flag"]
    fp["vpn_hint"]  = city_data["hint"]
    fp["languages"] = city_data["languages"]
    if city_data["timezone"]:
        fp["timezone"] = city_data["timezone"]
    save_fingerprint(fp, profiles_dir)
    return fp


def list_profiles(profiles_dir: str = "profiles") -> list:
    Path(profiles_dir).mkdir(exist_ok=True)
    return [f.stem for f in Path(profiles_dir).glob("*.json")]


if __name__ == "__main__":
    fp = generate_fingerprint("test_01", "London, UK")
    print(json.dumps(fp, indent=2))
