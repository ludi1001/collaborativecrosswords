from scrapy.selector import Selector
from scrapy.http import HtmlResponse
import scrapy

class CrosswordSpider(scrapy.Spider):
    name = "crosswords"
    start_urls = ['https://myaccount.nytimes.com/auth/login']
    across_clues = {}
    down_clues = {}
    
    def parse(self, response):
        # pass in parguments via -a username -a password
        return scrapy.FormRequest.from_response(
            response,
            formid='login-form',
            formdata={'userid': self.username, 'password': self.password},
            callback=self.after_login
        )

    def after_login(self, response):
        yield scrapy.Request(url='https://www.nytimes.com/crosswords/game/mini/2017/05/06',
                             callback=self.parse_crossword)

    def parse_crossword(self, response):
        clues = response.xpath('//ol[@class="clue-list"]')
        across_clues_list = clues[0].xpath('li')
        down_clues_list = clues[1].xpath('li')
        across_clues_list_strings = clues[0].xpath('li//text()')
        down_clues_list_strings = clues[1].xpath('li//text()')

        for aclue, aclue_strings in zip(across_clues_list, across_clues_list_strings):
            self.across_clues[aclue.xpath('@value')[0].extract()] = aclue_strings.extract()

        for dclue, dclue_strings in zip(down_clues_list, down_clues_list_strings):
            self.down_clues[dclue.xpath('@value')[0].extract()] = dclue_strings.extract()

        print(self.across_clues)
        print(self.down_clues)
