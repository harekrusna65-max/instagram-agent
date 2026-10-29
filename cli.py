"""
Interactive CLI for Instagram Agent (@stanger.man69)
"""

import sys
import os
import time
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm

# Force UTF-8 on Windows
if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

console = Console()

from database.db import init_db, get_active_rules, add_keyword_rule
from core.client import InstagramAgentClient
from services.ai_generator import AIGenerator
from services.post_service import PostService
from services.engagement_service import EngagementService
from services.analytics_service import AnalyticsService
from services.auto_content_pipeline import AutoContentPipeline

def print_banner():
    console.print(Panel(
        "[bold cyan]🤖 INSTAGRAM AI AGENT CONTROLLER[/bold cyan]\n"
        "[dim]Automated Growth, Content Scheduling & Smart Engagement for @stanger.man69[/dim]",
        border_style="cyan"
    ))

def view_profile_and_stats(analytics: AnalyticsService):
    with console.status("[cyan]Fetching live Instagram data...[/cyan]"):
        try:
            data = analytics.get_summary()
        except Exception as e:
            console.print(f"[red]Error fetching profile:[/red] {e}")
            return

    prof = data["profile"]
    metrics = data["metrics"]

    table = Table(title=f"Account Overview: @{prof['username']}", border_style="yellow")
    table.add_column("Property", style="bold white")
    table.add_column("Value", style="green")

    table.add_row("Full Name", str(prof.get("full_name")))
    table.add_row("Followers", str(prof.get("follower_count")))
    table.add_row("Following", str(prof.get("following_count")))
    table.add_row("Total Media", str(prof.get("media_count")))
    table.add_row("Avg Likes (Recent)", str(metrics["avg_likes"]))
    table.add_row("Avg Comments (Recent)", str(metrics["avg_comments"]))
    table.add_row("Est. Engagement Rate", str(metrics["est_engagement_rate"]))
    console.print(table)

    if data["recent_posts"]:
        post_table = Table(title="Recent Posts Performance", border_style="blue")
        post_table.add_column("Type", style="cyan")
        post_table.add_column("Likes", style="magenta")
        post_table.add_column("Comments", style="yellow")
        post_table.add_column("Post Link", style="blue")

        for p in data["recent_posts"][:5]:
            post_table.add_row(p["type"].upper(), str(p["likes"]), str(p["comments"]), p["url"])
        console.print(post_table)

def upload_post_now(post_service: PostService, ai: AIGenerator):
    console.print("\n[bold yellow]--- Upload Post (Instant) ---[/bold yellow]")
    media_path = Prompt.ask("[cyan]Enter full path of image or video file[/cyan]")
    media_path = media_path.strip("\"'")
    
    if not Path(media_path).exists():
        console.print(f"[red]File does not exist at:[/red] {media_path}")
        return

    ext = Path(media_path).suffix.lower()
    default_type = "reel" if ext in [".mp4", ".mov"] else "photo"
    media_type = Prompt.ask("[cyan]Media type (photo/reel)[/cyan]", default=default_type, choices=["photo", "reel"])

    use_ai = Confirm.ask("[cyan]Do you want AI to generate the caption & hashtags?[/cyan]", default=True)
    if use_ai:
        topic = Prompt.ask("[cyan]Enter post topic / niche[/cyan]", default="Motivation and Daily Grind")
        with console.status("[yellow]Generating viral caption with hooks...[/yellow]"):
            gen_res = ai.generate_caption(topic)
            caption = gen_res["caption"]
        console.print("\n[bold green]Generated Caption:[/bold green]\n" + caption + "\n")
        confirm_post = Confirm.ask("[bold yellow]Proceed to publish this post to Instagram now?[/bold yellow]", default=True)
        if not confirm_post:
            console.print("[dim]Post cancelled.[/dim]")
            return
    else:
        caption = Prompt.ask("[cyan]Enter your caption[/cyan]")

    with console.status("[bold green]Uploading to Instagram...[/bold green]"):
        try:
            res = post_service.publish_now(media_path, media_type, caption)
            console.print(f"[bold green]✓ Successfully published![/bold green] URL: {res.get('url')}")
        except Exception as e:
            console.print(f"[bold red]Upload failed:[/bold red] {e}")

def schedule_post(post_service: PostService, ai: AIGenerator):
    console.print("\n[bold yellow]--- Schedule a Post ---[/bold yellow]")
    media_path = Prompt.ask("[cyan]Enter image or video path[/cyan]").strip("\"'")
    if not Path(media_path).exists():
        console.print(f"[red]File does not exist:[/red] {media_path}")
        return

    ext = Path(media_path).suffix.lower()
    default_type = "reel" if ext in [".mp4", ".mov"] else "photo"
    media_type = Prompt.ask("[cyan]Media type (photo/reel)[/cyan]", default=default_type, choices=["photo", "reel"])
    
    topic = Prompt.ask("[cyan]Post topic for AI caption (or press Enter to type manually)[/cyan]", default="")
    if topic:
        with console.status("[yellow]Generating caption...[/yellow]"):
            caption = ai.generate_caption(topic)["caption"]
        console.print(f"\n[green]Generated Caption:[/green]\n{caption}\n")
    else:
        caption = Prompt.ask("[cyan]Enter Caption[/cyan]")

    scheduled_time = Prompt.ask(
        "[cyan]Enter publish date & time (YYYY-MM-DD HH:MM:SS)[/cyan]",
        default=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time() + 3600))
    )

    post_id = post_service.schedule(media_path, media_type, caption, scheduled_time)
    console.print(f"[bold green]✓ Post #{post_id} scheduled for {scheduled_time} successfully![/bold green]")
    console.print("[dim]The background agent will automatically publish it when time arrives.[/dim]")

def run_engagement_bot(engagement: EngagementService, post_service: PostService):
    console.print("\n[bold yellow]🤖 Auto-Engagement & Scheduler Bot Active[/bold yellow]")
    console.print("[dim]Scanning comments for keywords, answering DMs with AI, and checking scheduled posts...[/dim]")
    console.print("[dim]Press Ctrl+C anytime to stop and return to menu.\n[/dim]")

    try:
        while True:
            # 1. Process scheduled posts
            pub_count = post_service.process_pending_scheduled()
            if pub_count > 0:
                console.print(f"[green]Published {pub_count} scheduled post(s)![/green]")

            # 2. Process comments
            c_count = engagement.process_recent_post_comments(post_limit=3)
            if c_count > 0:
                console.print(f"[cyan]Replied to {c_count} comment trigger(s)![/cyan]")

            # 3. Process DMs
            dm_count = engagement.process_unread_dms()
            if dm_count > 0:
                console.print(f"[magenta]Replied to {dm_count} incoming DM(s)![/magenta]")

            time.sleep(30)  # Safe human-like polling interval
    except KeyboardInterrupt:
        console.print("\n[yellow]Bot stopped. Returning to main menu...[/yellow]")

def ai_caption_generator(ai: AIGenerator):
    console.print("\n[bold yellow]✨ AI Caption & Hashtag Generator[/bold yellow]")
    topic = Prompt.ask("[cyan]Enter your post topic or idea[/cyan]")
    tone = Prompt.ask("[cyan]Select tone (engaging, professional, motivational, humorous)[/cyan]", default="engaging")
    with console.status("[yellow]Generating...[/yellow]"):
        res = ai.generate_caption(topic, tone)
    console.print("\n" + Panel(res["caption"], title=f"Generated Caption ({res['source']})", border_style="green"))

def view_dms(client: InstagramAgentClient):
    with console.status("[cyan]Fetching Direct Message inbox...[/cyan]"):
        try:
            threads = client.get_direct_threads(amount=8)
        except Exception as e:
            console.print(f"[red]Error fetching inbox:[/red] {e}")
            return

    table = Table(title="Recent Direct Messages", border_style="magenta")
    table.add_column("From", style="bold yellow")
    table.add_column("Last Message", style="white")
    table.add_column("Time", style="dim")

    for th in threads:
        users = ", ".join([u.username for u in th.users]) if th.users else "Unknown"
        last_msg = th.messages[0].text if th.messages and hasattr(th.messages[0], "text") else "<Media/Action>"
        ts = str(th.messages[0].timestamp)[:19] if th.messages and hasattr(th.messages[0], "timestamp") else ""
        table.add_row(users, str(last_msg), ts)
    console.print(table)

def manage_rules():
    console.print("\n[bold yellow]⚙️ Keyword Auto-Reply Rules[/bold yellow]")
    rules = get_active_rules()
    table = Table(border_style="yellow")
    table.add_column("Trigger Keyword", style="cyan bold")
    table.add_column("Comment Reply", style="white")
    table.add_column("DM Reply", style="green")

    for r in rules:
        table.add_row(r["keyword"], r["reply_comment"] or "-", r["reply_dm"] or "-")
    console.print(table)

    add_new = Confirm.ask("\n[cyan]Do you want to add a new trigger rule?[/cyan]", default=False)
    if add_new:
        kw = Prompt.ask("[cyan]Enter trigger keyword (e.g. 'course', 'ebook', 'offer')[/cyan]")
        c_reply = Prompt.ask("[cyan]Comment reply text[/cyan]", default="Sent you the details in DM! 📩")
        dm_reply = Prompt.ask("[cyan]DM message text with link/info[/cyan]")
        add_keyword_rule(kw, c_reply, dm_reply)
        console.print(f"[bold green]✓ Rule for '{kw}' added successfully![/bold green]")

def auto_generate_and_publish_post(pipeline: AutoContentPipeline):
    console.print("\n[bold yellow]🎨 Auto-Create & Publish Aesthetic Post[/bold yellow]")
    custom = Confirm.ask("[cyan]Do you want to enter a custom quote/topic?[/cyan]", default=False)
    quote = None
    if custom:
        quote = Prompt.ask("[cyan]Enter Quote / Shayari[/cyan]")
    
    with console.status("[bold green]Creating aesthetic artwork and publishing to Instagram...[/bold green]"):
        try:
            res = pipeline.create_and_post_image(quote=quote)
            console.print(f"\n[bold green]✓ Post Successfully Published Live![/bold green]")
            console.print(f"[bold cyan]URL:[/bold cyan] {res.get('url')}\n")
        except Exception as e:
            console.print(f"[bold red]Failed to post:[/bold red] {e}")

def auto_generate_and_publish_reel(pipeline: AutoContentPipeline):
    console.print("\n[bold yellow]🎬 Auto-Create & Publish Aesthetic Reel[/bold yellow]")
    custom = Confirm.ask("[cyan]Do you want to enter a custom Hook & Quote?[/cyan]", default=False)
    hook = None
    quote = None
    if custom:
        hook = Prompt.ask("[cyan]Enter Reel Hook (e.g. 'Ye baat yaad rakhna...')[/cyan]")
        quote = Prompt.ask("[cyan]Enter Main Quote / Line[/cyan]")
    
    with console.status("[bold green]Rendering vertical animated reel video and uploading...[/bold green]"):
        try:
            res = pipeline.create_and_post_reel(hook=hook, quote=quote, duration_sec=6)
            console.print(f"\n[bold green]✓ Reel Successfully Published Live![/bold green]")
            console.print(f"[bold cyan]URL:[/bold cyan] {res.get('url')}\n")
        except Exception as e:
            console.print(f"[bold red]Failed to post reel:[/bold red] {e}")

def main():
    init_db()
    print_banner()

    client = InstagramAgentClient()
    with console.status("[cyan]Authenticating with Instagram session...[/cyan]"):
        if not client.authenticate():
            console.print("[red]❌ Authentication failed. Please run `uv run python login_browser.py` first.[/red]")
            return
    console.print(f"[bold green]✓ Connected as @{client.username}![/bold green]\n")

    ai = AIGenerator()
    post_service = PostService(client)
    engagement = EngagementService(client, ai)
    analytics = AnalyticsService(client)
    pipeline = AutoContentPipeline(client)

    while True:
        console.print("\n[bold cyan]Main Menu:[/bold cyan]")
        console.print("  [bold white][1][/bold white] 📊 View Account Profile & Live Analytics")
        console.print("  [bold white][2][/bold white] 📸 Upload Post (Photo / Reel) Now (Manual File)")
        console.print("  [bold white][3][/bold white] ⏰ Schedule a Post for Later")
        console.print("  [bold white][4][/bold white] 🤖 Run Auto-Engagement Bot (Auto-DM & Comment Responder)")
        console.print("  [bold white][5][/bold white] ✨ AI Caption & Hashtag Generator")
        console.print("  [bold white][6][/bold white] 💬 View Direct Message Inbox")
        console.print("  [bold white][7][/bold white] ⚙️ Keyword Auto-Reply Rules")
        console.print("  [bold yellow][8][/bold yellow] 🎨 [bold green]Auto-Create & Publish Aesthetic Post NOW[/bold green]")
        console.print("  [bold yellow][9][/bold yellow] 🎬 [bold green]Auto-Create & Publish Aesthetic Reel NOW[/bold green]")
        console.print("  [bold white][0][/bold white] 🚪 Exit\n")

        choice = Prompt.ask("[bold yellow]Choose an option[/bold yellow]", choices=["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"], default="1")

        if choice == "1":
            view_profile_and_stats(analytics)
        elif choice == "2":
            upload_post_now(post_service, ai)
        elif choice == "3":
            schedule_post(post_service, ai)
        elif choice == "4":
            run_engagement_bot(engagement, post_service)
        elif choice == "5":
            ai_caption_generator(ai)
        elif choice == "6":
            view_dms(client)
        elif choice == "7":
            manage_rules()
        elif choice == "8":
            auto_generate_and_publish_post(pipeline)
        elif choice == "9":
            auto_generate_and_publish_reel(pipeline)
        elif choice == "0":
            console.print("[bold green]Goodbye! 👋[/bold green]")
            break

if __name__ == "__main__":
    main()
