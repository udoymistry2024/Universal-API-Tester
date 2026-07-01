"""
Chat handler for sending and streaming messages to AI provider models.
Supports OpenAI-compatible, Anthropic, and Google Gemini APIs.
"""
import json
import time
import httpx
from typing import Dict, Any, List, Optional, AsyncGenerator

# Provider chat endpoint configurations
PROVIDER_CHAT_CONFIG: Dict[str, Dict[str, str]] = {
    "openai":       {"url": "https://api.openai.com/v1/chat/completions",               "type": "openai"},
    "deepseek":     {"url": "https://api.deepseek.com/chat/completions",                 "type": "openai"},
    "mistral":      {"url": "https://api.mistral.ai/v1/chat/completions",                "type": "openai"},
    "xai":          {"url": "https://api.x.ai/v1/chat/completions",                      "type": "openai"},
    "together":     {"url": "https://api.together.xyz/v1/chat/completions",              "type": "openai"},
    "groq":         {"url": "https://api.groq.com/openai/v1/chat/completions",           "type": "openai"},
    "cerebras":     {"url": "https://api.cerebras.ai/v1/chat/completions",               "type": "openai"},
    "fireworks":    {"url": "https://api.fireworks.ai/inference/v1/chat/completions",     "type": "openai"},
    "nvidia":       {"url": "https://integrate.api.nvidia.com/v1/chat/completions",      "type": "openai"},
    "openrouter":   {"url": "https://openrouter.ai/api/v1/chat/completions",             "type": "openai"},
    "opencode_zen": {"url": "https://opencode.ai/zen/v1/chat/completions",               "type": "openai"},
    "xiaomi":       {"url": "https://api.xiaomimimo.com/v1/chat/completions",            "type": "openai"},
    "anthropic":    {"url": "https://api.anthropic.com/v1/messages",                     "type": "anthropic"},
    "google":       {"url": "https://generativelanguage.googleapis.com/v1beta/models/",  "type": "google"},
    "cohere":       {"url": "https://api.cohere.com/compatibility/v1/chat/completions", "type": "openai"},
    "perplexity":   {"url": "https://api.perplexity.ai/chat/completions",               "type": "openai"},
    "deepinfra":    {"url": "https://api.deepinfra.com/v1/openai/chat/completions",      "type": "openai"},
}


async def send_chat_message(
    provider_id: str,
    api_key: str,
    model_id: str,
    messages: List[Dict[str, str]],
    timeout: float = 60.0,
    max_tokens: int = 2048
) -> Dict[str, Any]:
    """
    Send a chat message to an AI provider and return the response.
    (Non-streaming fallback method)
    """
    config = PROVIDER_CHAT_CONFIG.get(provider_id)
    if not config:
        return {"response": "", "latency": 0, "tokens_in": 0, "tokens_out": 0, "error": f"Provider '{provider_id}' not supported."}

    provider_type = config["type"]
    start = time.perf_counter()

    try:
        async with httpx.AsyncClient(follow_redirects=True) as client:
            if provider_type == "openai":
                headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
                payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7}
                resp = await client.post(config["url"], headers=headers, json=payload, timeout=timeout)
                data = resp.json()
                if resp.status_code != 200:
                    return {"response": "", "latency": time.perf_counter() - start, "tokens_in": 0, "tokens_out": 0, "error": data.get("error", {}).get("message", str(data))}
                return {
                    "response": data["choices"][0]["message"]["content"].strip(),
                    "latency": time.perf_counter() - start,
                    "tokens_in": data.get("usage", {}).get("prompt_tokens", 0),
                    "tokens_out": data.get("usage", {}).get("completion_tokens", 0),
                    "error": None
                }
            elif provider_type == "anthropic":
                headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
                system_text = ""
                filtered = []
                for m in messages:
                    if m["role"] == "system":
                        system_text += m["content"] + "\n"
                    else:
                        filtered.append(m)
                if not filtered or filtered[0]["role"] != "user":
                    filtered.insert(0, {"role": "user", "content": "Hello"})
                payload = {"model": model_id, "messages": filtered, "max_tokens": max_tokens}
                if system_text.strip():
                    payload["system"] = system_text.strip()
                resp = await client.post(config["url"], headers=headers, json=payload, timeout=timeout)
                data = resp.json()
                if resp.status_code != 200:
                    return {"response": "", "latency": time.perf_counter() - start, "tokens_in": 0, "tokens_out": 0, "error": data.get("error", {}).get("message", str(data))}
                text = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
                return {
                    "response": text.strip(),
                    "latency": time.perf_counter() - start,
                    "tokens_in": data.get("usage", {}).get("input_tokens", 0),
                    "tokens_out": data.get("usage", {}).get("output_tokens", 0),
                    "error": None
                }
            elif provider_type == "google":
                url = f"{config['url']}{model_id}:generateContent?key={api_key}"
                contents = [{"role": "user" if m["role"] in ("user", "system") else "model", "parts": [{"text": m["content"]}]} for m in messages]
                payload = {"contents": contents, "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}}
                resp = await client.post(url, json=payload, timeout=timeout)
                data = resp.json()
                if resp.status_code != 200:
                    return {"response": "", "latency": time.perf_counter() - start, "tokens_in": 0, "tokens_out": 0, "error": data.get("error", {}).get("message", str(data))}
                parts = data.get("candidates", [{}])[0].get("content", {}).get("parts", [])
                text = "".join(p.get("text", "") for p in parts)
                return {
                    "response": text.strip(),
                    "latency": time.perf_counter() - start,
                    "tokens_in": data.get("usageMetadata", {}).get("promptTokenCount", 0),
                    "tokens_out": data.get("usageMetadata", {}).get("candidatesTokenCount", 0),
                    "error": None
                }
    except Exception as e:
        return {"response": "", "latency": time.perf_counter() - start, "tokens_in": 0, "tokens_out": 0, "error": str(e)}


async def stream_chat_message(
    provider_id: str,
    api_key: str,
    model_id: str,
    messages: List[Dict[str, str]],
    timeout: float = 60.0,
    max_tokens: int = 2048
) -> AsyncGenerator[str, None]:
    """
    Stream a chat message from an AI provider.
    Yields JSON lines containing:
      - {"type": "content", "text": "..."}
      - {"type": "error", "text": "..."}
      - {"type": "meta", "latency": ...}
    """
    config = PROVIDER_CHAT_CONFIG.get(provider_id)
    if not config:
        yield json.dumps({"type": "error", "text": f"Provider '{provider_id}' not supported."}) + "\n"
        return

    provider_type = config["type"]
    start_time = time.perf_counter()

    try:
        if provider_type == "openai":
            headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
            payload = {"model": model_id, "messages": messages, "max_tokens": max_tokens, "temperature": 0.7, "stream": True}
            async with httpx.AsyncClient(follow_redirects=True).stream(
                "POST", config["url"], headers=headers, json=payload, timeout=timeout
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    error_msg = f"HTTP {response.status_code}: {body.decode('utf-8', errors='ignore')}"
                    yield json.dumps({"type": "error", "text": error_msg}) + "\n"
                    return

                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            
                            # Support DeepSeek/compatible reasoning content
                            reasoning = delta.get("reasoning_content", "")
                            if reasoning:
                                yield json.dumps({"type": "reasoning", "text": reasoning}) + "\n"
                            
                            content = delta.get("content", "")
                            if content:
                                yield json.dumps({"type": "content", "text": content}) + "\n"
                        except Exception:
                            pass

        elif provider_type == "anthropic":
            headers = {"x-api-key": api_key, "anthropic-version": "2023-06-01", "Content-Type": "application/json"}
            system_text = ""
            filtered = []
            for m in messages:
                if m["role"] == "system":
                    system_text += m["content"] + "\n"
                else:
                    filtered.append(m)
            if not filtered or filtered[0]["role"] != "user":
                filtered.insert(0, {"role": "user", "content": "Hello"})
            payload = {"model": model_id, "messages": filtered, "max_tokens": max_tokens, "stream": True}
            if system_text.strip():
                payload["system"] = system_text.strip()

            async with httpx.AsyncClient(follow_redirects=True).stream(
                "POST", config["url"], headers=headers, json=payload, timeout=timeout
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    error_msg = f"HTTP {response.status_code}: {body.decode('utf-8', errors='ignore')}"
                    yield json.dumps({"type": "error", "text": error_msg}) + "\n"
                    return

                event_name = ""
                async for line in response.aiter_lines():
                    if not line.strip():
                        continue
                    if line.startswith("event: "):
                        event_name = line[7:].strip()
                    elif line.startswith("data: "):
                        data_str = line[6:].strip()
                        try:
                            data = json.loads(data_str)
                            if event_name == "content_block_delta":
                                delta = data.get("delta", {})
                                if delta.get("type") == "text_delta":
                                    yield json.dumps({"type": "content", "text": delta.get("text", "")}) + "\n"
                        except Exception:
                            pass

        elif provider_type == "google":
            url = f"{config['url']}{model_id}:streamGenerateContent?key={api_key}"
            contents = [{"role": "user" if m["role"] in ("user", "system") else "model", "parts": [{"text": m["content"]}]} for m in messages]
            payload = {"contents": contents, "generationConfig": {"maxOutputTokens": max_tokens, "temperature": 0.7}}
            async with httpx.AsyncClient(follow_redirects=True).stream(
                "POST", url, json=payload, timeout=timeout
            ) as response:
                if response.status_code != 200:
                    body = await response.aread()
                    error_msg = f"HTTP {response.status_code}: {body.decode('utf-8', errors='ignore')}"
                    yield json.dumps({"type": "error", "text": error_msg}) + "\n"
                    return

                buffer = ""
                async for chunk in response.aiter_bytes():
                    buffer += chunk.decode("utf-8", errors="ignore")
                    while True:
                        buffer = buffer.strip().lstrip(",").lstrip("[").strip()
                        if not buffer:
                            break
                        brace_count = 0
                        in_string = False
                        escape = False
                        end_idx = -1
                        for idx, char in enumerate(buffer):
                            if char == '"' and not escape:
                                in_string = not in_string
                            elif char == '\\' and in_string:
                                escape = not escape
                                continue
                            elif not in_string:
                                if char == '{':
                                    brace_count += 1
                                elif char == '}':
                                    brace_count -= 1
                                    if brace_count == 0:
                                        end_idx = idx
                                        break
                            escape = False
                        
                        if end_idx != -1:
                            obj_str = buffer[:end_idx+1]
                            buffer = buffer[end_idx+1:]
                            try:
                                obj = json.loads(obj_str)
                                candidates = obj.get("candidates", [])
                                if candidates:
                                    parts = candidates[0].get("content", {}).get("parts", [])
                                    text = "".join(p.get("text", "") for p in parts)
                                    if text:
                                        yield json.dumps({"type": "content", "text": text}) + "\n"
                            except Exception:
                                pass
                        else:
                            break

        latency = time.perf_counter() - start_time
        yield json.dumps({"type": "meta", "latency": latency}) + "\n"

    except httpx.TimeoutException:
        yield json.dumps({"type": "error", "text": "Request timed out."}) + "\n"
    except Exception as e:
        yield json.dumps({"type": "error", "text": str(e)}) + "\n"
