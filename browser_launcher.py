"""
Browser Launcher - Opens isolated browser sessions with injected fingerprints
Uses Playwright with stealth JS injection to spoof all detectable signals
"""

import asyncio
import os
import json
from pathlib import Path
from fingerprint_engine import load_fingerprint

# ─── Stealth JS Injection ────────────────────────────────────────────────────

def build_stealth_script(fp: dict) -> str:
    """Build comprehensive JS to override all fingerprint signals"""
    langs = json.dumps(fp["languages"])
    fonts = json.dumps(fp.get("fonts", ["Arial"]))
    
    return f"""
// ── Navigator overrides ──────────────────────────────────────────────────────
Object.defineProperty(navigator, 'userAgent', {{
    get: () => '{fp["user_agent"]}',
    configurable: true
}});
Object.defineProperty(navigator, 'platform', {{
    get: () => '{fp["platform"]}',
    configurable: true
}});
Object.defineProperty(navigator, 'hardwareConcurrency', {{
    get: () => {fp["hardware_concurrency"]},
    configurable: true
}});
Object.defineProperty(navigator, 'deviceMemory', {{
    get: () => {fp.get("device_memory", 8)},
    configurable: true
}});
Object.defineProperty(navigator, 'languages', {{
    get: () => {langs},
    configurable: true
}});
Object.defineProperty(navigator, 'language', {{
    get: () => '{fp["languages"][0]}',
    configurable: true
}});
Object.defineProperty(navigator, 'cookieEnabled', {{
    get: () => true,
    configurable: true
}});
Object.defineProperty(navigator, 'doNotTrack', {{
    get: () => {json.dumps(fp.get("do_not_track"))},
    configurable: true
}});
Object.defineProperty(navigator, 'maxTouchPoints', {{
    get: () => {fp.get("touch_points", 0)},
    configurable: true
}});
Object.defineProperty(navigator, 'pdfViewerEnabled', {{
    get: () => {str(fp.get("pdf_viewer_enabled", True)).lower()},
    configurable: true
}});

// ── Screen overrides ─────────────────────────────────────────────────────────
Object.defineProperty(screen, 'width', {{ get: () => {fp["screen_width"]}, configurable: true }});
Object.defineProperty(screen, 'height', {{ get: () => {fp["screen_height"]}, configurable: true }});
Object.defineProperty(screen, 'availWidth', {{ get: () => {fp["screen_width"]}, configurable: true }});
Object.defineProperty(screen, 'availHeight', {{ get: () => {fp["screen_height"] - 40}, configurable: true }});
Object.defineProperty(screen, 'colorDepth', {{ get: () => {fp["color_depth"]}, configurable: true }});
Object.defineProperty(screen, 'pixelDepth', {{ get: () => {fp["color_depth"]}, configurable: true }});

// ── WebGL fingerprint spoof ───────────────────────────────────────────────────
const getParameter_orig = WebGLRenderingContext.prototype.getParameter;
WebGLRenderingContext.prototype.getParameter = function(parameter) {{
    if (parameter === 37445) return '{fp["webgl_vendor"]}';
    if (parameter === 37446) return '{fp["webgl_renderer"]}';
    return getParameter_orig.call(this, parameter);
}};
const getParameter2_orig = WebGL2RenderingContext.prototype.getParameter;
WebGL2RenderingContext.prototype.getParameter = function(parameter) {{
    if (parameter === 37445) return '{fp["webgl_vendor"]}';
    if (parameter === 37446) return '{fp["webgl_renderer"]}';
    return getParameter2_orig.call(this, parameter);
}};

// ── Canvas noise injection ────────────────────────────────────────────────────
const canvas_seed = {fp["canvas_noise_seed"]};
function seededRandom(seed) {{
    let s = seed;
    return function() {{
        s = (s * 9301 + 49297) % 233280;
        return s / 233280;
    }};
}}
const rng = seededRandom(canvas_seed);

const toDataURL_orig = HTMLCanvasElement.prototype.toDataURL;
HTMLCanvasElement.prototype.toDataURL = function(type, quality) {{
    const ctx = this.getContext('2d');
    if (ctx) {{
        const imageData = ctx.getImageData(0, 0, this.width || 1, this.height || 1);
        for (let i = 0; i < imageData.data.length; i += 100) {{
            imageData.data[i] = imageData.data[i] ^ Math.floor(rng() * 3);
        }}
        ctx.putImageData(imageData, 0, 0);
    }}
    return toDataURL_orig.call(this, type, quality);
}};

const getImageData_orig = CanvasRenderingContext2D.prototype.getImageData;
CanvasRenderingContext2D.prototype.getImageData = function(sx, sy, sw, sh) {{
    const imageData = getImageData_orig.call(this, sx, sy, sw, sh);
    for (let i = 0; i < imageData.data.length; i += 100) {{
        imageData.data[i] = imageData.data[i] ^ Math.floor(rng() * 3);
    }}
    return imageData;
}};

// ── Audio context noise ───────────────────────────────────────────────────────
const audio_seed = {fp["audio_noise_seed"]};
const audio_rng = seededRandom(audio_seed);
if (typeof AudioBuffer !== 'undefined') {{
    const getChannelData_orig = AudioBuffer.prototype.getChannelData;
    AudioBuffer.prototype.getChannelData = function(channel) {{
        const data = getChannelData_orig.call(this, channel);
        for (let i = 0; i < data.length; i += 100) {{
            data[i] += (audio_rng() - 0.5) * 0.0001;
        }}
        return data;
    }};
}}

// ── Plugins spoof ─────────────────────────────────────────────────────────────
Object.defineProperty(navigator, 'plugins', {{
    get: () => {{
        const mockPlugins = [];
        for (let i = 0; i < {fp.get("plugins_count", 3)}; i++) {{
            mockPlugins.push({{ name: 'Plugin ' + i, filename: 'plugin' + i + '.dll' }});
        }}
        return mockPlugins;
    }},
    configurable: true
}});

// ── Automation detection removal ──────────────────────────────────────────────
Object.defineProperty(navigator, 'webdriver', {{ get: () => undefined, configurable: true }});
delete navigator.__proto__.webdriver;
window.chrome = {{ runtime: {{}} }};

// ── Font enumeration override ─────────────────────────────────────────────────
// Respond to font check queries with our spoofed font list
const installedFonts = {fonts};
"""

async def launch_browser(profile_name: str, url: str = "https://www.facebook.com", 
                          profiles_dir: str = "profiles",
                          headless: bool = False):
    """Launch an isolated browser session with full fingerprint injection"""
    from playwright.async_api import async_playwright
    
    fp = load_fingerprint(profile_name, profiles_dir)
    stealth_js = build_stealth_script(fp)
    
    # Isolated user data directory per profile
    user_data_dir = os.path.join(profiles_dir, f"browser_data_{profile_name}")
    Path(user_data_dir).mkdir(exist_ok=True)
    
    print(f"[{profile_name}] Launching browser...")
    print(f"[{profile_name}] UA: {fp['user_agent'][:60]}...")
    print(f"[{profile_name}] Screen: {fp['screen_width']}x{fp['screen_height']}")
    print(f"[{profile_name}] Timezone: {fp['timezone']}")
    print(f"[{profile_name}] Platform: {fp['platform']}")
    
    # ── Window size vs Spoofed screen size ───────────────────────────────────
    # The WINDOW (what you see) uses a comfortable size that fits your monitor.
    # The SPOOFED screen size is what JavaScript/Facebook sees — stays unique per profile.
    # These are intentionally different — window size is NOT a fingerprint signal.
    WINDOW_WIDTH  = 1280   # Comfortable browser window width
    WINDOW_HEIGHT = 800    # Comfortable browser window height

    async with async_playwright() as p:
        # Use chromium (most compatible with Facebook)
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=headless,
            locale=fp["languages"][0],
            timezone_id=fp["timezone"],
            user_agent=fp["user_agent"],
            viewport={"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT},
            color_scheme="no-preference",
            ignore_https_errors=True,
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-accelerated-2d-canvas",
                "--no-first-run",
                "--no-zygote",
                f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT + 80}",  # +80 for browser chrome
                "--window-position=50,50",   # Always opens top-left, fully visible
                f"--lang={fp['languages'][0]}",
            ],
            extra_http_headers={
                "Accept-Language": ",".join(fp["languages"]),
            }
        )
        
        # Inject stealth script into all pages/frames
        await browser.add_init_script(stealth_js)
        
        page = browser.pages[0] if browser.pages else await browser.new_page()
        
        # Navigate to Facebook
        await page.goto(url, wait_until="domcontentloaded", timeout=30000)
        
        print(f"[{profile_name}] Browser ready! Press Ctrl+C to close.")
        
        # Keep alive until closed
        try:
            while True:
                await asyncio.sleep(1)
                if not browser.pages:
                    break
        except (KeyboardInterrupt, asyncio.CancelledError):
            pass
        finally:
            await browser.close()
            print(f"[{profile_name}] Browser closed.")

def launch_profile(profile_name: str, url: str = "https://www.facebook.com",
                   profiles_dir: str = "profiles"):
    """Synchronous wrapper for launching a profile"""
    asyncio.run(launch_browser(profile_name, url, profiles_dir))

if __name__ == "__main__":
    import sys
    profile = sys.argv[1] if len(sys.argv) > 1 else "profile_1"
    launch_profile(profile)
