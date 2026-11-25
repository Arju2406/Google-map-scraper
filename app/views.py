import logging
from datetime import datetime
from io import BytesIO

import pandas as pd
from flask import (
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)

from app import app
from scraper.communicator import Communicator
from scraper.scraper import Backend

logger = logging.getLogger(__name__)

# Successful scrape formats supported by the download endpoint.
DOWNLOAD_FORMATS = {"csv", "json", "excel", "xlsx"}


@app.route("/")
def index():
    # The button is driven by real in-memory data, not a spoofable query flag.
    # Data is cleared at the start of each new scrape, so it disappears while
    # a new scrape is running or after a failure.
    has_existing_data = bool(Communicator.get_scraped_data())
    return render_template("index.html", has_existing_data=has_existing_data)


@app.route("/scrape", methods=["POST"])
def scrape():
    search_query = request.form.get("keyword", "").strip()
    location_query = request.form.get("location", "").strip()
    headless_mode = bool(request.form.get("headless"))

    if not search_query or not location_query:
        flash("Please provide both a keyword and a location.", "error")
        return redirect(url_for("index"))

    search_combined = f"{search_query} {location_query}"

    # A new scrape invalidates results from the previous one. Clear them so
    # the "View Data" button never points to stale data while this runs.
    Communicator.clear_scraped_data()

    try:
        backend = Backend(
            searchquery=search_combined,
            outputformat="csv",
            headlessmode=headless_mode,
        )
        backend.mainscraping()

        if not Communicator.get_scraped_data():
            flash(
                "Scraping finished but no places were found. Google Maps may be "
                "showing a consent/CAPTCHA page (common on cloud services like "
                "Render). Please try again or run locally.",
                "error",
            )
            return redirect(url_for("index"))

        flash("Scraping completed successfully.", "success")
        return redirect(url_for("index"))
    except Exception as exc:
        logger.exception("Scraping failed")
        Communicator.show_error_message(f"Scraping failed: {exc}", "500")
        flash(
            "Scraping could not complete. If you are using the hosted (Render) "
            "version, note that Google Maps frequently blocks cloud services. "
            "Try running the app locally, or retry in a few minutes.",
            "error",
        )
        return redirect(url_for("index"))


@app.route("/scrape", methods=["GET"])
def scrape_get():
    # Avoid a raw 405 when someone opens /scrape directly in a browser.
    flash("Please submit the scraping form from the home page.", "error")
    return redirect(url_for("index"))


@app.route("/view_data")
def view_data():
    try:
        page = request.args.get("page", 1, type=int)
        per_page = 15

        latest_data = Communicator.get_scraped_data()
        if not latest_data:
            return render_template(
                "view_data.html", data=[], next_url=None, prev_url=None
            )

        df = pd.DataFrame(latest_data)
        total_records = len(df)
        total_pages = max(1, (total_records + per_page - 1) // per_page)
        page = max(1, min(page, total_pages))

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_data = df.iloc[start_idx:end_idx].to_dict("records")

        next_url = url_for("view_data", page=page + 1) if page < total_pages else None
        prev_url = url_for("view_data", page=page - 1) if page > 1 else None

        return render_template(
            "view_data.html",
            data=page_data,
            next_url=next_url,
            prev_url=prev_url,
            current_page=page,
            total_pages=total_pages,
            total_records=total_records,
        )
    except Exception:
        logger.exception("Failed to render view_data")
        return render_template("view_data.html", data=[], next_url=None, prev_url=None)


@app.route("/download_data/<format>")
def download_data(format):
    fmt = format.lower()
    if fmt not in DOWNLOAD_FORMATS:
        flash("Unsupported download format.", "error")
        return redirect(url_for("view_data"))

    try:
        latest_data = Communicator.get_scraped_data()
        if not latest_data:
            return redirect(url_for("view_data"))

        df = pd.DataFrame(latest_data)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        search_query = Communicator.get_search_query()
        search_query = (
            search_query.replace(" ", "_") if search_query else "google_maps_data"
        )
        base_filename = f"{search_query}_{timestamp}"

        buffer = BytesIO()

        if fmt in ("excel", "xlsx"):
            output_file = f"Google_Maps_Data_{base_filename}.xlsx"
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df.to_excel(writer, index=False, sheet_name="Google Maps Data")
            buffer.seek(0)
            mimetype = (
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        elif fmt == "json":
            output_file = f"Google_Maps_Data_{base_filename}.json"
            buffer.write(df.to_json(orient="records", indent=4).encode("utf-8"))
            mimetype = "application/json"
        else:
            output_file = f"Google_Maps_Data_{base_filename}.csv"
            buffer.write(df.to_csv(index=False).encode("utf-8"))
            mimetype = "text/csv"

        buffer.seek(0)
        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=output_file,
        )
    except Exception:
        logger.exception("Failed to download data")
        return redirect(url_for("view_data"))


@app.errorhandler(404)
def not_found_error(error):
    return render_template("error.html", error="Page not found"), 404


@app.errorhandler(405)
def method_not_allowed_error(error):
    flash("That action is not allowed from here.", "error")
    return redirect(url_for("index"))


@app.errorhandler(500)
def internal_error(error):
    return render_template("error.html", error="Internal server error"), 500
