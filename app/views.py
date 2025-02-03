from flask import render_template, request, redirect, url_for, send_file
from datetime import datetime
from io import BytesIO
import openpyxl
from app import app
from scraper.communicator import Communicator
from scraper.scraper import Backend
import pandas as pd

@app.route('/')
def index():
    show_view_data_button = request.args.get('show_view_data_button', 'false') == 'true'
    has_existing_data = bool(Communicator.get_scraped_data())
    return render_template('index.html', show_view_data_button=show_view_data_button, has_existing_data=has_existing_data)

@app.route('/scrape', methods=['POST'])
def scrape():
    search_query = request.form.get('keyword', '').strip()
    location_query = request.form.get('location', '').strip()
    headless_mode = bool(request.form.get('headless'))

    if not search_query or not location_query:
        return redirect(url_for('index'))

    search_combined = f"{search_query} {location_query}"

    try:
        backend = Backend(
            searchquery=search_combined,
            outputformat='csv',
            headlessmode=headless_mode
        )
        
        backend.mainscraping()
        return redirect(url_for('index', show_view_data_button='true'))
    
    except Exception as e:
        error_message = str(e)
        Communicator.show_error_message(f"Scraping failed: {error_message}", "500")
        return redirect(url_for('index'))

@app.route('/view_data')
def view_data():
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 15

        latest_data = Communicator.get_scraped_data()
        
        if not latest_data:
            return render_template('view_data.html', data=[], next_url=None, prev_url=None)

        df = pd.DataFrame(latest_data)
        total_records = len(df)
        total_pages = (total_records + per_page - 1) // per_page
        page = max(1, min(page, total_pages))
        
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_data = df.iloc[start_idx:end_idx].to_dict('records')

        next_url = url_for('view_data', page=page + 1) if page < total_pages else None
        prev_url = url_for('view_data', page=page - 1) if page > 1 else None

        return render_template('view_data.html',
                             data=page_data,
                             next_url=next_url,
                             prev_url=prev_url,
                             current_page=page,
                             total_pages=total_pages,
                             total_records=total_records)

    except Exception as e:
        return render_template('view_data.html', data=[], next_url=None, prev_url=None)

@app.route('/download_data/<format>')
def download_data(format):
    try:
        latest_data = Communicator.get_scraped_data()

        if not latest_data:
            return redirect(url_for('view_data'))

        df = pd.DataFrame(latest_data)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        search_query = Communicator.get_search_query()
        if search_query:
            search_query = search_query.replace(' ', '_')
        else:
            search_query = 'google_maps_data'

        base_filename = f"{search_query}_{timestamp}"

        buffer = BytesIO()
        
        if format.lower() in ['excel', 'xlsx']:
            output_file = f"Google_Maps_Data_{base_filename}.xlsx"
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Google Maps Data')
            buffer.seek(0)
            mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        
        elif format == 'json':
            output_file = f"Google_Maps_Data_{base_filename}.json"
            buffer.write(df.to_json(orient='records', indent=4).encode('utf-8'))
            mimetype = 'application/json'
        
        else:
            output_file = f"Google_Maps_Data_{base_filename}.csv"
            buffer.write(df.to_csv(index=False).encode('utf-8'))
            mimetype = 'text/csv'

        buffer.seek(0)
        return send_file(
            buffer,
            mimetype=mimetype,
            as_attachment=True,
            download_name=output_file
        )

    except Exception as e:
        return redirect(url_for('view_data'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('error.html', error="Internal server error"), 500