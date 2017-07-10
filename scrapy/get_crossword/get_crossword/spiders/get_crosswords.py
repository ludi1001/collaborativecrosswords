from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy_splash import SplashRequest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import json
import scrapy

class CrosswordSpider(scrapy.Spider):
    name = "crosswords"
    start_url = 'https://myaccount.nytimes.com/auth/login'
    across_clues = {}
    down_clues = {}
    handle_httpstatus_list = [424]
    driver = webdriver.Chrome()

    def get_cookies(self):
        driver = self.driver
        driver.implicitly_wait(30)
        base_url = self.start_url
        driver.get(base_url)
        driver.find_element_by_id("username").clear()
        driver.find_element_by_id("username").send_keys(self.username)
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(self.password)
        driver.find_element_by_id("submitButton").click()
        cookies = driver.get_cookies()
        return cookies
    
    def start_requests(self):
            yield SplashRequest(
                self.start_url,
                self.parse,
                args={'wait': 0.5},
            )
                
    def parse(self, response):
        # pass in arguments via -a username -a password
        return scrapy.FormRequest.from_response(
            response,
            cookies=self.get_cookies(),
            formdata={"username":self.username, "password":self.password},
            callback=self.after_login)

    def after_login(self, response):
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "TopLeft")))

        crossword_url = 'https://www.nytimes.com/crosswords/game/mini/%s' % self.date
        self.driver.get(crossword_url)
        self.parse_crossword(
            HtmlResponse(
                self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8')
        )

    def parse_crossword(self, response):
        across_clues = response.xpath('//ol[@class="ClueList-list--236kf"]').extract_first()
        print(across_clues)
        self.driver.quit()
