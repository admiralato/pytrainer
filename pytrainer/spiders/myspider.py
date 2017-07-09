from scrapy.contrib.spiders import CrawlSpider, Rule, BaseSpider
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.http import Request

from scrapy.selector import Selector

from pytrainer.items import PytrainerItem
from pytrainer.apputil.string_util import StringUtil

import validators
import csv


class MySpider(CrawlSpider):
    name = "trainer"
    allowed_domains = ["6pm.com"]
    start_urls = ['http://www.6pm.com/swimsuit-bottoms',
    'http://www.6pm.com/swimsuit-bottoms-page2/.zso?t=swimsuit+bottoms&p=1',
    'http://www.6pm.com/swimsuit-bottoms-page3/.zso?t=swimsuit+bottoms&p=2',
    'http://www.6pm.com/swimsuit-bottoms-men/wAEC4gIBGA.zso?t=swimsuit+bottoms',
    'http://www.6pm.com/swimsuit-bottoms-men-clothing-page2/CKvXAcABAuICAhgB.zso?t=swimsuit+bottoms&p=1',
    'http://www.6pm.com/swimsuit-bottoms-men-swimwear-page3/CKvXARDR1wHAAQLiAgMYAQI.zso?t=swimsuit+bottoms&p=2',
    'http://www.6pm.com/swimsuit-bottoms-men-swimwear-page4/CKvXARDR1wHAAQLiAgMYAQI.zso?t=swimsuit+bottoms&p=3',
    'http://www.6pm.com/swimsuit-bottoms-boys/wAEE4gIBGA.zso?t=swimsuit+bottoms']

    # Pass the pagination xpath
    rules = (Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//div[@class="pagination"]',)),
                  callback="parse",
                  follow=True),)

    def parse(self, response):
        # hxs = HtmlXPathSelector(response)
        sel = Selector(response)
        # Search results container
        urls = sel.xpath('//div[@id="searchResults"]/a')  # 6PM
        # urls = sel.xpath('//*[@id="searchProductResult"]//a[@itemprop="url"]') # Walmart
        # urls = sel.xpath('//*[@class="search-result-gridview-items"]/li//a[@itemprop="url"]')  # Walmart
        # urls = sel.xpath('//script[text()[contains(., "userName")]]') # Walmart
        # urls = sel.xpath('//*[@id="rightResultsATF"]//ul/li//a') # Amazon

        for url in urls:
            item = PytrainerItem()
            item['category'] = "swimsuit bottoms"
            # Extract JSON from Walmart
            # json_string = ''.join(url.xpath('text()').extract())
            # json_string = json_string.replace("window.__WML_REDUX_INITIAL_STATE__ =", "")
            # json_string = json_string[:-1]
            #
            # json_preso = json.loads(json_string)
            # items = json_preso['preso']['items']
            # for product in items:
            #     # print('ITEM: %s' % product['productPageUrl'])
            #     url = product['productPageUrl']
            #     if not validators.url(url):
            #         url = 'https://www.walmart.com{}'.format(''.join(url))
            #         yield Request(url=url, meta={'item': item}, callback=self.parse_item_page)
            # End of extraction

            item_url = ''.join(url.xpath("@href").extract())
            url = ''.join(item_url)
            if not validators.url(url):
                url = 'http://www.6pm.com{}'.format(''.join(item_url))

            yield Request(url=url, meta={'item': item}, callback=self.parse_item_page)

    def parse_item_page(self, response):
        item_list = []
        hxs = Selector(response)
        item = response.meta['item']

        # 6PM
        node_collection = hxs.xpath("//h1[@class='title']/a|//div["
                                    "@class='description']/ul/li/span|//div["
                                    "@class='description']/ul/li/a|//div[@class='description']/ul/li")

        # Walmart
        # node_collection = hxs.xpath("//h1[@itemprop='name']/div|//div["
        #                                         "@class='product-description-disclaimer']|//div[@class='about-desc']")

        # Amazon
        # node_collection = hxs.xpath("//span[@id='productTitle']|//div["
        #                                         "@id='fbExpandableSectionContent']/ul/li/span|//div["
        #                                         "@id='feature-bullets']/ul/li/span")
        if node_collection is not None and len(node_collection) > 0:
            indx = 0
            for node in node_collection:
                value = ''.join(node.xpath("text()").extract())
                if len(value) > 0:
                    indx += 1
                    value = str(value.strip().encode('utf-8'))
                    value = StringUtil.str_utf_encode(value)
                    item_list.append(value)
        item['keywords'] = StringUtil.remove_html_tags(
            str(' '.join(item_list)))

        # Create a CSV file for training data
        with open('train_data.csv', 'ab') as csvfile:
            trainwriter = csv.writer(
                csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
            trainwriter.writerow(
                [item['category'], str(item['keywords']).lower()])

        return item
