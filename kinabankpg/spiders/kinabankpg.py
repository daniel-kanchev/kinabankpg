import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from kinabankpg.items import Article


class kinabankpgSpider(scrapy.Spider):
    name = 'kinabankpg'
    start_urls = ['https://www.kinabank.com.pg/news/']

    def parse(self, response):
        articles = response.xpath('//div[@class="news-loop-item flex-height"]')
        for article in articles:
            link = article.xpath('.//a[@class="read-more-link"]/@href').get()
            if not link:
                return
            date = article.xpath('.//h4/text()').get()
            if date:
                date = " ".join(date.split())

            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="next page-numbers"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url.lower():
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@data-elementor-type="wp-post"]//text()').getall() or response.xpath('//div[@class="col-md-8"]//text()').getall()
        content = [text.strip() for text in content if text.strip() and '{' not in text]
        content = " ".join(content).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
