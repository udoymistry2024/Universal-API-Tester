import asyncio
import sys
from typing import Optional, List, Dict, Any
# pyrefly: ignore [missing-import]
import typer
import questionary
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.text import Text

from app.core.provider_manager import ProviderManager
from app.core.scanner import ModelScanner
from app.utils.config import ConfigManager
from app.utils.exporter import export_to_csv, export_to_json, export_to_markdown, export_to_txt
from app.ui.terminal import render_logo_and_banner, prompt_provider_selection, prompt_api_key, render_summary
from app.ui.table import build_results_table

# Initialize Typer App
app = typer.Typer(help="Universal AI API Model Tester CLI")
console = Console()

# We run the async main logic using asyncio.run
def run_async(coro):
    return asyncio.run(coro)

async def scan_flow(
    provider_id: str,
    api_key: str,
    concurrency: int,
    timeout: float,
    retry_count: int,
    export_format: Optional[str] = None
):
    pm = ProviderManager()
    provider = pm.get_provider(provider_id)
    if not provider:
        console.print(f"[bold red]Error: Provider '{provider_id}' is not supported.[/bold red]")
        sys.exit(1)
        
    if not api_key:
        console.print(f"[bold red]Error: API Key is required for scanning.[/bold red]")
        sys.exit(1)

    console.print(f"\n[bold cyan]Starting scan for {provider.display_name}...[/bold cyan]")
    
    scanner = ModelScanner(
        provider=provider,
        api_key=api_key,
        concurrency=concurrency,
        timeout=timeout,
        retry_count=retry_count
    )

    results = []
    
    # Progress UI
    with Progress(
        SpinnerColumn(spinner_name="dots"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=40, style="bright_black", complete_style="cyan", finished_style="green"),
        TaskProgressColumn(),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task_id = progress.add_task("[cyan]Connecting to API...", total=100)

        def progress_cb(completed: int, total: int, current_model: str):
            # Update description depending on progress
            if completed == 0:
                progress.update(task_id, description=f"[cyan]Retrieving models...")
            else:
                progress.update(
                    task_id,
                    total=total,
                    completed=completed,
                    description=f"[cyan]Testing model {completed}/{total} - [magenta]{current_model}[/magenta]"
                )

        try:
            results = await scanner.scan(progress_callback=progress_cb)
        except Exception as e:
            progress.stop()
            console.print("\n")
            console.print(Panel(
                Text.assemble(
                    ("Scan failed due to an error:\n", "bold red"),
                    (str(e), "white")
                ),
                title="[bold red]❌ SCAN ERROR[/bold red]",
                border_style="red"
            ))
            return

    if not results:
        console.print("\n[bold yellow]⚠️ No models were discovered or retrieved for this provider.[/bold yellow]\n")
        return []

    # Print results Table
    table = build_results_table(results)
    console.print("\n")
    console.print(table)

    # Print Summary section
    render_summary(results)

    return results


def perform_export(provider_name: str, results: List[Dict[str, Any]], format_type: str):
    """Run requested exporters and print confirmation."""
    fmt = format_type.lower()
    exported_paths = []
    
    if fmt in ["csv", "all"]:
        path = export_to_csv(provider_name, results)
        if path: exported_paths.append(path)
    if fmt in ["json", "all"]:
        path = export_to_json(provider_name, results)
        if path: exported_paths.append(path)
    if fmt in ["md", "markdown", "all"]:
        path = export_to_markdown(provider_name, results)
        if path: exported_paths.append(path)
    if fmt in ["txt", "text", "all"]:
        path = export_to_txt(provider_name, results)
        if path: exported_paths.append(path)

    if exported_paths:
        console.print("\n[bold green]💾 Reports successfully exported to:[/bold green]")
        for path in exported_paths:
            console.print(f"  ✓ [bright_cyan]{path}[/bright_cyan]")


def interactive_export(provider_name: str, results: List[Dict[str, Any]]):
    """Prompt the user for export formats in interactive mode (with coloring and numbering)."""
    custom_style = questionary.Style([
        ('qmark', 'fg:#ff00ff bold'),       # magenta
        ('question', 'bold fg:#ffffff'),    # white
        ('pointer', 'fg:#00ffff bold'),     # cyan
        ('highlighted', 'fg:#00ffff bold'), # cyan
        ('selected', 'fg:#00ffff'),
        ('text', 'fg:#ffffff'),
        ('choice_md', 'fg:#4caf50 bold'),      # green
        ('choice_csv', 'fg:#00bcd4 bold'),     # cyan
        ('choice_json', 'fg:#ffeb3b bold'),    # yellow
        ('choice_txt', 'fg:#e91e63 bold'),     # pink/magenta
        ('choice_all', 'fg:#ffffff bold'),     # white
        ('choice_skip', 'fg:#f44336 bold')      # red
    ])

    choices = [
        questionary.Choice(
            title=[
                ("class:text", f"({i+1}) "),
                (f"class:choice_{val}", name)
            ],
            value=val
        )
        for i, (name, val) in enumerate([
            ("Markdown (.md)", "md"),
            ("CSV (.csv)", "csv"),
            ("JSON (.json)", "json"),
            ("Plain Text (.txt)", "txt"),
            ("All Formats", "all"),
            ("Skip Export", "skip")
        ])
    ]

    try:
        console.print("\n[bold magenta]💾 Save Test Report:[/bold magenta]")
        choice = questionary.select(
            "Select export format:",
            choices=choices,
            style=custom_style,
            instruction="Use ↑↓ arrows and Press Enter to select"
        ).ask()

        if not choice or choice == "skip":
            console.print("\n[bold yellow]⚠️ Export skipped.[/bold yellow]\n")
            return

        perform_export(provider_name, results, choice)
        console.print("\n[bold green]✓ Scan finished successfully! Logs saved to logs/scanner.log[/bold green]\n")
    except KeyboardInterrupt:
        console.print("\n[bold yellow]Export cancelled.[/bold yellow]\n")


def main_interactive():
    """Interactive CLI sequence (synchronous to avoid event loop conflicts)."""
    config_mgr = ConfigManager()
    pm = ProviderManager()
    providers = pm.list_providers()
    
    while True:
        console.clear()
        render_logo_and_banner()
        
        # Selection Menu
        provider = prompt_provider_selection(providers)
        if not provider or provider == "exit":
            console.print("\n[bold yellow]Exiting application. Goodbye![/bold yellow]\n")
            sys.exit(0)

        # Selection of scan type
        custom_style_menu = questionary.Style([
            ('qmark', 'fg:#ff00ff bold'),
            ('question', 'bold fg:#ffffff'),
            ('pointer', 'fg:#00ffff bold'),
            ('highlighted', 'fg:#00ffff bold'),
            ('selected', 'fg:#00ffff'),
            ('text', 'fg:#ffffff'),
        ])
        
        console.print("\n[bold magenta]🔍 Select Scan Action:[/bold magenta]")
        scan_type = questionary.select(
            "What scan would you like to run?",
            choices=[
                questionary.Choice(title="(1) Scan Available Models", value="models"),
                questionary.Choice(title="(2) Test Endpoint Diagnostics", value="endpoints")
            ],
            style=custom_style_menu,
            instruction="Use ↑↓ arrows and Press Enter to select"
        ).ask()

        if not scan_type:
            continue

        # Resolve key
        preloaded_key = config_mgr.get_api_key(provider.provider_id)
        api_key = prompt_api_key(preloaded_key)
        
        # API key is mandatory for models discovery, optional for diagnostics
        if scan_type == "models" and not api_key:
            console.print("[bold red]API key cannot be empty for model scans.[/bold red]")
            input("\nPress Enter to return to the main menu...")
            continue

        if scan_type == "models":
            # Run scan asynchronously
            results = run_async(scan_flow(
                provider_id=provider.provider_id,
                api_key=api_key,
                concurrency=config_mgr.concurrency,
                timeout=config_mgr.timeout,
                retry_count=config_mgr.retry_count
            ))

            # Prompt export synchronously
            if results:
                interactive_export(provider.display_name, results)
        else:
            from app.core.endpoint_tester import EndpointTester
            from app.ui.table import build_endpoints_table
            
            console.print(f"\n[bold cyan]Starting endpoint diagnostics probe for {provider.display_name}...[/bold cyan]")
            
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task_id = progress.add_task("[cyan]Probing candidate endpoints...", total=None)
                tester = EndpointTester(provider.provider_id, api_key, timeout=config_mgr.timeout)
                ep_results = run_async(tester.run_diagnostics())

            if ep_results:
                table = build_endpoints_table(ep_results)
                console.print("\n")
                console.print(table)
                
                # Exporter
                interactive_export(f"{provider.display_name}_endpoints", ep_results)
            else:
                console.print("\n[bold yellow]⚠️ No candidate endpoints found to probe for this provider.[/bold yellow]\n")
        
        input("\nPress Enter to return to the main menu...")


@app.command()
def run(
    provider: Optional[str] = typer.Option(None, "--provider", "-p", help="Provider ID (e.g. openai, anthropic, google)"),
    key: Optional[str] = typer.Option(None, "--key", "-k", help="API Key for testing"),
    concurrency: Optional[int] = typer.Option(None, "--concurrency", "-c", help="Override concurrent requests limit"),
    timeout: Optional[float] = typer.Option(None, "--timeout", "-t", help="Override request timeout in seconds"),
    retries: Optional[int] = typer.Option(None, "--retries", "-r", help="Override rate-limit retry limit"),
    export: Optional[str] = typer.Option(None, "--export", "-e", help="Export format (csv, json, md, txt, all)"),
    endpoints: bool = typer.Option(False, "--endpoints", "-d", help="Run endpoint diagnostic scan instead of model test")
):
    """
    Launch the Universal AI API Model Tester.
    Run without arguments to launch interactive Terminal UI.
    """
    config_mgr = ConfigManager()
    
    if provider or key:
        # Resolve parameters (command line arguments override config file/env)
        p_id = provider or ""
        api_key = key or config_mgr.get_api_key(p_id)
        
        limit = concurrency if concurrency is not None else config_mgr.concurrency
        time_limit = timeout if timeout is not None else config_mgr.timeout
        retry_limit = retries if retries is not None else config_mgr.retry_count
        
        if endpoints:
            from app.core.endpoint_tester import EndpointTester
            from app.ui.table import build_endpoints_table
            
            tester = EndpointTester(p_id, api_key, timeout=time_limit)
            ep_results = run_async(tester.run_diagnostics())
            
            if ep_results:
                table = build_endpoints_table(ep_results)
                console.print("\n")
                console.print(table)
                
                if export:
                    pm = ProviderManager()
                    prov = pm.get_provider(p_id)
                    p_name = f"{prov.display_name if prov else p_id}_endpoints"
                    perform_export(p_name, ep_results, export)
        else:
            results = run_async(scan_flow(
                provider_id=p_id,
                api_key=api_key,
                concurrency=limit,
                timeout=time_limit,
                retry_count=retry_limit
            ))
            
            if results and export:
                pm = ProviderManager()
                prov = pm.get_provider(p_id)
                p_name = prov.display_name if prov else p_id
                perform_export(p_name, results, export)
    else:
        # Interactive mode
        try:
            main_interactive()
        except KeyboardInterrupt:
            console.print("\n[bold red]CLI terminated.[/bold red]")
            sys.exit(0)


@app.command(name="web")
def run_web(
    port: int = typer.Option(8000, "--port", "-p", help="Port to run the web server on"),
    host: str = typer.Option("0.0.0.0", "--host", "-h", help="Host to bind the web server to (use 0.0.0.0 for LAN access)")
):
    """
    Launch the Web UI Server.
    Accessible locally and on your local network (mobile/tablet).
    """
    import uvicorn
    import socket

    # Retrieve local IP address for LAN access info
    local_ip = "localhost"
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        local_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    console.print(f"\n[bold green]🚀 Launching Web UI Server...[/bold green]")
    console.print(f"  ➜ Local:   [bright_cyan]http://localhost:{port}[/bright_cyan]")
    if host == "0.0.0.0" and local_ip != "localhost":
        console.print(f"  ➜ Network: [bright_cyan]http://{local_ip}:{port}[/bright_cyan] (Use this on your Mobile/Tablet!)")
    console.print("\n[dim white]Press Ctrl+C to terminate the server.[/dim white]\n")

    try:
        uvicorn.run("app.web.server:app", host=host, port=port, log_level="info")
    except KeyboardInterrupt:
        console.print("\n[bold red]Web server terminated.[/bold red]")


if __name__ == "__main__":
    app()
