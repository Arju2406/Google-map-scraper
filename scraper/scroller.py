import time
from .communicator import Communicator
from .common import Common
from bs4 import BeautifulSoup
from selenium.common.exceptions import JavascriptException

class Scroller:

    def __init__(self, driver) -> None:
        self.driver = driver
    
    def __init_parser(self):
        # Import Parser here to avoid circular import
        from .parser import Parser
        self.parser = Parser(self.driver)

    def start_parsing(self):
        self.__init_parser()
        self.parser.main(self.__allResultsLinks)

    def scroll(self):
        scrollAbleElement = self.driver.execute_script(
            """return document.querySelector("[role='feed']")"""
        )
        if scrollAbleElement is None:
            Communicator.show_message(message="We are sorry but, No results found for your search query on Google Maps.")
        else:
            Communicator.show_message(message="Starting scrolling")

            last_height = 0

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
                    script = f"""
                    const endingElement = document.querySelector(".PbZDve ");
                    return endingElement;
                    """
                    endAlertElement = self.driver.execute_script(
                        script
                    )

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
                    
                    Communicator.show_message(f"Total locations scrolled: {len(self.__allResultsLinks)}")

            self.start_parsing()
