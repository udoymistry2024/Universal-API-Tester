import sys
from typing import List, Dict, Any, Optional
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.table import Table
import questionary
from app.providers.base import BaseProvider

console = Console()

def render_logo_and_banner():
    """Render a high-quality DevOps gradient title and logo."""
    logo = r"""
  _    _  _   _  _____ __      __ ______  _____    _____         _      
 | |  | || \ | ||_   _|\ \    / /|  ____||  __ \  / ____|  /\   | |     
 | |  | ||  \| |  | |   \ \  / / | |__   | |__) || (___   /  \  | |     
 | |  | || . ` |  | |    \ \/ /  |  __|  |  _  /  \___ \ / /\ \ | |     
 | |__| || |\  | _| |_    \  /   | |____ | | \ \  ____) / ____ \| |____ 
  \____/ |_| \_||_____|    \/    |______||_|  \_\|_____/_/    \_\______|
                                                                        
"""
    banner_text = Text()
    banner_text.append(logo, style="bold cyan")
    banner_text.append("⚡ UNIVERSAL AI API MODEL TESTER ⚡\n", style="bold magenta")
    banner_text.append("Instantly Discover & Verify Usable Models Across 14 Providers\n", style="italic white")
    banner_text.append("────────────────────────────────────────────────────────────────", style="dim cyan")
    
    panel = Panel(
        Align.center(banner_text),
        border_style="cyan",
        title="[bold magenta]v1.0.0[/bold magenta]",
        title_align="right",
        subtitle="[bold white]Press Ctrl+C to Exit[/bold white]",
        subtitle_align="center"
    )
    console.print(panel)

def prompt_provider_selection(providers: List[BaseProvider]):
    """Render a colorful selection menu for selecting an AI provider."""
    choices = [
        questionary.Choice(
            title=[
                ("class:text", f"({i+1:2d}) "),
                ("class:highlight", f"{p.display_name:<25}"),
                ("class:dim", f" [{p.provider_id}]")
            ],
            value=p
        )
        for i, p in enumerate(providers)
    ]
    
    # Append Exit Choice
    choices.append(
        questionary.Choice(
            title=[
                ("class:text", f"({len(providers)+1:2d}) "),
                ("class:exit", "Exit Application"),
                ("class:dim", " [exit]")
            ],
            value="exit"
        )
    )
    
    # Custom Questionary styling to match our dark cyan / magenta theme
    custom_style = questionary.Style([
        ('qmark', 'fg:#ff00ff bold'),       # magenta
        ('question', 'bold fg:#ffffff'),    # white
        ('pointer', 'fg:#00ffff bold'),     # cyan
        ('highlighted', 'fg:#00ffff bold'), # cyan
        ('selected', 'fg:#00ffff'),
        ('text', 'fg:#ffffff'),
        ('dim', 'fg:#666666 italic'),
        ('exit', 'fg:#f44336 bold'),        # red for exit option
    ])

    console.print("\n[bold magenta]🤖 Select AI Provider to Scan:[/bold magenta]")
    try:
        selection = questionary.select(
            "",
            choices=choices,
            style=custom_style,
            instruction="Use ↑↓ arrows and Press Enter to select"
        ).ask()
        return selection
    except KeyboardInterrupt:
        console.print("\n[bold red]Operation cancelled by user.[/bold red]")
        sys.exit(0)

def prompt_api_key(default_key: str = "") -> str:
    """Prompt the user to paste their API key. Hidden input is optional, let's keep it visible but masked or simple."""
    if default_key:
        console.print(f"\n[bold green]✓ Pre-loaded API Key from environment variables/dotenv.[/bold green]")
        use_default = questionary.confirm(
            "Use pre-loaded API Key?",
            default=True
        ).ask()
        if use_default:
            return default_key

    # Prompt key
    custom_style = questionary.Style([
        ('question', 'bold fg:#ffffff'),
        ('answer', 'fg:#00ffff bold'),
    ])
    
    key = questionary.password(
        "Paste your API Key:",
        style=custom_style
    ).ask()
    
    if key is None:
        console.print("\n[bold red]Operation cancelled by user.[/bold red]")
        sys.exit(0)
        
    return key.strip()

def render_summary(results: List[Dict[str, Any]]):
    """Render a beautiful, concise summary panel with metrics."""
    total = len(results)
    working = sum(1 for r in results if r["status"] == "Working")
    failed = sum(1 for r in results if r["status"] in ["Failed", "Error", "Network Error"])
    unsupported = sum(1 for r in results if r["status"] == "Unsupported")
    permission_denied = sum(1 for r in results if r["status"] == "Not Accessible")
    quota_exceeded = sum(1 for r in results if r["status"] == "Quota Exceeded")
    rate_limited = sum(1 for r in results if r["status"] == "Rate Limited")
    invalid_key = sum(1 for r in results if r["status"] == "Invalid API Key")
    
    # Latencies
    latencies = [r["latency"] for r in results if r["latency"] > 0 and r["status"] == "Working"]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0.0
    
    working_results = [r for r in results if r["status"] == "Working" and r["latency"] > 0]
    if working_results:
        fastest = min(working_results, key=lambda x: x["latency"])
        slowest = max(working_results, key=lambda x: x["latency"])
        fastest_str = f"{fastest['model_name']} ({fastest['latency']:.3f}s)"
        slowest_str = f"{slowest['model_name']} ({slowest['latency']:.3f}s)"
    else:
        fastest_str = "N/A"
        slowest_str = "N/A"

    success_rate = (working / total * 100) if total > 0 else 0.0

    # Build summary metrics grid
    grid = Table.grid(expand=True)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)
    grid.add_column(ratio=1)

    grid.add_row(
        Text.assemble(("Total Models: ", "cyan"), (str(total), "bold white")),
        Text.assemble(("Working Models: ", "green"), (str(working), "bold green")),
        Text.assemble(("Success Rate:   ", "magenta"), (f"{success_rate:.1f}%", "bold magenta"))
    )
    grid.add_row(
        Text.assemble(("Failed Models: ", "red"), (str(failed), "bold red")),
        Text.assemble(("Avg Latency:    ", "cyan"), (f"{avg_latency:.3f}s", "bold white")),
        Text.assemble(("Quota Exceeded: ", "yellow"), (str(quota_exceeded), "bold yellow"))
    )
    grid.add_row(
        Text.assemble(("Unsupported:   ", "yellow"), (str(unsupported), "bold yellow")),
        Text.assemble(("Fastest Model:  ", "green"), (fastest_str, "bold white")),
        Text.assemble(("Rate Limited:   ", "yellow"), (str(rate_limited), "bold yellow"))
    )
    grid.add_row(
        Text.assemble(("Perm. Denied:  ", "red"), (str(permission_denied), "bold red")),
        Text.assemble(("Slowest Model:  ", "red"), (slowest_str, "bold white")),
        Text.assemble(("Invalid Keys:   ", "red"), (str(invalid_key), "bold red"))
    )

    panel = Panel(
        grid,
        title="[bold magenta]📊 SCAN SUMMARY[/bold magenta]",
        border_style="magenta",
        padding=(1, 2)
    )
    console.print("\n")
    console.print(panel)
