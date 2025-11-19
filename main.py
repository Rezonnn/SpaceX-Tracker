#!/usr/bin/env python3
"""SpaceX Launch Tracker (CLI)

A command-line tool that fetches live launch data from the public SpaceX API.
It lets you browse upcoming and recent launches, view details, and search by mission name.

Language: Python 3
Type: CLI (terminal) app using live HTTP API.
"""

import sys
import textwrap
from datetime import datetime
from typing import List, Dict, Any, Optional

import requests
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel
from rich import box

API_BASE = "https://api.spacexdata.com/v5"

console = Console()


def fetch_json(path: str) -> Any:
    """Fetch JSON from the SpaceX API and handle errors gracefully."""
    url = f"{API_BASE}{path}"
    try:
        resp = requests.get(url, timeout=15)
        resp.raise_for_status()
        return resp.json()
    except requests.RequestException as e:
        console.print(f"[bold red]Error:[/bold red] Failed to fetch {url}\n{e}")
        return None


def format_datetime(iso_str: Optional[str]) -> str:
    if not iso_str:
        return "—"
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M UTC")
    except Exception:
        return iso_str


def load_rocket_map() -> Dict[str, str]:
    """Return a mapping from rocket id -> rocket name."""
    rockets = fetch_json("/rockets") or []
    mapping = {}
    for r in rockets:
        _id = r.get("id")
        name = r.get("name") or "Unknown rocket"
        if _id:
            mapping[_id] = name
    return mapping


def load_launchpad_map() -> Dict[str, str]:
    pads = fetch_json("/launchpads") or []
    mapping = {}
    for p in pads:
        _id = p.get("id")
        name = p.get("name") or "Unknown pad"
        locality = p.get("locality") or ""
        region = p.get("region") or ""
        loc = ", ".join(part for part in [locality, region] if part)
        mapping[_id] = f"{name} ({loc})" if loc else name
    return mapping


def get_upcoming_launches() -> List[Dict[str, Any]]:
    launches = fetch_json("/launches/upcoming") or []
    # Sort by date ascending (soonest first)
    launches.sort(key=lambda x: x.get("date_utc") or "")
    return launches


def get_past_launches(limit: int = 20) -> List[Dict[str, Any]]:
    launches = fetch_json("/launches/past") or []
    # Most recent first
    launches.sort(key=lambda x: x.get("date_utc") or "", reverse=True)
    return launches[:limit]


def show_launch_table(title: str, launches: List[Dict[str, Any]]) -> None:
    if not launches:
        console.print(Panel.fit("No launches to display.", title=title))
        return

    table = Table(
        title=title,
        box=box.SIMPLE_HEAVY,
        show_lines=False,
        header_style="bold cyan",
    )
    table.add_column("#", justify="right", style="dim", width=3)
    table.add_column("Mission", no_wrap=True)
    table.add_column("Date", no_wrap=True)
    table.add_column("Rocket", no_wrap=True)
    table.add_column("Launchpad", no_wrap=True)
    table.add_column("Success", justify="center", width=7)

    rocket_map = load_rocket_map()
    pad_map = load_launchpad_map()

    for idx, launch in enumerate(launches, start=1):
        name = launch.get("name") or "(no name)"
        date = format_datetime(launch.get("date_utc"))
        rocket_name = rocket_map.get(launch.get("rocket"), "Unknown")
        pad_name = pad_map.get(launch.get("launchpad"), "Unknown")
        success = launch.get("success")
        if success is True:
            success_str = "[green]✔[/green]"
        elif success is False:
            success_str = "[red]✖[/red]"
        else:
            success_str = "[yellow]?[/yellow]"

        table.add_row(
            str(idx),
            name,
            date,
            rocket_name,
            pad_name,
            success_str,
        )

    console.print(table)


def choose_launch(launches: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    if not launches:
        return None

    while True:
        choice = Prompt.ask(
            "Enter a launch [bold]number[/bold] to view details, or press [bold]Enter[/bold] to go back",
            default="",
        )
        if not choice.strip():
            return None
        if not choice.isdigit():
            console.print("[red]Please enter a valid number.[/red]")
            continue
        idx = int(choice)
        if 1 <= idx <= len(launches):
            return launches[idx - 1]
        console.print(f"[red]Number must be between 1 and {len(launches)}.[/red]")


def show_launch_details(launch: Dict[str, Any]) -> None:
    rocket_map = load_rocket_map()
    pad_map = load_launchpad_map()

    name = launch.get("name") or "(no name)"
    date = format_datetime(launch.get("date_utc"))
    rocket_name = rocket_map.get(launch.get("rocket"), "Unknown rocket")
    pad_name = pad_map.get(launch.get("launchpad"), "Unknown launchpad")
    success = launch.get("success")
    details = launch.get("details") or "No description provided."
    flight_number = launch.get("flight_number")
    webcast = (launch.get("links") or {}).get("webcast") or "N/A"
    article = (launch.get("links") or {}).get("article") or "N/A"
    wiki = (launch.get("links") or {}).get("wikipedia") or "N/A"

    if success is True:
        success_str = "[green]Success[/green]"
    elif success is False:
        success_str = "[red]Failure[/red]"
    else:
        success_str = "[yellow]Unknown / upcoming[/yellow]"

    body_lines = [
        f"[bold]Mission:[/bold] {name}",
        f"[bold]Flight #:[/bold] {flight_number}",
        f"[bold]Date:[/bold] {date}",
        f"[bold]Rocket:[/bold] {rocket_name}",
        f"[bold]Launchpad:[/bold] {pad_name}",
        f"[bold]Status:[/bold] {success_str}",
        "",
        "[bold]Details:[/bold]",
        textwrap.fill(details, width=90),
        "",
        f"[bold]Webcast:[/bold] {webcast}",
        f"[bold]Article:[/bold] {article}",
        f"[bold]Wikipedia:[/bold] {wiki}",
    ]

    console.print(
        Panel(
            "\n".join(body_lines),
            title="Launch details",
            expand=False,
            border_style="cyan",
        )
    )


def search_launches(launches: List[Dict[str, Any]]) -> None:
    if not launches:
        console.print("[yellow]No launches loaded yet. Try viewing past launches first.[/yellow]")
        return

    query = Prompt.ask("Enter part of a mission name to search (case-insensitive)", default="").strip()
    if not query:
        return

    query_lower = query.lower()
    matches = [l for l in launches if query_lower in (l.get("name") or "").lower()]

    if not matches:
        console.print(f"[yellow]No launches found matching '{query}'.[/yellow]")
        return

    show_launch_table(f"Search results for '{query}'", matches)
    chosen = choose_launch(matches)
    if chosen:
        show_launch_details(chosen)


def main_menu() -> None:
    past_cache: List[Dict[str, Any]] = []
    upcoming_cache: List[Dict[str, Any]] = []

    while True:
        console.print("\n[bold cyan]SpaceX Launch Tracker[/bold cyan]")
        console.print("[dim]Live data from api.spacexdata.com[/dim]\n")
        console.print("[bold]1.[/bold] View upcoming launches")
        console.print("[bold]2.[/bold] View recent launches")
        console.print("[bold]3.[/bold] Search recent launches by mission name")
        console.print("[bold]4.[/bold] Refresh all data")
        console.print("[bold]0.[/bold] Exit")

        choice = Prompt.ask("Choose an option", choices=["0", "1", "2", "3", "4"], default="1")

        if choice == "0":
            console.print("Goodbye! 👋")
            return

        if choice == "1":
            upcoming_cache = get_upcoming_launches()
            show_launch_table("Upcoming launches", upcoming_cache)
            chosen = choose_launch(upcoming_cache)
            if chosen:
                show_launch_details(chosen)

        elif choice == "2":
            past_cache = get_past_launches(limit=20)
            show_launch_table("Recent launches", past_cache)
            chosen = choose_launch(past_cache)
            if chosen:
                show_launch_details(chosen)

        elif choice == "3":
            if not past_cache:
                past_cache = get_past_launches(limit=50)
            search_launches(past_cache)

        elif choice == "4":
            console.print("[dim]Refreshing all cached data...[/dim]")
            past_cache = get_past_launches(limit=50)
            upcoming_cache = get_upcoming_launches()
            console.print("[green]Data refreshed.[/green]")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[dim]Interrupted by user.[/dim]")
        sys.exit(0)
