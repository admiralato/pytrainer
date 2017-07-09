from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request
from pytrainer.items import PytrainerItem

from pytrainer.apputil.string_util import StringUtil

class SixPMSpider(CrawlSpider):
    name = "6pm"
    allowed_domains = ["6pm.com"]
    start_urls = ["https://www.walmart.com/search/?page=1&po=1&query=analog+watches#searchProductResult"]

    ## Pass the pagination xpath
    rules = (
        Rule(SgmlLinkExtractor(allow=(), restrict_xpaths=('//div[@class="paginator"]/ul/li/a',
                                                          )),
             callback="parse_items",
             follow= True),
    )

    def parse_items(self, response):
        hxs = HtmlXPathSelector(response)

        ## Search results container
        # urls = hxs.select('//div[@id="searchResults"]/a') # 6PM
        urls = hxs.select('//ul[@class="search-result-gridview-items"]/li/div/div[3]/a') # Walmart

        for url in urls:
            item = PytrainerItem()
            item['category'] = "analog watches"
            item_url = ''.join(url.xpath("@href").extract())
            url = 'https://www.walmart.com{}'.format(''.join(item_url))
            yield Request(url=url, meta={'item': item}, callback=self.parse_item_page)

    def parse_item_page(self, response):
        item_list = []
        hxs = HtmlXPathSelector(response)
        item = response.meta['item']

        # 6PM
        # node_collection = hxs.select("//h1[@class='title']/a|//div["
        #                                         "@class='description']/ul/li/span|//div["
        #                                         "@class='description']/ul/li/a|//div[@class='description']/ul/li")

        # Walmart
        node_collection = hxs.select("//h1[@itemprop='name']/div|//div["
                                                "@class='product-description-disclaimer']|//div[@class='about-desc']")
        if node_collection is not None and len(node_collection) > 0:
            indx = 0
            for node in node_collection:
                value = ''.join(node.xpath("text()").extract())
                if len(value) > 0:
                    indx += 1
                    value = str(value.strip().encode('utf-8'))
                    value = StringUtil.str_utf_encode(value)
                    item_list.append(value)
        item['keywords'] = StringUtil.remove_html_tags(str(' '.join(item_list)))
        return item