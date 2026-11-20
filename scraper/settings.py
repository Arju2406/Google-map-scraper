import glob
import os

OUTPUT_PATH = "output/"  # Ensure this directory exists and is writable
DRIVER_EXECUTABLE_PATH = None

# On Render we download Chromium via Playwright during the build. Locate the
# binary so Selenium can launch it. On local machines this resolves to None and
# Selenium uses the system-installed Chrome.
def get_chrome_binary():
    """Return the path to the downloaded Chromium binary, or None."""
    if os.environ.get("RENDER"):
        browsers_path = os.environ.get(
            "PLAYWRIGHT_BROWSERS_PATH",
            os.path.join(
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                ".render",
                "browsers",
            ),
        )
        candidates = glob.glob(
            os.path.join(browsers_path, "chromium-*", "chrome-linux*", "chrome")
        )
        candidates += glob.glob(
            os.path.join(browsers_path, "chromium_headless_shell-*", "chrome-linux*", "headless_shell")
        )
        if candidates:
            return candidates[0]
    return None

CHROME_BINARY_PATH = get_chrome_binary()
