"""Download a headless Chromium browser into the project (no root needed).

Uses Playwright's browser downloader because it works in Render's unprivileged
build environment. At runtime scraper/settings.py points Selenium at this
browser and uses Selenium Manager / webdriver-manager for the matching driver.
"""
import os
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BROWSERS_DIR = os.path.join(PROJECT_ROOT, ".render", "browsers")
os.makedirs(BROWSERS_DIR, exist_ok=True)

# Keep the downloaded browser inside the project so it is shipped to runtime.
os.environ.setdefault("PLAYWRIGHT_BROWSERS_PATH", BROWSERS_DIR)

print("==> Installing Playwright (used only to fetch Chromium)")
subprocess.check_call([sys.executable, "-m", "pip", "install", "playwright==1.49.1"])

print("==> Downloading Chromium into", BROWSERS_DIR)
subprocess.check_call(
    [sys.executable, "-m", "playwright", "install", "chromium"]
)

print("==> Chromium download complete")
