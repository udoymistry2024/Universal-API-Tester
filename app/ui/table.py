from typing import List, Dict, Any
from rich.table import Table
from rich.text import Text
from app.ui.colors import STATUS_STYLES, STATUS_ICONS

def build_results_table(results: List[Dict[str, Any]]) -> Table:
    """Build a Rich Table containing model scan results and capabilities."""
    table = Table(
        title="Universal AI API Model Test Report",
        title_style="bold cyan",
        show_header=True,
        header_style="bold magenta",
        border_style="cyan",
        box=None,  # Minimalist box styling looks extremely modern
        padding=(0, 1)
    )

    # Add columns
    table.add_column("Provider", style="bright_white", width=12)
    table.add_column("Model ID", style="bright_cyan", no_wrap=True)
    table.add_column("Working", justify="center", width=8)
    table.add_column("Latency", justify="right", width=9)
    table.add_column("Reason / Error", style="bright_black", width=30)
    table.add_column("Context", justify="right", style="bright_white", width=8)
    table.add_column("Vision", justify="center", width=6)
    table.add_column("Reasoning", justify="center", width=9)
    table.add_column("Streaming", justify="center", width=9)
    table.add_column("Tool Calling", justify="center", width=12)
    table.add_column("JSON", justify="center", width=6)
    table.add_column("Status", justify="center", width=16)

    for r in results:
        status = r["status"]
        status_style = STATUS_STYLES.get(status, "white")
        status_icon = STATUS_ICONS.get(status, "✗")
        
        # Working column
        working_text = Text()
        if status == "Working":
            working_text.append("✓", style="bold green")
        else:
            working_text.append("✗", style="bold red")

        # Latency column
        latency_val = r["latency"]
        if latency_val > 0:
            latency_text = f"{latency_val:.3f}s"
        else:
            latency_text = "-"

        # Reason column (truncated)
        err_msg = r["error_message"]
        if len(err_msg) > 28:
            truncated_err = err_msg[:25] + "..."
        else:
            truncated_err = err_msg or "-"
            
        reason_color = "red" if status in ["Invalid API Key", "Not Accessible", "Server Error"] else "yellow"
        reason_text = Text(truncated_err, style=f"dim {reason_color}" if err_msg else "dim white")

        # Capabilities columns
        def format_cap(val: bool) -> Text:
            return Text("✓", style="bold green") if val else Text("-", style="bright_black")

        # Context limit format
        ctx = r["context_window"]
        if isinstance(ctx, int):
            if ctx >= 1000000:
                ctx_str = f"{ctx // 1000000}M"
            elif ctx >= 1000:
                ctx_str = f"{ctx // 1000}k"
            else:
                ctx_str = str(ctx)
        else:
            ctx_str = "-"

        table.add_row(
            r["provider"],
            r["model_id"],
            working_text,
            latency_text,
            reason_text,
            ctx_str,
            format_cap(r["supports_vision"]),
            format_cap(r["supports_reasoning"]),
            format_cap(r["supports_streaming"]),
            format_cap(r["supports_tools"]),
            format_cap(r["supports_json"]),
            Text(f"{status_icon} {status}", style=status_style)
        )

    return table


def build_endpoints_table(results: List[Dict[str, Any]]) -> Table:
    """Build a Rich Table containing endpoint diagnostic scan results."""
    table = Table(
        title="AI Provider Endpoint Diagnostics Report",
        title_style="bold magenta",
        show_header=True,
        header_style="bold cyan",
        border_style="magenta",
        box=None,
        padding=(0, 1)
    )

    table.add_column("Candidate Endpoint URL", style="bright_cyan", no_wrap=True)
    table.add_column("Method", justify="center", style="bright_magenta", width=8)
    table.add_column("Latency", justify="right", width=10)
    table.add_column("Status", justify="center", width=25)
    table.add_column("Diagnostic Details", style="bright_black", width=35)

    for r in results:
        status = r["status"]
        if "Active" in status:
            if "Auth Required" in status:
                status_style = "bold yellow"
                status_icon = "🔑"
            else:
                status_style = "bold green"
                status_icon = "✓"
        elif "Offline" in status:
            status_style = "bold red"
            status_icon = "🔌"
        else:
            status_style = "red"
            status_icon = "✗"

        latency_val = r["latency"]
        latency_text = f"{latency_val:.3f}s" if latency_val > 0 else "-"

        table.add_row(
            r["url"],
            r["method"],
            latency_text,
            Text(f"{status_icon} {status}", style=status_style),
            Text(r["info"], style="dim white")
        )

    return table
