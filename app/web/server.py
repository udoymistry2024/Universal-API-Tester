import os
import uuid
from typing import Dict, Any
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, PlainTextResponse
from pydantic import BaseModel
from pathlib import Path
from jinja2 import Template

from app.core.provider_manager import ProviderManager
from app.core.scanner import ModelScanner

app = FastAPI(title="Universal AI API Tester Web Server")

# Global in-memory scan store
SCANS: Dict[str, Dict[str, Any]] = {}


@app.get("/robots.txt", response_class=PlainTextResponse)
def robots_txt():
    """Serve robots.txt for search engine crawlers."""
    return """User-agent: *
Allow: /
Disallow: /api/

Sitemap: https://utestapi.onrender.com/sitemap.xml
"""

class ScanRequest(BaseModel):
    provider_id: str
    api_key: str
    concurrency: int = 5
    timeout: float = 15.0
    scan_type: str = "models"  # "models" or "endpoints"

@app.get("/", response_class=HTMLResponse)
def read_index():
    """Serve the Web UI page with dynamic affiliate links."""
    html_path = Path(__file__).parent / "templates" / "index.html"
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            template_content = f.read()
        
        affiliate_link_1 = os.getenv("AFFILIATE_LINK_1", "") or "https://build.nvidia.com/"
        affiliate_link_2 = os.getenv("AFFILIATE_LINK_2", "") or "https://opencode.ai/"
        
        template = Template(template_content)
        rendered_content = template.render(
            affiliate_link_1=affiliate_link_1,
            affiliate_link_2=affiliate_link_2
        )
        return HTMLResponse(content=rendered_content, status_code=200)
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading index.html: {str(e)}</h1>", status_code=500)

@app.get("/api/providers")
def get_providers():
    """Retrieve list of supported AI providers."""
    pm = ProviderManager()
    return [{"id": p.provider_id, "name": p.display_name} for p in pm.list_providers()]

async def run_scan_in_background(scan_id: str, req: ScanRequest):
    """Scan worker that updates the global SCANS store."""
    pm = ProviderManager()
    provider = pm.get_provider(req.provider_id)
    if not provider:
        SCANS[scan_id]["status"] = "failed"
        SCANS[scan_id]["error"] = f"Provider '{req.provider_id}' not found."
        return

    if req.scan_type == "endpoints":
        from app.core.endpoint_tester import EndpointTester
        
        tester = EndpointTester(req.provider_id, req.api_key, timeout=req.timeout)
        try:
            total_candidates = len(tester.candidates)
            SCANS[scan_id]["total"] = total_candidates
            SCANS[scan_id]["current_model"] = "Probing candidate endpoints..."
            SCANS[scan_id]["completed"] = 0
            
            results = await tester.run_diagnostics()
            
            SCANS[scan_id]["results"] = results
            SCANS[scan_id]["completed"] = total_candidates
            SCANS[scan_id]["status"] = "completed"
        except Exception as e:
            SCANS[scan_id]["status"] = "failed"
            SCANS[scan_id]["error"] = str(e)
        return

    scanner = ModelScanner(
        provider=provider,
        api_key=req.api_key,
        concurrency=req.concurrency,
        timeout=req.timeout,
        retry_count=2
    )

    def progress_callback(completed: int, total: int, current_model: str):
        SCANS[scan_id]["completed"] = completed
        SCANS[scan_id]["total"] = total
        SCANS[scan_id]["current_model"] = current_model

    try:
        results = await scanner.scan(progress_callback=progress_callback)
        SCANS[scan_id]["results"] = results
        SCANS[scan_id]["status"] = "completed"
    except Exception as e:
        SCANS[scan_id]["status"] = "failed"
        SCANS[scan_id]["error"] = str(e)

@app.post("/api/scan")
def start_scan(req: ScanRequest, background_tasks: BackgroundTasks):
    """Initiate a scanning task in the background."""
    scan_id = str(uuid.uuid4())
    SCANS[scan_id] = {
        "status": "scanning",
        "completed": 0,
        "total": 0,
        "current_model": "Initializing scanner...",
        "results": [],
        "error": None,
        "scan_type": req.scan_type
    }
    background_tasks.add_task(run_scan_in_background, scan_id, req)
    return {"scan_id": scan_id}

@app.get("/api/scan/status/{scan_id}")
def get_scan_status(scan_id: str):
    """Retrieve scanning progress and results."""
    if scan_id not in SCANS:
        raise HTTPException(status_code=404, detail="Scan session not found")
    return SCANS[scan_id]


class ChatRequest(BaseModel):
    provider_id: str
    api_key: str
    model_id: str
    messages: list
    max_tokens: int = 2048

@app.post("/api/chat")
async def chat_completion(req: ChatRequest):
    """Send a chat message to a selected AI model and return the stream response."""
    from app.core.chat import stream_chat_message

    generator = stream_chat_message(
        provider_id=req.provider_id,
        api_key=req.api_key,
        model_id=req.model_id,
        messages=req.messages,
        max_tokens=req.max_tokens
    )

    return StreamingResponse(generator, media_type="text/event-stream")

