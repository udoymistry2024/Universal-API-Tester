# Universal API Tester v2.0 (Web Dashboard & Playground)

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![License: Proprietary](https://img.shields.io/badge/License-Proprietary-red.svg)](LICENSE)
[![Developer: Udoy Mistry](https://img.shields.io/badge/Developer-Udoy%20Mistry-00ff88.svg)](https://github.com/udoymistry)

Universal API Tester is a premium, lightweight, and extremely powerful **developer dashboard** designed to probe, diagnose, and test any supported API provider's credentials. It dynamically discovers active models, performs latency tests, generates report exports, and provides a full-featured real-time **Chat Playground** with advanced capabilities.

Designed with a cyber-futuristic **Matrix-Green Terminal HUD** aesthetic (complete with CRT monitor scanlines, glowing visual feedback, and custom searchable dropdown widgets), it brings the command-line vibe directly to your web browser.

---
Live Website URl: https://utestapi.onrender.com
---

## 🚀 Key Features

- **Double Scan Modes**:
  - ⚡ **Model Discovery**: Connects to providers' live endpoints, checks active model access, tests inference connection, and registers usable models.
  - 🔍 **Endpoint Diagnostic**: Runs concurrent diagnostics against provider endpoints to analyze latency, methods, and status warnings.
- **Dynamic Connection & Rate Control**: Highly configurable concurrency limits with exponential backoff on `HTTP 429` (Rate Limited) errors.
- **Futuristic Matrix Terminal UI**:
  - Rotating progress ring displaying live percentage.
  - Real-time logging console printing polling status messages (`[OK]`, `[ERR]`, `[WARN]`).
  - Searchable custom dropdown panels—no default browser `<select>` boxes.
- **Advanced SSE Chat Playground**:
  - 💬 **Real-time Streaming**: Word-by-word Server-Sent Events (SSE) token loading.
  - 🧠 **Thinking Separation**: Automatically parses and collapses DeepSeek R1 `<think>` reasoning details inside custom styled details boxes.
  - 📎 **Multi-File Uploads**: Attach up to 5 files (up to 50MB each) to feed text, configurations, or logs context directly into the prompt.
  - 🛑 **Immediate Interrupt**: Stop and cancel streaming completions instantly using a glowing Stop button.
  - 📋 **Code Canvas**: Premium dark markdown code boxes with a one-click **Copy** clipboard button.
- **17 Top Global Providers Supported**: Fully maps OpenAI, Anthropic, Google Gemini, Cohere, Perplexity, DeepInfra, Cerebras, OpenRouter, and more.
- **Persistent LocalStorage State**: Instantly saves configurations, keys, selected providers, and active scans so they persist across page refreshes.

---

## 🛠️ Installation & Quick Start

### Prerequisites
- **Python 3.12+**

### Steps
1. **Clone the repository**:
   ```bash
   git clone https://github.com/udoymistry/universal-ai-tester.git
   cd universal-ai-tester
   ```

2. **Create & activate a virtual environment**:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Launch the FastAPI Server**:
   ```bash
   uvicorn app.web.server:app --host 0.0.0.0 --port 8000 --reload
   ```

5. **Open Web HUD**:
   Go to `http://localhost:8000` in your web browser.

---

## 📖 Configuration

### API Key Preloading (`.env`)
Create a `.env` file in the root directory to preload your credentials. Preloaded keys will fill in automatically inside the Web UI config sidebar:
```env
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GEMINI_API_KEY=AIzaSy...
DEEPSEEK_API_KEY=sk-...
COHERE_API_KEY=...
PERPLEXITY_API_KEY=...
DEEPINFRA_API_KEY=...
# Check config.json.example for other keys mapping
```

---

## 🗂️ Project Documentation
For details on system files, directories, core concurrency algorithms, streaming SSE formats, custom markdown parsing patterns, and production server deployment scripts (Gunicorn, Systemd, Nginx), read the full [PROJECT_DETAILS.md](file:///home/udoy/Documents/universal-ai-tester/PROJECT_DETAILS.md) file.

---

## 🤝 Contributing & Extension
Adding new providers is incredibly easy. For details on subclassing `BaseProvider` or wrapping compatible APIs, check the **Developer Guide** inside the [PROJECT_DETAILS.md](file:///home/udoy/Documents/universal-ai-tester/PROJECT_DETAILS.md).

---

## 🔒 Copyright & License
- **Author/Developer**: [Udoy Mistry](https://github.com/udoymistry)
- © 2026 Udoy Mistry. All rights reserved.
- Distributed under a Proprietary License. See [LICENSE](LICENSE) for details.
