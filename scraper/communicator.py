class Communicator:
    __frontend_object = None
    __backend_object = None
    __scraped_data = []

    @classmethod
    def show_message(cls, message):
        if cls.__frontend_object is None:
            print(message)
        else:
            cls.__frontend_object.messageshowing(message)

    @classmethod
    def show_error_message(cls, message, error_code):
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
    def get_scraped_data(cls):
        return cls.__scraped_data
