from rich.style import Style

# Color Theme definitions
THEME_COLORS = {
    "primary": "cyan",
    "secondary": "magenta",
    "success": "green",
    "warning": "yellow",
    "error": "red",
    "info": "blue",
    "muted": "bright_black"
}

# Status color mappings
STATUS_STYLES = {
    "Working": Style(color="green", bold=True),
    "Not Accessible": Style(color="red", bold=True),
    "Unsupported": Style(color="yellow"),
    "Deprecated": Style(color="bright_black", italic=True),
    "Quota Exceeded": Style(color="yellow", bold=True),
    "Rate Limited": Style(color="yellow", bold=True),
    "Server Error": Style(color="red"),
    "Invalid API Key": Style(color="red", bold=True),
    "Failed": Style(color="red"),
    "Timeout": Style(color="yellow"),
    "Network Error": Style(color="red"),
    "Error": Style(color="red")
}

# Status Icon mappings
STATUS_ICONS = {
    "Working": "✓",
    "Not Accessible": "🔒",
    "Unsupported": "⚠️",
    "Deprecated": "🕒",
    "Quota Exceeded": "💰",
    "Rate Limited": "⏳",
    "Server Error": "🔥",
    "Invalid API Key": "🔑",
    "Failed": "✗",
    "Timeout": "⏱",
    "Network Error": "🌐",
    "Error": "✗"
}
