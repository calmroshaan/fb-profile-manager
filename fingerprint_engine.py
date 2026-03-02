"""
Fingerprint Engine - Generates realistic, unique browser fingerprints
Each profile gets a consistent identity + optional VPN city assignment
"""

import json
import random
import hashlib
import os
from pathlib import Path

# ─── VPN City → Timezone + Language mapping ──────────────────────────────────
# Format: "Display Name": { timezone, languages, country_code, vpn_search_hint }

VPN_CITIES = {
    # 🇺🇸 United States
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
    # 🇬🇧 United Kingdom
    "London, UK":           {"timezone": "Europe/London",       "languages": ["en-GB", "en"], "flag": "🇬🇧", "hint": "Search 'United Kingdom' → London"},
    "Manchester, UK":       {"timezone": "Europe/London",       "languages": ["en-GB", "en"], "flag": "🇬🇧", "hint": "Search 'United Kingdom' → Manchester"},
    # 🇨🇦 Canada
    "Toronto, Canada":      {"timezone": "America/Toronto",     "languages": ["en-CA", "en"], "flag": "🇨🇦", "hint": "Search 'Canada' → Toronto"},
    "Vancouver, Canada":    {"timezone": "America/Vancouver",   "languages": ["en-CA", "en"], "flag": "🇨🇦", "hint": "Search 'Canada' → Vancouver"},
    "Montreal, Canada":     {"timezone": "America/Toronto",     "languages": ["en-CA", "fr-CA", "en"], "flag": "🇨🇦", "hint": "Search 'Canada' → Montreal"},
    # 🇦🇺 Australia
    "Sydney, Australia":    {"timezone": "Australia/Sydney",    "languages": ["en-AU", "en"], "flag": "🇦🇺", "hint": "Search 'Australia' → Sydney"},
    "Melbourne, Australia": {"timezone": "Australia/Melbourne", "languages": ["en-AU", "en"], "flag": "🇦🇺", "hint": "Search 'Australia' → Melbourne"},
    # 🇩🇪 Germany
    "Frankfurt, Germany":   {"timezone": "Europe/Berlin",       "languages": ["de-DE", "de", "en"], "flag": "🇩🇪", "hint": "Search 'Germany' → Frankfurt"},
    "Berlin, Germany":      {"timezone": "Europe/Berlin",       "languages": ["de-DE", "de", "en"], "flag": "🇩🇪", "hint": "Search 'Germany' → Berlin"},
    # 🇫🇷 France
    "Paris, France":        {"timezone": "Europe/Paris",        "languages": ["fr-FR", "fr", "en"], "flag": "🇫🇷", "hint": "Search 'France' → Paris"},
    # 🇳🇱 Netherlands
    "Amsterdam, NL":        {"timezone": "Europe/Amsterdam",    "languages": ["nl-NL", "en"], "flag": "🇳🇱", "hint": "Search 'Netherlands' → Amsterdam"},
    # 🇸🇬 Singapore
    "Singapore":            {"timezone": "Asia/Singapore",      "languages": ["en-SG", "en"], "flag": "🇸🇬", "hint": "Search 'Singapore'"},
    # 🇯🇵 Japan
    "Tokyo, Japan":         {"timezone": "Asia/Tokyo",          "languages": ["ja-JP", "ja", "en"], "flag": "🇯🇵", "hint": "Search 'Japan' → Tokyo"},
    # 🇮🇳 India
    "Mumbai, India":        {"timezone": "Asia/Kolkata",        "languages": ["en-IN", "en"], "flag": "🇮🇳", "hint": "Search 'India' → Mumbai"},
    "Delhi, India":         {"timezone": "Asia/Kolkata",        "languages": ["en-IN", "en"], "flag": "🇮🇳", "hint": "Search 'India' → Delhi"},
    # 🇧🇷 Brazil
    "Sao Paulo, Brazil":    {"timezone": "America/Sao_Paulo",   "languages": ["pt-BR", "pt", "en"], "flag": "🇧🇷", "hint": "Search 'Brazil' → Sao Paulo"},
    # 🇦🇪 UAE
    "Dubai, UAE":           {"timezone": "Asia/Dubai",          "languages": ["ar-AE", "en"], "flag": "🇦🇪", "hint": "Search 'UAE' → Dubai"},
    # 🇵🇰 Pakistan
    "Karachi, Pakistan":    {"timezone": "Asia/Karachi",        "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰", "hint": "Search 'Pakistan' → Karachi"},
    "Lahore, Pakistan":     {"timezone": "Asia/Karachi",        "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰", "hint": "Search 'Pakistan' → Lahore"},
    "Islamabad, Pakistan":  {"timezone": "Asia/Karachi",        "languages": ["en-PK", "ur", "en"], "flag": "🇵🇰", "hint": "Search 'Pakistan' → Islamabad"},
    # 🇿🇦 South Africa
    "Johannesburg, SA":     {"timezone": "Africa/Johannesburg", "languages": ["en-ZA", "en"], "flag": "🇿🇦", "hint": "Search 'South Africa' → Johannesburg"},
    # No VPN
    "No VPN (Local)":       {"timezone": None, "languages": ["en-US", "en"], "flag": "🖥️",  "hint": "Run without VPN — use real local IP"},
}

# ─── Other fingerprint data pools ─────────────────────────────────────────────

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_2_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

SCREEN_RESOLUTIONS = [
    (1920, 1080), (1920, 1080), (1920, 1080),
    (2560, 1440), (2560, 1440),
    (1366, 768), (1366, 768),
    (1440, 900), (1536, 864), (1280, 720),
    (3840, 2160), (2560, 1600), (1680, 1050),
]

PLATFORMS = ["Win32", "Win32", "Win32", "MacIntel", "Linux x86_64"]
HARDWARE_CONCURRENCY = [2, 4, 4, 4, 6, 8, 8, 8, 12, 16]
DEVICE_MEMORY = [2, 4, 4, 8, 8, 8, 16]

WEBGL_RENDERERS = [
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 620 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce GTX 1060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (NVIDIA)", "ANGLE (NVIDIA, NVIDIA GeForce RTX 2060 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (AMD)", "ANGLE (AMD, AMD Radeon RX 580 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) Iris(R) Xe Graphics Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Google Inc. (Intel)", "ANGLE (Intel, Intel(R) UHD Graphics 630 Direct3D11 vs_5_0 ps_5_0, D3D11)"),
    ("Apple Inc.", "Apple GPU"),
    ("Mesa/X.org", "Mesa Intel(R) UHD Graphics 620 (KBL GT2)"),
]

INSTALLED_FONTS = [
    ["Arial", "Verdana", "Times New Roman", "Courier New", "Georgia", "Palatino", "Garamond", "Bookman", "Comic Sans MS", "Trebuchet MS", "Arial Black", "Impact"],
    ["Arial", "Helvetica", "Times New Roman", "Courier", "Verdana", "Georgia", "Palatino", "Garamond", "Impact", "Comic Sans MS"],
    ["Segoe UI", "Arial", "Calibri", "Cambria", "Georgia", "Times New Roman", "Courier New", "Verdana", "Tahoma", "Trebuchet MS"],
    ["Helvetica Neue", "Arial", "Georgia", "Times New Roman", "Courier New", "Monaco", "Menlo", "Palatino"],
]


def generate_fingerprint(profile_name: str, vpn_city: str = "No VPN (Local)") -> dict:
    """Generate a complete, consistent fingerprint for a profile"""
    seed = int(hashlib.md5(profile_name.encode()).hexdigest()[:8], 16)
    rng = random.Random(seed)

    ua = rng.choice(USER_AGENTS)
    screen = rng.choice(SCREEN_RESOLUTIONS)
    webgl = rng.choice(WEBGL_RENDERERS)

    if "Firefox" in ua:
        browser_type = "firefox"
    elif "Edg/" in ua:
        browser_type = "edge"
    else:
        browser_type = "chrome"

    city_data = VPN_CITIES.get(vpn_city, VPN_CITIES["No VPN (Local)"])
    timezone = city_data["timezone"] if city_data["timezone"] else rng.choice([
        "America/New_York", "America/Chicago", "America/Los_Angeles",
        "Europe/London", "Asia/Singapore", "Australia/Sydney"
    ])
    languages = city_data["languages"]

    return {
        "profile_name": profile_name,
        "vpn_city": vpn_city,
        "vpn_flag": city_data["flag"],
        "vpn_hint": city_data["hint"],
        "user_agent": ua,
        "browser_type": browser_type,
        "screen_width": screen[0],
        "screen_height": screen[1],
        "color_depth": rng.choice([24, 24, 24, 32]),
        "timezone": timezone,
        "languages": languages,
        "platform": rng.choice(PLATFORMS),
        "hardware_concurrency": rng.choice(HARDWARE_CONCURRENCY),
        "device_memory": rng.choice(DEVICE_MEMORY),
        "webgl_vendor": webgl[0],
        "webgl_renderer": webgl[1],
        "canvas_noise_seed": rng.randint(1000, 9999),
        "audio_noise_seed": rng.randint(1000, 9999),
        "fonts": rng.choice(INSTALLED_FONTS),
        "do_not_track": rng.choice([None, "1"]),
        "touch_points": rng.choice([0, 0, 0, 1, 5]),
        "cookie_enabled": True,
        "pdf_viewer_enabled": rng.choice([True, True, False]),
        "plugins_count": rng.randint(0, 5),
    }


def save_fingerprint(fingerprint: dict, profiles_dir: str = "profiles"):
    Path(profiles_dir).mkdir(exist_ok=True)
    path = os.path.join(profiles_dir, f"{fingerprint['profile_name']}.json")
    with open(path, "w") as f:
        json.dump(fingerprint, f, indent=2)
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
    """Assign / update VPN city for an existing profile — auto-updates timezone & language"""
    fp = load_fingerprint(profile_name, profiles_dir)
    city_data = VPN_CITIES.get(vpn_city, VPN_CITIES["No VPN (Local)"])
    fp["vpn_city"] = vpn_city
    fp["vpn_flag"] = city_data["flag"]
    fp["vpn_hint"] = city_data["hint"]
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
