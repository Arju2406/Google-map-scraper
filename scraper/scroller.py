import os
import time
from .communicator import Communicator
from .common import Common
from bs4 import BeautifulSoup
from selenium.common.exceptions import JavascriptException, WebDriverException, TimeoutException


class Scroller:

    def __init__(self, driver) -> None:
        self.driver = driver
        # Cap the number of locations parsed on cloud hosts. Each location
        # requires a separate page load, which is slow and often blocked.
        self.max_results = 15 if os.environ.get("RENDER") else 10_000

    def __init_parser(self):
        # Import Parser here to avoid circular import
        from .parser import Parser
        self.parser = Parser(self.driver)

    def start_parsing(self):
        self.__init_parser()
        self.parser.main(self.__allResultsLinks[:self.max_results])

    def scroll(self):
        try:
            scrollAbleElement = self.driver.execute_script(
                """return document.querySelector("[role='feed']")"""
            )
        except (WebDriverException, TimeoutException, Exception):
            Communicator.show_message(
                "Google Maps did not load a results list. This often means the "
                "request was blocked (common on cloud services like Render)."
            )
            return

        if scrollAbleElement is None:
            Communicator.show_message(
                "No results found. Google Maps may be showing a consent/CAPTCHA "
                "page instead of results (common on cloud IPs)."
            )
            return

        Communicator.show_message(message="Starting scrolling")

        last_height = 0
        try:
            while True:
                if Common.close_thread_is_set():
                    self.driver.quit()
                    return

                scrollAbleElement = self.driver.execute_script(
                    """return document.querySelector("[role='feed']")"""
                )
                self.driver.execute_script(
                    "arguments[0].scrollTo(0, arguments[0].scrollHeight);",
                    scrollAbleElement,
                )
                time.sleep(2)

                new_height = self.driver.execute_script(
                    "return arguments[0].scrollHeight", scrollAbleElement
                )
                if new_height == last_height:
                    script = """
                    const endingElement = document.querySelector(".PbZDve ");
                    return endingElement;
                    """
                    endAlertElement = self.driver.execute_script(script)

                    if endAlertElement is None:
                        try:
                            self.driver.execute_script(
                                "array=document.getElementsByClassName('hfpxzc');array[array.length-1].click();"
                            )
                        except JavascriptException:
                            pass
                    else:
                        break
                else:
                    last_height = new_height
                    allResultsListSoup = BeautifulSoup(
                        scrollAbleElement.get_attribute('outerHTML'), 'html.parser'
                    )
                    allResultsAnchorTags = allResultsListSoup.find_all(
                        'a', class_='hfpxzc'
                    )
                    self.__allResultsLinks = [anchorTag.get(
                        'href') for anchorTag in allResultsAnchorTags]
                    Communicator.show_message(
                        f"Total locations scrolled: {len(self.__allResultsLinks)}"
                    )

                    # Stop early on cloud hosts to avoid excessive slow loads.
                    if os.environ.get("RENDER") and len(self.__allResultsLinks) >= self.max_results:
                        Communicator.show_message(
                            f"Reached the cloud-host limit of {self.max_results} locations."
                        )
                        break
        except (WebDriverException, TimeoutException, Exception) as e:
            Communicator.show_message(
                "Scrolling stopped because Google Maps did not respond in time "
                f"({str(e)[:120]}). This is common from cloud IPs."
            )

        if getattr(self, "_Scroller__allResultsLinks", None):
            self.start_parsing()
