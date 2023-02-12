# For work with browser
from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.options import Options
# For work with classes
from abc import ABC
# For work with html quries
import requests
from requests .sessions import Session


class Scraper(ABC):
    def get_chrome_options(self) -> Options:
        '''
        Get browser options.

        Returns
        -------
        Options
            Browser options.
        '''

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--remote-debugging-port=9222')
        chrome_options.add_argument('ignore-certificate-errors')
        return chrome_options

    def get_driver(self) -> WebDriver:
        '''
        Get webdriver.

        Returns
        -------
        WebDriver
            Webdriver.
        '''
        chrome_options = self.get_chrome_options()
        driver = webdriver.Chrome(options=chrome_options)
        driver.set_page_load_timeout(60)
        driver.set_window_size(1920, 1080)
        return driver

    def close_driver(self, driver: WebDriver) -> None:
        '''
        Close all open tabs and webdriver.

        Parameters
        ----------
        driver : WebDriver
            Webdriver.
        '''
        for handle in driver.window_handles:
            driver.switch_to.window(handle)
            driver.close()
        driver.quit()

    def get_session(self) -> Session:
        '''
        Get sesion for html queries.

        Returns
        -------
        Session
            Session.
        '''
        s = requests.Session()
        return s
