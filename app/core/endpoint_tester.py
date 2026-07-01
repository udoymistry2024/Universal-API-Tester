import time
import asyncio
import httpx
from typing import List, Dict, Any, Optional
from app.providers.base import BaseProvider

# Diagnostic candidates mapping
CANDIDATE_ENDPOINTS: Dict[str, List[Dict[str, str]]] = {
    "openai": [
        {"url": "https://api.openai.com/v1/models", "method": "GET"},
        {"url": "https://api.openai.com/v1/chat/completions", "method": "POST"},
        {"url": "https://api.openai.com/v1/embeddings", "method": "POST"},
        {"url": "https://api.openai.com/v1/engines", "method": "GET"}
    ],
    "anthropic": [
        {"url": "https://api.anthropic.com/v1/models", "method": "GET"},
        {"url": "https://api.anthropic.com/v1/messages", "method": "POST"},
        {"url": "https://api.anthropic.com/v1/complete", "method": "POST"}
    ],
    "google": [
        {"url": "https://generativelanguage.googleapis.com/v1beta/models", "method": "GET"},
        {"url": "https://generativelanguage.googleapis.com/v1/models", "method": "GET"},
        {"url": "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent", "method": "POST"}
    ],
    "nvidia": [
        {"url": "https://integrate.api.nvidia.com/v1/models", "method": "GET"},
        {"url": "https://api.nvidia.com/v1/models", "method": "GET"},
        {"url": "https://integrate.api.nvidia.com/v1/chat/completions", "method": "POST"}
    ],
    "openrouter": [
        {"url": "https://openrouter.ai/api/v1/models", "method": "GET"},
        {"url": "https://openrouter.ai/api/v1/chat/completions", "method": "POST"},
        {"url": "https://openrouter.ai/api/v1/auth/key", "method": "GET"}
    ],
    "deepseek": [
        {"url": "https://api.deepseek.com/models", "method": "GET"},
        {"url": "https://api.deepseek.com/v1/models", "method": "GET"},
        {"url": "https://api.deepseek.com/chat/completions", "method": "POST"}
    ],
    "mistral": [
        {"url": "https://api.mistral.ai/v1/models", "method": "GET"},
        {"url": "https://api.mistral.ai/v1/chat/completions", "method": "POST"}
    ],
    "xai": [
        {"url": "https://api.x.ai/v1/models", "method": "GET"},
        {"url": "https://api.x.ai/v1/chat/completions", "method": "POST"}
    ],
    "together": [
        {"url": "https://api.together.xyz/v1/models", "method": "GET"},
        {"url": "https://api.together.xyz/v1/chat/completions", "method": "POST"}
    ],
    "groq": [
        {"url": "https://api.groq.com/openai/v1/models", "method": "GET"},
        {"url": "https://api.groq.com/openai/v1/chat/completions", "method": "POST"}
    ],
    "cerebras": [
        {"url": "https://api.cerebras.ai/v1/models", "method": "GET"},
        {"url": "https://api.cerebras.ai/v1/chat/completions", "method": "POST"}
    ],
    "fireworks": [
        {"url": "https://api.fireworks.ai/inference/v1/models", "method": "GET"},
        {"url": "https://api.fireworks.ai/inference/v1/chat/completions", "method": "POST"}
    ],
    "opencode_zen": [
        {"url": "https://opencode.ai/zen/v1/models", "method": "GET"},
        {"url": "https://opencode.ai/zen/v1/chat/completions", "method": "POST"}
    ],
    "xiaomi": [
        {"url": "https://api.xiaomimimo.com/v1/models", "method": "GET"},
        {"url": "https://token-plan-cn.xiaomimimo.com/v1/models", "method": "GET"},
        {"url": "https://api.xiaomimimo.com/v1/chat/completions", "method": "POST"},
        {"url": "https://token-plan-cn.xiaomimimo.com/v1/chat/completions", "method": "POST"},
        {"url": "https://api.xiaomimimo.com/anthropic/v1/messages", "method": "POST"}
    ]
}

class EndpointTester:
    def __init__(self, provider_id: str, api_key: str = "", timeout: float = 8.0):
        self.provider_id = provider_id
        self.api_key = api_key
        self.timeout = timeout
        self.candidates = CANDIDATE_ENDPOINTS.get(provider_id, [])

    def _get_headers(self, url: str) -> dict:
        """Construct correct headers based on endpoint provider type."""
        headers = {}
        if not self.api_key:
            return headers

        if self.provider_id == "anthropic":
            headers = {
                "x-api-key": self.api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json"
            }
        else:
            # Default to Bearer Authorization for OpenAI-compatible and others
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
        return headers

    async def probe_single(self, client: httpx.AsyncClient, url: str, method: str) -> Dict[str, Any]:
        # Formulate Gemini queries which append ?key=
        target_url = url
        if self.provider_id == "google" and self.api_key:
            separator = "&" if "?" in url else "?"
            target_url = f"{url}{separator}key={self.api_key}"

        headers = self._get_headers(url)
        start_time = time.perf_counter()
        
        try:
            if method == "POST":
                # Send empty/dummy bodies to check path response
                response = await client.post(target_url, headers=headers, json={}, timeout=self.timeout)
            else:
                response = await client.get(target_url, headers=headers, timeout=self.timeout)
                
            latency = time.perf_counter() - start_time
            status_code = response.status_code
            server_header = response.headers.get("server", "Unknown")

            if status_code in [200, 201]:
                status = "Active"
                info = f"200 OK | Server: {server_header}"
            elif status_code in [401, 403]:
                status = "Active (Auth Required)"
                info = f"HTTP {status_code} | Verification needed"
            elif status_code == 405:
                status = "Active (Method Not Allowed)"
                info = "Endpoint exists, requires POST/GET"
            elif status_code == 404:
                status = "Inactive (404)"
                info = "Path not found on host"
            elif status_code >= 500:
                status = "Server Error"
                info = f"HTTP {status_code} internal error"
            else:
                status = f"HTTP {status_code}"
                info = f"Returned status code {status_code}"

            return {
                "url": url,
                "method": method,
                "status": status,
                "latency": latency,
                "info": info
            }

        except httpx.TimeoutException:
            latency = time.perf_counter() - start_time
            return {
                "url": url,
                "method": method,
                "status": "Offline (Timeout)",
                "latency": latency,
                "info": "Connection timed out"
            }
        except httpx.HTTPError as e:
            latency = time.perf_counter() - start_time
            return {
                "url": url,
                "method": method,
                "status": "Offline (HTTP Error)",
                "latency": latency,
                "info": str(e)
            }
        except Exception as e:
            latency = time.perf_counter() - start_time
            return {
                "url": url,
                "method": method,
                "status": "Offline (Error)",
                "latency": latency,
                "info": str(e)
            }

    async def run_diagnostics(self) -> List[Dict[str, Any]]:
        """Probe all candidate endpoints concurrently."""
        if not self.candidates:
            return []

        limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
        async with httpx.AsyncClient(limits=limits, follow_redirects=True) as client:
            tasks = [
                self.probe_single(client, cand["url"], cand["method"]) 
                for cand in self.candidates
            ]
            results = await asyncio.gather(*tasks)
            # Sort results with Active ones first
            results.sort(key=lambda x: (not x["status"].startswith("Active"), x["url"]))
            return results
