from app import app
from scraper.communicator import Communicator

client = app.test_client()

# GET /scrape must redirect home, not return a raw 405.
r = client.get("/scrape")
print("GET /scrape ->", r.status_code, "location:", r.headers.get("Location"))
assert r.status_code == 302 and r.headers["Location"].endswith("/")

# Index renders.
r = client.get("/")
print("GET / ->", r.status_code)
assert r.status_code == 200

# Empty view_data renders.
r = client.get("/view_data")
print("GET /view_data (empty) ->", r.status_code)
assert r.status_code == 200

# Unsupported download format redirects.
r = client.get("/download_data/badformat")
print("GET /download_data/badformat ->", r.status_code, r.headers.get("Location"))
assert r.status_code == 302

# 404 handler renders friendly page.
r = client.get("/does-not-exist")
print("GET /missing ->", r.status_code)
assert r.status_code == 404

# With data, view_data and all download formats work.
Communicator.save_scraped_data([{"Name": "Test", "Phone": "123"}])
r = client.get("/view_data")
print("GET /view_data (with data) ->", r.status_code, "has Test:", b"Test" in r.data)
assert r.status_code == 200 and b"Test" in r.data
for fmt in ("csv", "json", "excel"):
    r = client.get(f"/download_data/{fmt}")
    print(f"GET /download_data/{fmt} ->", r.status_code, r.headers.get("Content-Type"))
    assert r.status_code == 200

# Index shows the View Data button when data exists.
r = client.get("/")
print("index with data shows button:", b"view-data-button" in r.data)
assert b"view-data-button" in r.data

# Clearing data removes the button.
Communicator.clear_scraped_data()
r = client.get("/")
print("index after clear shows button:", b"view-data-button" in r.data)
assert b"view-data-button" not in r.data

print("ALL QUALITY TESTS PASSED")
