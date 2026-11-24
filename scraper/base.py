from time import sleep
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import WebDriverException, TimeoutException
from .common import Common
from .communicator import Communicator


class Base:
    timeout = 60

    def openingurl(self, url: str):
        """Navigate to a URL, retrying a bounded number of times.

        Cloud IPs are commonly throttled by Google, which surfaces as
        WebDriverException / TimeoutException / raw connection timeouts.
        We retry a few times then give up instead of hanging forever.
        """
        max_retries = 3
        for attempt in range(max_retries):
            if Common.close_thread_is_set():
                self.driver.quit()
                return False

            try:
                self.driver.get(url)
                return True
            except (WebDriverException, TimeoutException, Exception):
                # Includes urllib3 "Read timed out" connection errors.
                if attempt == max_retries - 1:
                    Communicator.show_message(
                        "Could not load Google Maps (the request timed out or was blocked). "
                        "Note: cloud services like Render are frequently blocked by Google Maps."
                    )
                    return False
                sleep(3)
        return False

    def findelementwithwait(self, by, value):
        element = WebDriverWait(self.driver, self.timeout).until(
            EC.visibility_of_element_located((by, value))
        )
        return element
