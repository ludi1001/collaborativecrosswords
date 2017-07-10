from scrapy.selector import Selector
from scrapy.http import HtmlResponse
from scrapy_splash import SplashRequest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

import json
import re
import scrapy

class CrosswordSpider(scrapy.Spider):
    name = "crosswords"
    start_url = 'https://myaccount.nytimes.com/auth/login'
    across_clues = {}
    down_clues = {}
    grid = []
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

        crossword_url = 'https://www.nytimes.com/crosswords/game/daily/%s' % self.date
        self.driver.get(crossword_url)
        self.parse_crossword(
            HtmlResponse(
                self.driver.current_url,
                body=self.driver.page_source,
                encoding='utf-8')
        )

    def parse_crossword(self, response):
        soup = BeautifulSoup(response.body, 'html.parser')
        clues_list = soup.find_all('ol')
        across = clues_list[0]
        a_clues = across.find_all('li')
        down = clues_list[1]
        d_clues = down.find_all('li')
        for clue in a_clues:
            label = clue.find("span", {"class" : re.compile('Clue-label')}).text
            text = clue.find("span", {"class" : re.compile('Clue-text')}).text
            self.across_clues[label] = text
        for clue in d_clues:
            label = clue.find("span", {"class" : re.compile('Clue-label')}).text
            text = clue.find("span", {"class" : re.compile('Clue-text')}).text
            self.down_clues[label] = text

        print(self.across_clues)
        print(self.down_clues)
        cells = soup.find("g", {"class": "cells"}).find_all("g")
        row = []
        curr_path = 0
        for cell in cells:
            texts = cell.find_all("text")
            path = cell.find_all("path")
            path_data = float(path[0]["d"][1:].split(" ")[0])
            if path_data < curr_path:
                self.grid.append(row)
                print(row)
                curr_path = path_data
                row = []
            if len(texts) == 0: # cell is not used
                row.append("x")
            elif len(texts) >= 1:    
                if len(texts) == 1: # If the cell is empty
                    row.append(0)
                    curr_path = path_data
                elif len(texts) == 2: # If the cell contains number
                    row.append(texts[0].text)
                    curr_path = path_data
        self.grid.append(row)
        print(row)
        #print(self.grid)
        self.driver.quit()

if __name__ == "__main__":
    CrosswordSpider().parse_crossword()
