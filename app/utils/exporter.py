import os
import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

def generate_filename(provider_name: str, ext: str) -> Path:
    """Generate timestamped filename in the reports directory."""
    # Clean provider name for filename
    clean_name = "".join(c for c in provider_name if c.isalnum() or c in (" ", "_", "-")).strip().replace(" ", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return REPORTS_DIR / f"{clean_name}_{timestamp}.{ext}"

def export_to_csv(provider_name: str, results: List[Dict[str, Any]]) -> str:
    filepath = generate_filename(provider_name, "csv")
    if not results:
        return ""
    
    keys = results[0].keys()
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(results)
    
    return str(filepath)

def export_to_json(provider_name: str, results: List[Dict[str, Any]]) -> str:
    filepath = generate_filename(provider_name, "json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    return str(filepath)

def export_to_markdown(provider_name: str, results: List[Dict[str, Any]]) -> str:
    filepath = generate_filename(provider_name, "md")
    if not results:
        return ""
    
    # Define columns
    headers = [
        "Provider", "Model ID", "Status", "Latency", "Reason", 
        "Context", "Vision", "Reasoning", "Streaming", "Tool Calling", "JSON"
    ]
    
    lines = []
    lines.append(f"# Model Test Report for {provider_name}")
    lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # Table headers
    lines.append("| " + " | ".join(headers) + " |")
    lines.append("| " + " | ".join(["---"] * len(headers)) + " |")
    
    # Rows
    for r in results:
        latency = f"{r['latency']:.3f}s" if r["latency"] > 0 else "-"
        reason = r["error_message"][:30] + "..." if len(r["error_message"]) > 30 else r["error_message"]
        
        row = [
            r["provider"],
            f"`{r['model_id']}`",
            r["status"],
            latency,
            reason or "N/A",
            str(r["context_window"]),
            "✓" if r["supports_vision"] else "-",
            "✓" if r["supports_reasoning"] else "-",
            "✓" if r["supports_streaming"] else "-",
            "✓" if r["supports_tools"] else "-",
            "✓" if r["supports_json"] else "-"
        ]
        lines.append("| " + " | ".join(row) + " |")
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    return str(filepath)

def export_to_txt(provider_name: str, results: List[Dict[str, Any]]) -> str:
    filepath = generate_filename(provider_name, "txt")
    
    lines = []
    lines.append(f"=== MODEL TEST REPORT: {provider_name} ===")
    lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    for r in results:
        latency = f"{r['latency']:.3f}s" if r["latency"] > 0 else "N/A"
        lines.append(f"Model ID: {r['model_id']}")
        lines.append(f"  Status: {r['status']}")
        lines.append(f"  Latency: {latency}")
        lines.append(f"  Capabilities:")
        lines.append(f"    Context Window: {r['context_window']}")
        lines.append(f"    Vision: {'Yes' if r['supports_vision'] else 'No'}")
        lines.append(f"    Reasoning: {'Yes' if r['supports_reasoning'] else 'No'}")
        lines.append(f"    Streaming: {'Yes' if r['supports_streaming'] else 'No'}")
        lines.append(f"    Tool Calling: {'Yes' if r['supports_tools'] else 'No'}")
        lines.append(f"    JSON Mode: {'Yes' if r['supports_json'] else 'No'}")
        if r["error_message"]:
            lines.append(f"  Error: {r['error_message']}")
        lines.append("-" * 40)
        
    with open(filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
        
    return str(filepath)
