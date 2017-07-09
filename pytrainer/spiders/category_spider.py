import json
import traceback
import sys
import csv
import scrapy

from logger import logger
from scrapy.selector import Selector
from scrapy.utils.serialize import ScrapyJSONEncoder

from merchants.amazon import Amazon
from merchants.keds import Keds
from merchants.sixpm import SixPM
from merchants.forever21 import ForeverTwentyOne
from merchants.harrods import Harrods
from merchants.karmaloop import Karmaloop
from merchants.adidas import Adidas
from merchants.macys import Macys
from merchants.eastbay import Eastbay
from merchants.footaction import FootAction
from merchants.amazonuk import AmazonUK
from merchants.walmart import Walmart
from merchants.yoox import Yoox
from merchants.zappos import Zappos
from merchants.bowling import Bowling
from merchants.nike import Nike
from merchants.athleta import Athleta
from merchants.nordstrom import Nordstrom
from merchants.sportsdirect import SportsDirect
from merchants.carters import Carters
from merchants.oshkosh import OshKosh
from merchants.babytula import BabyTula
from merchants.casemate import CaseMate

traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n'''

class CategorySpider(scrapy.Spider):
    urls = [
        'http://www.6pm.com/bootie-shoes/CK_XAToC7BLiAgIBBw.zso?ot=bootie&s=percentOff/desc/&redirected=true'
    ]
    name = "keywordcrawler"

    def start_requests(self):
        for url in self.urls:
            cookies = self.set_cookies(url)

            if cookies is not None:
                yield scrapy.Request(url=url, cookies=cookies, dont_filter=True, callback=self.parse)
            else:
                yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        logger.info("SCRAPING '%s' " % response.url)
        logger.info("RESPONSE: %s" % response.status)

        hxs = Selector(response)
        merchant = None

        try:
            if "amazon.co.uk" in response.url:
                merchant = AmazonUK(hxs, response.url)
            elif "amazon.com" in response.url:
                merchant = Amazon(hxs, response.url)
            elif "keds.com" in response.url:
                merchant = Keds(hxs, response.url)
            elif "6pm.com" in response.url:
                merchant = SixPM(hxs, response.url)
            elif "forever21.com" in response.url:
                merchant = ForeverTwentyOne(hxs, response.url)
            elif "harrods.com" in response.url:
                merchant = Harrods(hxs, response.url)
            elif "karmaloop.com" in response.url:
                merchant = Karmaloop(hxs, response.url)
            elif "adidas.com" in response.url:
                merchant = Adidas(hxs, response.url)
            elif "macys.com" in response.url:
                merchant = Macys(hxs, response.url)
            elif "eastbay.com" in response.url:
                merchant = Eastbay(hxs, response.url)
            elif "footaction.com" in response.url:
                merchant = FootAction(hxs, response.url)
            elif "walmart.com" in response.url:
                merchant = Walmart(hxs, response.url)
            elif "yoox.com" in response.url:
                merchant = Yoox(hxs, response.url)
            elif "zappos.com" in response.url:
                merchant = Zappos(hxs, response.url)
            elif "bowling.com" in response.url:
                merchant = Bowling(hxs, response.url)
            elif "nike.com" in response.url:
                merchant = Nike(hxs, response.url)
            elif "athleta.gap.com" in response.url:
                merchant = Athleta(hxs, response.url)
            elif "nordstrom.com" in response.url:
                merchant = Nordstrom(hxs, response.url)
            elif "sportsdirect.com" in response.url:
                merchant = SportsDirect(hxs, response.url)
            elif "carters.com" in response.url:
                merchant = Carters(hxs, response.url)
            elif "oshkosh.com" in response.url:
                merchant = OshKosh(hxs, response.url)
            elif "babytula.com" in response.url:
                merchant = BabyTula(hxs, response.url)
            elif "case-mate.com" in response.url:
                merchant = CaseMate(hxs, response.url)


            if merchant is not None:
                item = merchant.extractProductData()

            # Parse item
            _encoder = ScrapyJSONEncoder()
            jsonString = json.loads(_encoder.encode(item))
            keywords = jsonString['keywords']

            # Create a CSV file for product-category data
            # with open('train_data.csv', 'ab') as csvfile:
            #     trainwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
            #     for keyword in keywords:
            #         trainwriter.writerow([jsonString['category'], str(''.join(keyword['title'])).lower()])

            # Create a CSV file for training data
            with open('train_data.csv', 'ab') as csvfile:
                trainwriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
                trainwriter.writerow([jsonString['category'], str(jsonString['keywords']).lower()])
            return item
        except Exception, e:
            print ' '
            print '--------------------BEGIN ERROR-------------------'
            print('Error: %s' % e.message)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {'filename': exc_traceback.tb_frame.f_code.co_filename,
                                 'lineno': exc_traceback.tb_lineno, 'name': exc_traceback.tb_frame.f_code.co_name,
                                 'type': exc_type.__name__, 'message': exc_value.message, }
            del (exc_type, exc_value, exc_traceback)
            print traceback.format_exc()
            print traceback_template % traceback_details
            print '--------------------END ERROR-------------------'
            print ' '
            return item

    def set_cookies(self, url):
        cookies = None

        if "macys.com" in url:
            cookies = {'shippingCountry': 'US', 'currency': 'USD'}
        elif "athleta.gap.com" in url:
            cookies = {'locale': 'en_US|||',
                       'customerLocation': 'us|USD',
                       'extole_access_token': 'DKLWUNYD3CJOO1PNVJC',
                       'pib': 'false',
                       'SSP_AB_FP_20160815': 'Control',
                       '_sp_id.27c8': '85e9b916-e239-44c1-a811-4d8cfd7c4875.1478590667.1.1478590819.1478590667'
                                      '.cbee17e0-b110-4354-9482-732e23dd7f1c',
                       'SurveyPersist': 'surveyType%3DRockbridgeSurvey',
                       'optimizelyEndUserId': 'oeu1487672310730r0.7674629299714169',
                       'RES_TRACKINGID': '751877728630239',
                       'ResonanceSegment': '1',
                       'ABSeg': 'B|B|B|B|',
                       'unknownShopperId': 'B45D859070F76D813D1B2B3809C3CF11|||',
                       'mktUniversalPersist':
                           'responsiveShoppingBagMode%3DresponsiveBag_SegB%26wcdCheckoutCountryPreselect%3DUS%26globalInterceptDontShow%3Dtrue%2611012015_Email_Acq_Popup_BRUS%3D1%26ONOL_hasSeenEmailpopUS%3D1478596904963%26sop2%3DA%26sop4%3DB%26GOL_hasSeenEmailpop%3D1',
                       's_pers': '%20s_chan%3D%255B%255B%2527_u%2527%252C%25271478590740191%2527%255D%255D'
                                 '%7C1636357140191%3B%20s_dfa%3Dgapproduction%252Cgapgidproduction%7C1487674251229%3B%20s_fid%3D248578F47853A64E-1D8AA233225E2389%7C1550744451807%3B%20s_depth%3D5%7C1487674251812%3B',
                       'pixelManagementPersist':
                           'cvo_client_sid1%3D6Y53CJGMC2Z7%26pixelPartnerList%3DdoubleClick_2011/10/20-2020/10/24%252CrangeDoubleClick_2011/10/20-2020/10/24%252CgoogleAdServices_2011/01/26-2020/01/26%252CbrightTag_2011/07/19-2020/07/19',
                       's_vi': '[CS]v1|2C10C065052A2000-40000108400114FA[CE]',
                       'mp_gapinc_mixpanel': '%7B%22distinct_id%22%3A%20%2215842df394e33c-0aad96806ac65d-5c412b1c-1fa400-15842df394f1be%22%7D'}

        return cookies
