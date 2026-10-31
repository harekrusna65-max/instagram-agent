"""
Interactive Direct Terminal Login (No Browser Needed)
Supports Username, Password, and 2FA / SMS / Email OTP challenge.
"""

import sys
import getpass
import json
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt

# UTF-8 on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()
SESSION_FILE = Path("instagrapi_session.json")
RAW_SESSION_FILE = Path("session.json")

def direct_login():
    console.print("\n[bold cyan]==================================================[/bold cyan]")
    console.print("[bold yellow]       INSTAGRAM DIRECT TERMINAL LOGIN[/bold yellow]")
    console.print("[bold cyan]==================================================[/bold cyan]\n")

    from core.client import InstagramAgentClient
    client = InstagramAgentClient()

    username = Prompt.ask("[bold white]Instagram Username[/bold white]", default="stanger.man69")
    password = Prompt.ask("[bold white]Instagram Password[/bold white]", password=True)

    console.print("\n[dim]Connecting to Instagram servers securely...[/dim]")

    try:
        res = client.cl.login(username, password)
        if res:
            console.print(f"\n[bold green]✓ Login Successful as @{username}![/bold green]")
            client.cl.dump_settings(str(SESSION_FILE))
            
            # Extract session data for raw session
            settings = client.cl.get_settings()
            cookie_dict = {}
            for k, v in settings.get("cookies", {}).items():
                cookie_dict[k] = v
            
            with open(RAW_SESSION_FILE, "w", encoding="utf-8") as f:
                json.dump({
                    "sessionid": cookie_dict.get("sessionid"),
                    "ds_user_id": client.cl.user_id,
                    "csrftoken": cookie_dict.get("csrftoken"),
                    "username": username
                }, f, indent=2)

            console.print(f"[bold green]✓ Session successfully saved to `{SESSION_FILE}`![/bold green]\n")
            return True
    except Exception as e:
        err_msg = str(e)
        if "two_factor_required" in err_msg.lower() or "challenge" in err_msg.lower():
            console.print("\n[bold yellow]⚠️ 2-Factor Authentication (OTP) Required![/bold yellow]")
            code = Prompt.ask("[bold cyan]Enter the 6-digit 2FA/SMS code sent to your phone/app[/bold cyan]")
            try:
                client.cl.login_by_2fa(code)
                client.cl.dump_settings(str(SESSION_FILE))
                console.print(f"\n[bold green]✓ 2FA Verified & Login Successful as @{username}![/bold green]")
                return True
            except Exception as e2:
                console.print(f"\n[bold red]❌ 2FA Verification Failed: {e2}[/bold red]")
                return False
        else:
            console.print(f"\n[bold red]❌ Login Error: {err_msg}[/bold red]")
            return False

if __name__ == "__main__":
    success = direct_login()
    sys.exit(0 if success else 1)
