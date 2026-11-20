#!/usr/bin/env bash
# Build script for Render: installs Python deps plus a headless Chrome/Chromium
# so Selenium-based scraping has a browser available at runtime.
set -euo pipefail

echo "==> Installing Python dependencies"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

echo "==> Installing Chromium + system dependencies"
# Render's Python images are Debian-based and run builds as a non-root user,
# so apt-get is not available. Use the official chrome-for-testing download
# which unpacks into a local directory with no root privileges required.
python .render/install_chrome.py

echo "==> Build complete"
