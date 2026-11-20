from scraper.communicator import Communicator


class DataSaver:
    def __init__(self) -> None:
        self.outputFormat = Communicator.get_output_format()

    def save(self, datalist):
        """
        This function will save the data that has been scrapped.
        This can be called if any error occurs while scraping, or if scraping is done successfully.
        In both cases we have to save the scraped data.
        """

        if len(datalist) > 0:
            Communicator.show_message("Saving the scraped data")

            Communicator.save_scraped_data(datalist)  # Save data in memory

            Communicator.show_message(f"Hello! Scraped data successfully saved! Total records saved: {len(datalist)}.")
        else:
            Communicator.show_error_message("Oops! Could not scrape the data because you did not scrape any record.", 'ds0')
