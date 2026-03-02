#!/usr/bin/env python3
"""
FB Profile Manager v2 - With VPN City Assignment
Manage 10+ Facebook profiles with unique fingerprints + VPN city reminders
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from fingerprint_engine import (
    generate_fingerprint, save_fingerprint, load_fingerprint,
    assign_vpn_city, list_profiles, VPN_CITIES
)

PROFILES_DIR = "profiles"

# ─── Colors ───────────────────────────────────────────────────────────────────
R  = "\033[31m"   # Red
G  = "\033[32m"   # Green
Y  = "\033[33m"   # Yellow
B  = "\033[36m"   # Cyan/Blue
W  = "\033[1m"    # Bold
DIM = "\033[2m"   # Dim
RST = "\033[0m"   # Reset
BG  = "\033[44m"  # Blue background

def cls():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print(f"""
{B}{W}╔══════════════════════════════════════════════════════════╗
║        FB PROFILE MANAGER v2  —  VPN Edition            ║
║     Unique Fingerprints + VPN City Reminders             ║
╚══════════════════════════════════════════════════════════╝{RST}
""")

def print_menu():
    print(f"""{W}
  ── Profile Management ──────────────────────────────
  {B}[1]{RST} List all profiles
  {B}[2]{RST} Create new profile
  {B}[3]{RST} Assign VPN city to profile       ← NEW
  {B}[4]{RST} Bulk assign VPN cities           ← NEW
  {B}[5]{RST} View profile fingerprint + VPN info

  ── Browser Launch ───────────────────────────────────
  {B}[6]{RST} Launch profile  {Y}(shows VPN reminder first){RST}
  {B}[7]{RST} Launch multiple profiles

  ── Profile Tools ────────────────────────────────────
  {B}[8]{RST} Bulk create profiles
  {B}[9]{RST} Delete profile
  {B}[10]{RST} Regenerate fingerprint

  {DIM}[0] Exit{RST}
""")

# ─── List Profiles ────────────────────────────────────────────────────────────

def list_profiles_display():
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found. Create one first!{RST}")
        return

    print(f"\n{W}  {'#':<4} {'Profile Name':<22} {'VPN City':<25} {'Timezone':<22} {'Screen'}{RST}")
    print("  " + "─" * 82)

    for i, name in enumerate(profiles, 1):
        fp = load_fingerprint(name, PROFILES_DIR)
        screen = f"{fp['screen_width']}x{fp['screen_height']}"
        tz = fp.get("timezone", "Unknown")
        city = fp.get("vpn_city", "No VPN (Local)")
        flag = fp.get("vpn_flag", "🖥️")
        city_display = f"{flag} {city}"
        print(f"  {B}{i:<4}{RST} {name:<22} {city_display:<28} {tz:<22} {screen}")

    print()

# ─── Create Profile ───────────────────────────────────────────────────────────

def pick_vpn_city(prompt="  Assign VPN city") -> str:
    """Show city picker and return chosen city name"""
    cities = list(VPN_CITIES.keys())
    
    print(f"\n{W}  Available VPN Cities:{RST}")
    
    # Group by region
    groups = {
        "🇺🇸 USA": [c for c in cities if "USA" in c],
        "🇬🇧 UK": [c for c in cities if "UK" in c],
        "🇨🇦 Canada": [c for c in cities if "Canada" in c],
        "🇦🇺 Australia": [c for c in cities if "Australia" in c],
        "🇪🇺 Europe": [c for c in cities if any(x in c for x in ["Germany","France","NL"])],
        "🌏 Asia": [c for c in cities if any(x in c for x in ["Singapore","Japan","India","UAE","Pakistan"])],
        "🌍 Other": [c for c in cities if any(x in c for x in ["Brazil","SA","Local"])],
    }
    
    all_cities = []
    for group, group_cities in groups.items():
        if group_cities:
            print(f"\n  {DIM}{group}{RST}")
            for c in group_cities:
                idx = len(all_cities) + 1
                data = VPN_CITIES[c]
                print(f"    {B}{idx:>2}{RST}. {data['flag']} {c}")
                all_cities.append(c)
    
    print()
    while True:
        try:
            choice = input(f"  {prompt} (number, or Enter to skip): ").strip()
            if choice == "":
                return "No VPN (Local)"
            idx = int(choice) - 1
            if 0 <= idx < len(all_cities):
                return all_cities[idx]
            print(f"{R}  Invalid number.{RST}")
        except ValueError:
            # Allow typing city name directly
            matches = [c for c in cities if choice.lower() in c.lower()]
            if len(matches) == 1:
                return matches[0]
            elif len(matches) > 1:
                print(f"  Multiple matches: {matches}")
            else:
                print(f"{R}  Not found. Try a number.{RST}")

def create_profile():
    name = input("  Profile name (e.g. fb_account_1): ").strip()
    if not name:
        print(f"{R}  Name cannot be empty.{RST}")
        return

    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if os.path.exists(path):
        print(f"{Y}  Profile '{name}' already exists.{RST}")
        return

    vpn_city = pick_vpn_city("Assign VPN city to this profile")
    fp = generate_fingerprint(name, vpn_city)
    save_fingerprint(fp, PROFILES_DIR)

    print(f"\n{G}  ✓ Profile '{name}' created!{RST}")
    print_profile_summary(fp)

def print_profile_summary(fp: dict):
    city = fp.get("vpn_city", "No VPN (Local)")
    flag = fp.get("vpn_flag", "🖥️")
    hint = fp.get("vpn_hint", "")
    print(f"    {flag} VPN City: {W}{city}{RST}")
    if hint and city != "No VPN (Local)":
        print(f"    {DIM}    → In your VPN app: {hint}{RST}")
    print(f"    Timezone:  {fp['timezone']}")
    print(f"    Screen:    {fp['screen_width']}x{fp['screen_height']}")
    print(f"    Platform:  {fp['platform']}")
    print(f"    Languages: {', '.join(fp['languages'])}")

# ─── Assign VPN City ──────────────────────────────────────────────────────────

def assign_vpn_to_profile():
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found.{RST}")
        return

    list_profiles_display()
    name = input("  Profile name to update: ").strip()
    if name not in profiles:
        print(f"{R}  Profile '{name}' not found.{RST}")
        return

    vpn_city = pick_vpn_city(f"New VPN city for '{name}'")
    fp = assign_vpn_city(name, vpn_city, PROFILES_DIR)

    print(f"\n{G}  ✓ Updated '{name}'!{RST}")
    print_profile_summary(fp)

def bulk_assign_vpn():
    """Assign VPN cities to multiple profiles at once"""
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found.{RST}")
        return

    cities = [c for c in VPN_CITIES.keys() if c != "No VPN (Local)"]
    
    print(f"\n{W}  Bulk VPN City Assignment{RST}")
    print(f"  You have {len(profiles)} profiles and {len(cities)} cities available.")
    print(f"\n{Y}  Modes:{RST}")
    print(f"  {B}[1]{RST} Auto-assign (spread profiles across different cities)")
    print(f"  {B}[2]{RST} Assign one city to selected profiles")
    print(f"  {B}[3]{RST} Assign manually one by one")
    
    mode = input("\n  Mode: ").strip()
    
    if mode == "1":
        # Spread profiles across cities
        for i, name in enumerate(profiles):
            city = cities[i % len(cities)]
            fp = assign_vpn_city(name, city, PROFILES_DIR)
            print(f"  {G}✓{RST} {name:<25} → {fp['vpn_flag']} {city}")
        print(f"\n{G}  Done! {len(profiles)} profiles assigned.{RST}")

    elif mode == "2":
        vpn_city = pick_vpn_city("City to assign to all selected profiles")
        names_input = input("  Profile names (comma separated, or 'all'): ").strip()
        
        if names_input.lower() == "all":
            targets = profiles
        else:
            targets = [n.strip() for n in names_input.split(",") if n.strip() in profiles]
        
        for name in targets:
            assign_vpn_city(name, vpn_city, PROFILES_DIR)
            data = VPN_CITIES[vpn_city]
            print(f"  {G}✓{RST} {name} → {data['flag']} {vpn_city}")
        print(f"\n{G}  Done! {len(targets)} profiles updated.{RST}")

    elif mode == "3":
        for name in profiles:
            fp = load_fingerprint(name, PROFILES_DIR)
            current = fp.get("vpn_city", "No VPN (Local)")
            print(f"\n  Profile: {W}{name}{RST} (current: {current})")
            vpn_city = pick_vpn_city("New city (Enter to keep current)")
            if vpn_city != "No VPN (Local)" or current == "No VPN (Local)":
                assign_vpn_city(name, vpn_city, PROFILES_DIR)
                data = VPN_CITIES[vpn_city]
                print(f"  {G}✓{RST} Set to {data['flag']} {vpn_city}")

# ─── View Profile ─────────────────────────────────────────────────────────────

def view_fingerprint():
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found.{RST}")
        return

    list_profiles_display()
    name = input("  Profile name: ").strip()
    path = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(path):
        print(f"{R}  Profile '{name}' not found.{RST}")
        return

    fp = load_fingerprint(name, PROFILES_DIR)
    city = fp.get("vpn_city", "No VPN (Local)")
    flag = fp.get("vpn_flag", "🖥️")
    hint = fp.get("vpn_hint", "")

    print(f"\n{W}  ── VPN Info ─────────────────────────────────────────{RST}")
    print(f"  {flag}  City:    {W}{city}{RST}")
    if hint:
        print(f"       Hint:    {Y}{hint}{RST}")
    print(f"       Timezone: {fp['timezone']}")
    print(f"       Language: {', '.join(fp['languages'])}")

    print(f"\n{W}  ── Browser Fingerprint ──────────────────────────────{RST}")
    skip = {"vpn_city", "vpn_flag", "vpn_hint", "profile_name", "timezone", "languages"}
    for key, val in fp.items():
        if key in skip:
            continue
        print(f"  {B}{key:<25}{RST} {val}")
    print()

# ─── VPN Reminder Before Launch ───────────────────────────────────────────────

def show_vpn_reminder(fp: dict) -> bool:
    """Show VPN setup reminder. Returns True if user confirms ready."""
    city = fp.get("vpn_city", "No VPN (Local)")
    flag = fp.get("vpn_flag", "🖥️")
    hint = fp.get("vpn_hint", "")

    print(f"\n{'═'*58}")
    print(f"  {W}Profile:{RST} {fp['profile_name']}")
    print(f"{'═'*58}")

    if city == "No VPN (Local)":
        print(f"\n  {flag}  {W}No VPN required{RST} for this profile.")
        print(f"  This profile uses your local IP.")
    else:
        print(f"\n  {BG}{W}  ⚠  VPN REQUIRED BEFORE CONTINUING  ⚠  {RST}")
        print(f"\n  {flag}  Connect VPN to:  {W}{city}{RST}")
        print(f"\n  {Y}How to find it in your VPN app:{RST}")
        print(f"  → {hint}")
        print(f"\n  {DIM}Browser timezone will be: {fp['timezone']}{RST}")
        print(f"  {DIM}Browser language will be: {', '.join(fp['languages'])}{RST}")
        print(f"\n  {R}⚠  Do NOT launch until VPN is connected to {city}!{RST}")

    print()
    ans = input(f"  Ready? Press Enter to launch, or 'n' to cancel: ").strip().lower()
    return ans != "n"

def launch_profile_cli():
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found.{RST}")
        return

    list_profiles_display()
    name = input("  Profile name to launch: ").strip()
    if name not in profiles:
        print(f"{R}  Profile '{name}' not found.{RST}")
        return

    fp = load_fingerprint(name, PROFILES_DIR)
    
    if not show_vpn_reminder(fp):
        print(f"{Y}  Launch cancelled.{RST}")
        return

    print(f"\n{G}  Launching {name}...{RST}")
    cmd = [sys.executable, "browser_launcher.py", name]
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print(f"\n{Y}  Browser closed.{RST}")

def launch_multiple():
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found.{RST}")
        return

    list_profiles_display()
    names_input = input("  Profile names (comma separated): ").strip()
    names = [n.strip() for n in names_input.split(",")]
    valid = [n for n in names if n in profiles]

    if not valid:
        print(f"{R}  No valid profiles.{RST}")
        return

    # Show VPN reminders for all
    print(f"\n{W}  ── VPN Checklist ────────────────────────────────────{RST}")
    vpn_needed = {}
    for name in valid:
        fp = load_fingerprint(name, PROFILES_DIR)
        city = fp.get("vpn_city", "No VPN (Local)")
        flag = fp.get("vpn_flag", "🖥️")
        if city != "No VPN (Local)":
            vpn_needed[name] = fp
            print(f"  {R}⚠{RST}  {name:<22} → {flag} {city}")
        else:
            print(f"  {G}✓{RST}  {name:<22} → 🖥️  No VPN needed")

    if vpn_needed:
        print(f"\n  {Y}⚠  IMPORTANT: You can only use ONE VPN city at a time!{RST}")
        print(f"  Profiles needing VPN MUST be launched one at a time.")
        print(f"  Only launch multiple profiles if they ALL use 'No VPN'.")
        print()
        
        # Check if all have same city
        cities = set(fp.get("vpn_city") for fp in vpn_needed.values())
        if len(cities) > 1:
            print(f"  {R}✗ These profiles have DIFFERENT VPN cities — cannot run simultaneously!{RST}")
            print(f"  Cities: {cities}")
            print(f"  Launch them one at a time instead.")
            return
        elif len(cities) == 1:
            city = list(cities)[0]
            print(f"  All VPN profiles use same city: {city}")
            print(f"  Make sure your VPN is connected to {city} before continuing.")

    ans = input("\n  All VPNs ready? Press Enter to launch all, or 'n' to cancel: ").strip().lower()
    if ans == "n":
        print(f"{Y}  Cancelled.{RST}")
        return

    procs = []
    for name in valid:
        cmd = [sys.executable, "browser_launcher.py", name]
        p = subprocess.Popen(cmd)
        procs.append(p)
        print(f"  {G}✓{RST} Launched: {name} (PID: {p.pid})")

    print(f"\n  All {len(valid)} browsers running!")
    input("  Press Enter to return to menu...")

# ─── Other Tools ──────────────────────────────────────────────────────────────

def bulk_create_profiles():
    print(f"\n  {W}Bulk Profile Creator{RST}")
    base_name = input("  Base name (e.g. 'fb'): ").strip() or "profile"
    try:
        count = int(input("  How many profiles: ").strip())
    except ValueError:
        print(f"{R}  Invalid number.{RST}")
        return

    auto_assign = input("  Auto-assign VPN cities? (y/n): ").strip().lower() == "y"
    cities = [c for c in VPN_CITIES.keys() if c != "No VPN (Local)"]
    existing = list_profiles(PROFILES_DIR)
    created = 0

    for i in range(1, count + 1):
        name = f"{base_name}_{i:02d}"
        if name in existing:
            print(f"  {Y}Skipping {name} (already exists){RST}")
            continue
        city = cities[(i - 1) % len(cities)] if auto_assign else "No VPN (Local)"
        fp = generate_fingerprint(name, city)
        save_fingerprint(fp, PROFILES_DIR)
        created += 1
        flag = fp.get("vpn_flag", "🖥️")
        print(f"  {G}✓{RST} {name:<20} {flag} {city:<25} {fp['timezone']}")

    print(f"\n{G}  Created {created} profiles!{RST}")

def delete_profile():
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found.{RST}")
        return

    list_profiles_display()
    name = input("  Profile name to delete: ").strip()
    profile_json = os.path.join(PROFILES_DIR, f"{name}.json")
    if not os.path.exists(profile_json):
        print(f"{R}  Profile '{name}' not found.{RST}")
        return

    confirm = input(f"  Delete '{name}' + browser data? (yes/no): ").strip()
    if confirm.lower() != "yes":
        print("  Cancelled.")
        return

    import shutil
    os.remove(profile_json)
    browser_data = os.path.join(PROFILES_DIR, f"browser_data_{name}")
    if os.path.exists(browser_data):
        shutil.rmtree(browser_data)
    print(f"{G}  ✓ Deleted '{name}'.{RST}")

def regenerate_fingerprint():
    profiles = list_profiles(PROFILES_DIR)
    if not profiles:
        print(f"{Y}  No profiles found.{RST}")
        return

    list_profiles_display()
    name = input("  Profile name to regenerate: ").strip()
    if name not in profiles:
        print(f"{R}  Profile '{name}' not found.{RST}")
        return

    import random
    old_fp = load_fingerprint(name, PROFILES_DIR)
    old_city = old_fp.get("vpn_city", "No VPN (Local)")
    
    new_seed_name = f"{name}_{random.randint(100, 999)}"
    fp = generate_fingerprint(new_seed_name, old_city)
    fp["profile_name"] = name
    save_fingerprint(fp, PROFILES_DIR)
    print(f"{G}  ✓ Fingerprint regenerated for '{name}' (VPN city kept: {old_city}){RST}")

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    Path(PROFILES_DIR).mkdir(exist_ok=True)
    print_banner()

    try:
        from playwright.async_api import async_playwright
    except ImportError:
        print(f"{R}  ⚠ Playwright not installed!{RST}")
        print("  Run: pip install playwright && playwright install chromium\n")

    while True:
        print_menu()
        choice = input("  Choice: ").strip()
        print()

        if choice == "0":
            print("  Goodbye!\n")
            break
        elif choice == "1":
            list_profiles_display()
        elif choice == "2":
            create_profile()
        elif choice == "3":
            assign_vpn_to_profile()
        elif choice == "4":
            bulk_assign_vpn()
        elif choice == "5":
            view_fingerprint()
        elif choice == "6":
            launch_profile_cli()
        elif choice == "7":
            launch_multiple()
        elif choice == "8":
            bulk_create_profiles()
        elif choice == "9":
            delete_profile()
        elif choice == "10":
            regenerate_fingerprint()
        else:
            print(f"{R}  Invalid choice.{RST}")
        print()

if __name__ == "__main__":
    main()
