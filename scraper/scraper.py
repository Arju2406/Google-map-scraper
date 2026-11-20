from time import sleep
from .base import Base
from .scroller import Scroller
import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .settings import DRIVER_EXECUTABLE_PATH, CHROME_BINARY_PATH
from .communicator import Communicator

class Backend(Base):
    def __init__(self, searchquery, outputformat, headlessmode):
        self.searchquery = searchquery
        # Cloud platforms have no display, so force headless mode there.
        self.headlessMode = headlessmode or bool(os.environ.get("RENDER"))
        self.init_driver()
        self.scroller = Scroller(driver=self.driver)
        self.init_communicator()

    def init_communicator(self):
        Communicator.set_backend_object(self)

    def init_driver(self):
        options = webdriver.ChromeOptions()

        if self.headlessMode:
            options.add_argument('--headless=new')

        # Chromium binary downloaded at build time on Render (if present).
        if CHROME_BINARY_PATH:
            options.binary_location = CHROME_BINARY_PATH

        prefs = {"profile.managed_default_content_settings.images": 2}
        options.add_experimental_option("prefs", prefs)

        # Flags required for running Chrome inside containers / as non-root.
        for flag in (
            "--no-sandbox",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--disable-setuid-sandbox",
            "--window-size=1920,1080",
            "--disable-blink-features=AutomationControlled",
        ):
            options.add_argument(flag)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])

        Communicator.show_message("Wait checking for driver...")

        if os.environ.get("RENDER") and CHROME_BINARY_PATH:
            # Selenium Manager resolves the correct driver for the bundled
            # Chromium without needing a separate webdriver-manager download.
            self.driver = webdriver.Chrome(options=options)
        else:
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=options)

        Communicator.show_message("Opening browser...")
        if not self.headlessMode:
            self.driver.maximize_window()
        self.driver.implicitly_wait(self.timeout)

    def mainscraping(self):
        try:
            querywithplus = "+".join(self.searchquery.split())

            link_of_page = f"https://www.google.com/maps/search/{querywithplus}/"

            self.openingurl(url=link_of_page)

            Communicator.show_message("Working start...")

            sleep(1)

            self.scroller.scroll()

        except Exception as e:
            Communicator.show_message(f"Error occurred while scraping. Error: {str(e)}")
        finally:
            try:
                Communicator.show_message("Closing the driver")
                self.driver.close()
                self.driver.quit()
            except:  # If the browser is already closed due to an error
                pass

            Communicator.end_processing()
            Communicator.show_message("Now you can start another session")
