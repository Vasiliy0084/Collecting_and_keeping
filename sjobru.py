import scrapy
from scrapy.http import HtmlResponse
from jobparser.items import JobparserItem

class SjobruSpider(scrapy.Spider):
    name = 'sjobru'
    allowed_domains = ['superjob.ru']
    start_urls = ['https://russia.superjob.ru/vacancy/search/?keywords=data']

    def parse(self, response: HtmlResponse):
        next_page = response.xpath("//a[@class='icMQ_ bs_sM _3ze9n _2Pv5x f-test-button-dalshe f-test-link-Dalshe']/@href").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse)
        links = response.xpath("//div[@class='_2rfUm _2hCDz _21a7u']/a[@target='_blank']/@href").getall()
        for link in links:
            yield response.follow(link, callback=self.vacancy_parse)

    def vacancy_parse(self, response: HtmlResponse):
        name = response.xpath("//h1[@class='rFbjy _2dazi _2hCDz _1RQyC']/text()").get()
        salary = response.xpath("//span[@class='_2Wp8I _2rfUm _2hCDz']/text()").getall()
        company = response.xpath("//h2[@class='_2rfUm _2hCDz _2ZsgW _21a7u _2SvHc']/text()").get()
        link = response.url
        item = JobparserItem(name=name, salary=salary, company=company, link=link)
        yield item