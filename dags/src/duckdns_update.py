# For work with airflow
from airflow.models import Variable
# For work with time
import time
# For work with browser
from selenium.webdriver.common.by import By
# For scraping
from .scraper import Scraper
# Search by html
from bs4 import BeautifulSoup
# For work with regular expression
import re


class DuckDnsUpdater(Scraper):
    def __init__(self):
        super().__init__()
        self.router_ip = Variable.get('router_ip')
        self.router_url = f"http://{self.router_ip}/"
        self.router_password = Variable.get('router_password')
        self.duck_domain = Variable.get('duck_domain')
        self.duck_tocken = Variable.get('duck_tocken')
        self.ip_pattern = re.compile(r'[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}')

    def get_external_ip(self) -> str:
        driver = self.get_driver()
        driver.get(self.router_url)
        time.sleep(10)
        # Set password
        driver.find_elements(
            by=By.XPATH,
            value='/html/body/div[1]/div[2]/div[1]/div[1]/div/form[2]/div[2]/div/div/div[1]/span[2]/input[1]'
        )[0].send_keys(self.router_password)
        driver.save_screenshot('test1.png')
        # Press on button
        driver.find_elements(by=By.XPATH, value='//*[@id="login-btn"]')[0].click()
        time.sleep(10)
        driver.save_screenshot('test2.png')
        # Search on html
        # Отдельная функция
        soup = BeautifulSoup(driver.page_source)
        for i in soup.find_all('span', {'class': 'text-wrap'}):
            ip_list = self.ip_pattern.findall(str(i))
            if [i for i in ip_list if i != '0.0.0.0']:
                return ip_list[0]

    def update_duckdns(self) -> None:
        external_ip = self.get_external_ip()
        s = self.get_session()
        if external_ip:
            # Передть в переменные в самом начале
            params = {
                'domains': self.duck_domain,
                'token': self.duck_tocken,
                'ip': external_ip,
            }
            r = s.get(url='https://www.duckdns.org/update', params=params)
            if r.status_code != 200 and r.decode("utf-8") != 'ОК':
                raise ValueError('Error in query')
        else:
            raise ValueError('No external IP')
        s.close()
