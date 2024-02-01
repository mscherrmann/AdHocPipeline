import sys
import re
import os
from urllib import request
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager



class Crawler:
    """
    A class used to crawl Ad-Hoc news from the website
    "https://www.unternehmensregister.de"

    ...

    Attributes
    ----------
    start_date : str
        the start date of the observation period
        (given in the format dd.mm.yyyy)
    end_date : str
        the end date of the observation period (given in the format dd.mm.yyyy)


    Methods
    -------
    crawl()
        Crawls and saves the html files into the folder
        "C:/Users/scherrmann/Documents/Textanalyse_Projekt/
        Ad_Hoc_Meldungen_Unternehmensregister_(+language)"
    """

    def __init__(self,
                 start_page: int = 1,
                 start_index: int = 1,
                 language: str = "de",
                 is_test_mode: bool = False):
        """
        Parameters
        ----------
        start_page : int
            The page where the crawling should start (default is 1)
        start_index : int
            Given a page, define at which document on that page the
            crawling should start (default is 1)
        language : str
            Specify the language (default is "de"):
                "de" : german
                "en" : English
        is_test_mode : bool
         Flag to indicate whether to use pipeline in test mode or not
        """
        self.__page_counter = start_page
        self.__page_index = start_index
        self.__language = language
        self.__is_test_mode = is_test_mode

        if self.__is_test_mode:
            self.__path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "tests",
                "data",
                "AdHocHtml",
                language)
        else:
            self.__path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                "data",
                "AdHocHtml",
                language)
        # Counter: Counts number of files that are downloaded in actual run
        self.__counter = 1
        # Exception counter: Counts the number of exceptions on one file
        self.__exception_counter = 1
        # Exception threshold: Threshold of number of retry downloading
        # file where exception occurs. If exceeeded, error is thrown
        self.__exception_th = 5

    def crawl(self, start_date, end_date):
        """
        Parameters
        ----------
        start_date : str
            the start date of the observation period
            (given in the format dd.mm.yyyy)
        end_date : str
            the end date of the observation period
            (given in the format dd.mm.yyyy)
        """
        # Start driver
        self.__driver = self.__start_web_driver()
        start = time.time()
        self.__startpage_navigation(start_date, end_date)
        self.__go_to()

        while self.__page_counter <= self.n_pages:
            # Alle Ad-Hoc-Meldungen auf der Seite
            ad_hoc_links = self.__driver.find_elements(
                By.PARTIAL_LINK_TEXT, 'Ad-')
            while self.__page_index <= len(ad_hoc_links):
                try:
                    url = ad_hoc_links[self.__page_index-1]\
                        .get_attribute("href")
                    doc_id = re.findall(r"\&id=(\d+)$", url)
                    response = request.urlopen(url)
                    html = response.read()
                    with open(
                            os.path.join(self.__path, doc_id[0]+'.html'),
                            'w') as file:
                        file.write(html.decode('utf-8'))
                    self.__page_index += 1
                    self.__counter += 1
                    self.__exception_counter = 0
                except KeyboardInterrupt:
                    raise
                except:
                    self.__print_error(sys.exc_info(), start_date, end_date)
                    self.__driver.quit()
                    os.system('taskkill /IM chrome.exe /F')
                    self.__exception_counter += 1
                    if self.__exception_counter == self.__exception_th:
                        raise
                    time.sleep(10)
                    # Start again
                    self.__driver = self.__start_web_driver()
                    self.__startpage_navigation(start_date, end_date)
                    self.__go_to()
            print(f"{start_date} - {end_date}: Completed Page Nr. "
                  f"{self.__page_counter} of {self.n_pages} after "
                  f"{(time.time() - start) / 60:02.2f} minutes."
                  )

            self.__page_counter += 1
            self.__page_index = 1
            if self.__page_counter <= self.n_pages:
                self.__go_to()

        # Reset params
        self.__page_counter = 1
        self.__page_index = 1
        self.__counter = 1
        self.__exception_counter = 1
        self.__driver.quit()

    def __startpage_navigation(self, start_date, end_date):

        try:
            # Navigate to the start page of 'unternehmensregister'
            self.__driver.get("https://www.unternehmensregister.de")

            # Maximize window size
            self.__driver.maximize_window()

            # Accept cookies
            self.__driver.find_element(By.ID, "cc_all").click()

            # Click on 'Menü'
            self.__driver.find_element(By.CLASS_NAME, "menu__toggle").click()

            # Click on 'Kapitalmarktinformationen'
            self.__driver.find_element(
                By.XPATH, '//a[contains(@href, "search1.6.html")]').click()

            # Click on 'Sprache'
            self.__driver.find_element(
                By.ID,
                "select2-searchRegisterFormpublicationsOfCapital" +
                "InvestmentsLanguage-container").click()

            # Insert language "Deutsch" or "Englisch"
            corp_element = self.__driver.find_element(
                By.CLASS_NAME,
                "select2-search__field")
            corp_element.send_keys(self.__language)
            corp_element.send_keys(Keys.ENTER)

            # Click on 'Bereich'
            self.__driver.find_element(
                By.ID,
                "select2-searchRegisterFormpublicationsOfCapital"
                "InvestmentsCategory-container").click()

            # Insert "Insiderinformationen"
            corp_element = self.__driver.find_element(
                By.CLASS_NAME,
                "select2-search__field")
            corp_element.send_keys("Insider­informationen")
            corp_element.send_keys(Keys.ENTER)

            # Fix start date
            startdate_element = self.__driver.find_element(
                By.ID,
                "searchRegisterForm:publicationsOfCapital"
                "InvestmentsPublicationsStartDate")
            startdate_element.clear()
            startdate_element.send_keys(start_date)

            # Fix end date
            enddate_element = self.__driver.find_element(
                By.ID,
                "searchRegisterForm:publicationsOfCapital"
                "InvestmentsPublicationsEndDate")
            enddate_element.clear()
            enddate_element.send_keys(end_date)

            # Start search
            self.__driver.find_element(By.XPATH,
                                       "//input[@type='submit' and "
                                       "@value='Suchen']").click()

            # Get number of pages
            num_pages_element = self.__driver.find_element(
                By.CLASS_NAME,
                "page_count")
            element_text = num_pages_element.get_attribute('innerHTML')
            self.n_pages = int(re.search(r"^\d+", element_text).group())
        except:
            self.__print_error(
                sys.exc_info(),
                start_date,
                end_date,
                is_start_page=True)
            self.__driver.quit()
            os.system('taskkill /IM chrome.exe /F')
            self.__exception_counter += 1
            if self.__exception_counter == self.__exception_th:
                raise
            time.sleep(10)
            # Start again
            self.__driver = self.__start_web_driver()
            self.__startpage_navigation(start_date, end_date)
        self.__exception_counter = 1

    def __go_to(self):
        # Begin crawling with specified start page and start index
        if self.__page_counter > 1:
            base_url = self.__driver.current_url
            append_url = "?submitaction=pathnav&page." + \
                str(self.__page_counter) + "=page"
            question_mark_position = base_url.find('?')
            if question_mark_position == -1:
                url = base_url + append_url
            else:
                url = base_url[:question_mark_position] + append_url
            self.__driver.get(url)

    def __session_time_out(self):
        text = self.__driver.page_source
        searchstr = 'Sie befinden sich auf dieser' + \
            ' Webseite in einer so genannten'
        return text.find(searchstr) >= 0

    def __start_web_driver(self):
        options = webdriver.ChromeOptions()
        # Run in headless mode, without a UI or display server dependencies
        # options.add_argument('--headless')
        # Bypass OS security model, MUST BE THE VERY FIRST OPTION
        options.add_argument('--no-sandbox')
        # Overcome limited resource problems
        options.add_argument('--disable-dev-shm-usage')
        return webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options)

    def __print_error(self, error, start_date, end_date, is_start_page=False):
        if is_start_page:
            print("Exception during start page navigation occurred")
        else:
            print("Exception during crawling process occurred")
        print(f"Exception class: {error[0]}")
        print(f"Exception instance: {error[1]}")
        print(f"Exception traceback: {error[2]}")
        print(f"Start date: {start_date}")
        print(f"End date: {end_date}")
        print(f"Page: {self.__page_counter}")
        print(f"Index: {self.__page_index}")
        print(f"Exception counter: {self.__exception_counter}\n")
