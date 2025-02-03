from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .error_codes import ERROR_CODES
from .communicator import Communicator
from .datasaver import DataSaver
from .base import Base
from .common import Common
import time

class Parser(Base):

    def __init__(self, driver) -> None:
        self.driver = driver
        self.finalData = []
        self.comparing_tool_tips = {
            "location": "Copy address",
            "phone": "Copy phone number",
            "website": "Open website",
            "booking": "Open booking link",
        }

    def init_data_saver(self):
        self.data_saver = DataSaver()

    def parse(self):
        retries = 5
        infoSheet = None
        while retries > 0:
            try:
                infoSheet = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "[role='main']"))
                )
                break
            except:
                retries -= 1
                time.sleep(2)

        if not infoSheet:
            Communicator.show_error_message("Info sheet not found", ERROR_CODES['ERR_WHILE_PARSING_DETAILS'])
            return

        try:
            data = {
                "Category": None,
                "Name": None,
                "Phone": None,
                "Google Maps URL": None,
                "Website": None,
                "Business Status": None,
                "Address": None,
                "Total Reviews": None,
                "Booking Links": None,
                "Rating": None,
                "Hours": None,
            }

            html = infoSheet.get_attribute("outerHTML")
            soup = BeautifulSoup(html, "html.parser")

            try:
                data["Rating"] = soup.find("span", class_="ceNzKf").get("aria-label").replace("stars", "").strip()
            except:
                pass
            try:
                totalReviews = list(soup.find("div", class_="F7nice").children)
                data["Total Reviews"] = totalReviews[1].get_text(strip=True)
            except:
                pass
            try:
                data["Name"] = soup.select_one(".tAiQdd h1.DUwDvf").text.strip()
            except:
                pass
            try:
                allInfoBars = soup.find_all("button", class_="CsEnBe")
                for infoBar in allInfoBars:
                    data_tooltip = infoBar.get("data-tooltip")
                    text = infoBar.find('div', class_='rogA2c').text.strip()
                    if data_tooltip == self.comparing_tool_tips["location"]:
                        data["Address"] = text
                    elif data_tooltip == self.comparing_tool_tips["phone"]:
                        data["Phone"] = text.strip()
            except:
                pass
            try:
                websiteTag = soup.find("a", {"aria-label": lambda x: x and "Website:" in x})
                if websiteTag:
                    data["Website"] = websiteTag.get("href")
            except:
                pass
            try:
                bookingTag = soup.find("a", {"aria-label": lambda x: x and "Open booking link" in x})
                if bookingTag:
                    data["Booking Links"] = bookingTag.get("href")
            except:
                pass
            try:
                data["Hours"] = soup.find("div", class_="t39EBf").get_text(strip=True)
            except:
                pass
            try:
                data["Category"] = soup.find("button", class_="DkEaL").text.strip()
            except:
                pass
            try:
                data["Google Maps URL"] = self.driver.current_url
            except:
                pass
            try:
                data["Business Status"] = soup.find("span", class_="ZDu9vd").findChildren("span", recursive=False)[0].get_text(strip=True)
            except:
                pass
            
            self.finalData.append(data)
            
        except Exception as e:
            Communicator.show_error_message(f"Error occurred while parsing a location. Error is: {str(e)}", ERROR_CODES['ERR_WHILE_PARSING_DETAILS'])
        
    def main(self, allResultsLinks):
        Communicator.show_message("Scrolling is done. Now going to scrape each location")
        try:
            for resultLink in allResultsLinks:
                if Common.close_thread_is_set():
                    # Check if the cancellation flag is set, and exit early if it is
                    break

                self.openingurl(url=resultLink)
                self.parse()

        except Exception as e:
            Communicator.show_message(f"Error occurred while parsing the locations. Error: {str(e)}")

        finally:
            self.init_data_saver()
            self.data_saver.save(datalist=self.finalData)
