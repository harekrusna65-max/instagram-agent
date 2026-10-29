"""
Interactive Instagram Login Helper
Opens official Instagram login in a real browser on your desktop.
Once you log in, it automatically captures and saves your session locally to `session.json`.
"""

import sys
import json
import time
from pathlib import Path
from playwright.sync_api import sync_playwright
from rich.console import Console

console = Console()

SESSION_FILE = Path("session.json")
COOKIES_FILE = Path("cookies.json")

def login_and_save_session():
    console.print("\n[bold cyan]==================================================[/bold cyan]")
    console.print("[bold yellow]       INSTAGRAM SECURE BROWSER LOGIN[/bold yellow]")
    console.print("[bold cyan]==================================================[/bold cyan]\n")
    console.print("[white]Aapke screen par ek browser window khulegi official Instagram login page ke sath.[/white]")
    console.print("[green]1. Wahan apna username (@stranger.man69) aur password daliye.[/green]")
    console.print("[green]2. Agar 2FA / OTP code maange toh daal kar login complete kijiye.[/green]")
    console.print("[cyan]3. Jaise hi login ho jayega, ye script automatically session save kar legi.[/cyan]\n")

    with sync_playwright() as p:
        # Launch installed Google Chrome or Edge directly
        try:
            browser = p.chromium.launch(headless=False, channel="chrome")
        except Exception:
            try:
                browser = p.chromium.launch(headless=False, channel="msedge")
            except Exception:
                browser = p.chromium.launch(headless=False, executable_path=r"C:\Program Files\Google\Chrome\Application\chrome.exe")
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()

        console.print("[bold blue]Opening Instagram Login Page...[/bold blue]")
        page.goto("https://www.instagram.com/accounts/login/")

        console.print("[bold green]Browser khul chuka hai! Please Instagram me login kijiye...[/bold green]")
        console.print("[dim](Waiting for successful login...)[/dim]\n")

        # Wait until user is logged in (url no longer contains /accounts/login/ or session cookie appears)
        logged_in = False
        start_time = time.time()
        timeout = 300  # 5 minutes to log in

        while time.time() - start_time < timeout:
            cookies = context.cookies()
            cookie_dict = {c["name"]: c["value"] for c in cookies}

            # Instagram sessionid cookie indicates successful login
            if "sessionid" in cookie_dict and "ds_user_id" in cookie_dict:
                logged_in = True
                console.print("\n[bold green]✓ Login Detected Successfully![/bold green]")
                break
            
            # Check URL change
            current_url = page.url
            if "instagram.com" in current_url and "/accounts/login" not in current_url and "two_factor" not in current_url:
                if "sessionid" in cookie_dict:
                    logged_in = True
                    console.print("\n[bold green]✓ Login Detected Successfully via URL & Cookie![/bold green]")
                    break

            time.sleep(2)

        if not logged_in:
            console.print("[bold red]❌ Login timeout or not completed.[/bold red]")
            browser.close()
            return False

        # Save cookies
        all_cookies = context.cookies()
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(all_cookies, f, indent=2)

        # Also format for instagrapi session
        cookie_dict = {c["name"]: c["value"] for c in all_cookies}
        session_data = {
            "sessionid": cookie_dict.get("sessionid"),
            "ds_user_id": cookie_dict.get("ds_user_id"),
            "csrftoken": cookie_dict.get("csrftoken"),
            "mid": cookie_dict.get("mid"),
            "ig_did": cookie_dict.get("ig_did"),
            "all_cookies": cookie_dict
        }

        with open(SESSION_FILE, "w", encoding="utf-8") as f:
            json.dump(session_data, f, indent=2)

        console.print(f"[bold green]✓ Session successfully saved to `{SESSION_FILE}`![/bold green]")
        console.print("[bold cyan]Ab aapka Instagram Agent bina dobara password maange kaam kar sakta hai.[/bold cyan]\n")
        
        # Give a moment then close
        time.sleep(3)
        browser.close()
        return True

if __name__ == "__main__":
    success = login_and_save_session()
    sys.exit(0 if success else 1)
