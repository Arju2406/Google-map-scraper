import time

from app import app
from scraper.communicator import Communicator

client = app.test_client()

# Health endpoint (used to wake the service after idle).
r = client.get("/health")
assert r.status_code == 200 and r.get_json()["status"] == "ok"
print("GET /health -> ok OK")

# GET /scrape must redirect home, not return a raw 405.
r = client.get("/scrape")
assert r.status_code == 302 and r.headers["Location"].endswith("/")
print("GET /scrape -> 302 OK")

# Status endpoint works and starts idle.
r = client.get("/scrape_status")
assert r.status_code == 200 and r.get_json()["status"] == "idle"
print("GET /scrape_status -> idle OK")

# Index renders.
assert client.get("/").status_code == 200
print("GET / -> 200 OK")

# Empty view_data renders.
assert client.get("/view_data").status_code == 200
print("GET /view_data (empty) -> 200 OK")

# Unsupported format redirects.
r = client.get("/download_data/badformat")
assert r.status_code == 302
print("GET bad format -> 302 OK")

# 404 handler.
assert client.get("/does-not-exist").status_code == 404
print("GET missing -> 404 OK")

# POST /scrape returns immediately (background thread) even without real Chrome.
# Patch Backend to a no-op so the test is fast and deterministic.
import app.views as views

class FakeBackend:
    def __init__(self, *a, **k):
        pass
    def mainscraping(self):
        from scraper.communicator import Communicator as C
        C.save_scraped_data([{"Name": "Fake", "Phone": "123"}])

orig_backend = views.Backend
views.Backend = FakeBackend
try:
    start = time.time()
    r = client.post("/scrape", data={"keyword": "x", "location": "y"})
    elapsed = time.time() - start
    assert r.status_code == 302 and elapsed < 1.0, (r.status_code, elapsed)
    print(f"POST /scrape -> 302 in {elapsed:.3f}s (async) OK")

    # Poll until the background job finishes.
    for _ in range(50):
        state = client.get("/scrape_status").get_json()
        if state["status"] in ("done", "error"):
            break
        time.sleep(0.05)
    assert state["status"] == "done", state
    assert state["has_data"] is True
    print("Background job -> done with data OK")
finally:
    views.Backend = orig_backend

# With data, view_data and downloads work.
r = client.get("/view_data")
assert r.status_code == 200 and b"Fake" in r.data
print("GET /view_data (with data) -> 200 OK")
for fmt in ("csv", "json", "excel"):
    r = client.get(f"/download_data/{fmt}")
    assert r.status_code == 200, (fmt, r.status_code)
    print(f"GET /download_data/{fmt} -> 200 OK")

# Index shows/hides the View Data button based on data.
assert b'id="view-data-button"' in client.get("/").data
Communicator.clear_scraped_data()
assert b'id="view-data-button"' not in client.get("/").data
print("View Data button show/hide OK")

print("ALL QUALITY TESTS PASSED")
