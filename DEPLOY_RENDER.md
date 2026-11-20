# Deploying to Render

This project is now configured for deployment on Render as a Python Web Service.

## ⚠️ Important limitation

Google Maps actively blocks cloud/datacenter IP addresses (Render's IPs included).
Even with Chrome installed, scrapes started from Render will very likely hit
Google's "unusual traffic" / CAPTCHA wall and return no results. The web UI and
download features will work fine, but live scraping is unreliable from Render.
For reliable scraping, run the app locally (your home IP) or use a proxy.

## What was added / changed

- `render.yaml` — Render service definition (free plan, gunicorn start command).
- `render-build.sh` — build script: installs Python deps + downloads Chromium.
- `.render/install_chrome.py` — fetches a headless Chromium (no root needed).
- `scraper/settings.py` — locates the downloaded Chromium at runtime.
- `scraper/scraper.py` — headless + container-friendly Chrome flags on Render.

## Steps

### 1. Create a GitHub repository

Go to https://github.com/new and create a **new public repository** (e.g.
`google-map-scraper`). Do NOT initialize it with a README.

### 2. Push this project to it

Open PowerShell in this project folder and run (replace the URL with yours):

```powershell
git init -b main
git add .
git commit -m "Initial commit - Google Maps Scraper with Render config"
git remote add origin https://github.com/YOUR_USERNAME/google-map-scraper.git
git push -u origin main
```

### 3. Deploy on Render

1. Sign up / log in at https://render.com (GitHub sign-in is easiest).
2. Click **New +** → **Web Service**.
3. Connect your GitHub account and select the repo you just pushed.
4. Render should auto-detect `render.yaml` and pre-fill the settings.
   If it asks, set:
   - **Runtime:** Python
   - **Build Command:** `./render-build.sh`
   - **Start Command:** `gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 4 --timeout 300 app:app`
   - **Plan:** Free
5. Click **Create Web Service**.

### 4. Wait for the build

The first build downloads Chromium (~150 MB) and can take 5–10 minutes.
Watch the logs. Once it says "Your service is live", open the URL Render gives
you (e.g. `https://google-map-scraper.onrender.com`).

## Notes

- The free plan spins down after ~15 min of inactivity; the first request after
  that will be slow (cold start).
- `gunicorn` uses 1 worker because scraped data is stored in a module-level
  in-memory variable (`Communicator.__scraped_data`). Multiple workers would
  not share data. This is fine for a single-user demo, not for production.
