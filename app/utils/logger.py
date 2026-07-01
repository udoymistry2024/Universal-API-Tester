import os
import logging
from pathlib import Path

# Ensure logs directory exists
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

logger = logging.getLogger("universal_ai_tester")
logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(LOGS_DIR / "scanner.log", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Formatter
formatter = logging.Formatter(
    "%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

# Prevent duplicate logs if re-imported
logger.propagate = False

def log_scan_start(provider_name: str):
    logger.info("==========================================")
    logger.info(f"Starting API scan for provider: {provider_name}")

def log_model_test(provider_id: str, model_id: str, status: str, latency: float, error_message: str = None):
    err_str = f" | Error: {error_message}" if error_message else ""
    logger.info(
        f"Provider: {provider_id} | Model: {model_id} | Status: {status} | Latency: {latency:.4f}s{err_str}"
    )

def log_scan_end(provider_name: str, total: int, working: int, failed: int):
    logger.info(
        f"Completed scan for {provider_name}. Total models: {total} | Working: {working} | Failed: {failed}"
    )
    logger.info("==========================================")

def log_error(provider_id: str, message: str):
    logger.error(f"Provider: {provider_id} | Error: {message}")
