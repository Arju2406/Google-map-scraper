class Communicator:
    __frontend_object = None
    __backend_object = None
    __scraped_data = []

    # Background-job state (scraping runs off the HTTP request to avoid
    # Render's ~30s proxy request timeout).
    __status = "idle"  # idle | running | done | error
    __status_message = ""
    __error_message = ""

    @classmethod
    def show_message(cls, message):
        cls.__status_message = message
        if cls.__frontend_object is None:
            print(message)
        else:
            cls.__frontend_object.messageshowing(message)

    @classmethod
    def show_error_message(cls, message, error_code):
        cls.__status_message = message
        if cls.__frontend_object is None:
            print(f"{message} Error code is: {error_code}")
        else:
            message = f"{message} Error code is: {error_code}"
            cls.__frontend_object.messageshowing(message)

    @classmethod
    def set_frontend_object(cls, frontend_object):
        cls.__frontend_object = frontend_object

    @classmethod
    def end_processing(cls):
        if cls.__frontend_object is not None:
            cls.__frontend_object.end_processing()

    @classmethod
    def get_output_format(cls):
        return cls.__frontend_object.outputFormatValue if cls.__frontend_object else 'csv'

    @classmethod
    def set_backend_object(cls, backend_object):
        cls.__backend_object = backend_object

    @classmethod
    def get_search_query(cls):
        return cls.__backend_object.searchquery if cls.__backend_object else None

    @classmethod
    def save_scraped_data(cls, data):
        cls.__scraped_data = data

    @classmethod
    def clear_scraped_data(cls):
        """Discard results from a previous scrape when a new one begins."""
        cls.__scraped_data = []

    @classmethod
    def get_scraped_data(cls):
        return cls.__scraped_data

    # ---- Background job state helpers ----
    @classmethod
    def start_job(cls):
        cls.__status = "running"
        cls.__status_message = "Starting..."
        cls.__error_message = ""
        cls.clear_scraped_data()

    @classmethod
    def set_status(cls, status, message=None, error=None):
        cls.__status = status
        if message is not None:
            cls.__status_message = message
        if error is not None:
            cls.__error_message = error

    @classmethod
    def get_status(cls):
        return {
            "status": cls.__status,
            "message": cls.__status_message,
            "error": cls.__error_message,
            "has_data": bool(cls.__scraped_data),
        }
