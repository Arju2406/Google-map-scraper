import glob
import os

OUTPUT_PATH = "output/"  # Ensure this directory exists and is writable
DRIVER_EXECUTABLE_PATH = None


def get_chrome_binary():
    """Return the path to the downloaded Chromium binary, or None.

    Prefers Playwright's headless shell (smaller and far more stable in
    memory-constrained containers) over the full Chromium build.
    """
    if not os.environ.get("RENDER"):
        return None

    browsers_path = os.environ.get(
        "PLAYWRIGHT_BROWSERS_PATH",
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            ".render",
            "browsers",
        ),
    )

    # Prefer headless_shell, fall back to full chrome.
    candidates = glob.glob(
        os.path.join(browsers_path, "chromium_headless_shell-*", "chrome-linux*", "headless_shell")
    )
    candidates += glob.glob(
        os.path.join(browsers_path, "chromium_headless_shell-*", "chrome-linux*", "chrome")
    )
    candidates += glob.glob(
        os.path.join(browsers_path, "chromium-*", "chrome-linux*", "chrome")
    )
    return candidates[0] if candidates else None


CHROME_BINARY_PATH = get_chrome_binary()
