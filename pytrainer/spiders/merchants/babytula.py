# -*- coding: utf-8 -*-
import re
import os
import sys
import json
import traceback

from m_base import MBase
from pytrainer.items import PytrainerItem
from pytrainer.apputil.string_util import StringUtil
from m_base import UnitTypes
from urlparse import urlparse

reload(sys)
sys.setdefaultencoding('utf8')
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

traceback_template = '''Traceback (most recent call last):
  File "%(filename)s", line %(lineno)s, in %(name)s
%(type)s: %(message)s\n'''


class BabyTula(MBase):

    def __init__(self, xreponse, url):
        MBase.__init__(self, xreponse)
        self.url = url

    def extractProductData(self):
        item = PytrainerItem()

        try:
            item["category"] = "baby carriers"

            # Get product title
            # item["keywords"] = self.__getTitleInCategoryLevel()

            # Get product description
            item["keywords"] = self.__getDescription()

        except Exception, e:
            print ' '
            print '--------------------BEGIN ERROR-------------------'
            print('ERROR: %s' % e.message)
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_details = {'filename': exc_traceback.tb_frame.f_code.co_filename,
                                 'lineno': exc_traceback.tb_lineno, 'name': exc_traceback.tb_frame.f_code.co_name,
                                 'type': exc_type.__name__, 'message': exc_value.message,}
            del (exc_type, exc_value, exc_traceback)
            print traceback.format_exc()
            print traceback_template % traceback_details
            item["error_desc"] = e.message % traceback_template % traceback_details
            print '--------------------END ERROR-------------------'
            print ' '
        else:
            pass
        finally:
            return item

    def __getTitleInCategoryLevel(self):
        item_list = []
        node_collection = self.getElementValues("//div[@class='a-row a-spacing-micro']/a/h2|//div[@class='a-row "
                                                "a-spacing-top-mini']/a/h2|//div[@class='a-row "
                                                "a-spacing-mini']/a/h2|//div[@class='a-row "
                                                "a-spacing-none']/a/h2|//span[@id='productTitle']|//ol["
                                                "@class='class=a-carousel']/li/div/a/span")
        if node_collection is not None and len(node_collection) > 0:
            indx = 0
            for node in node_collection:
                value = ''.join(node.xpath("@data-attribute").extract())
                if len(value) > 0:
                    indx += 1
                    value = str(value.strip().encode('utf-8'))
                    value = StringUtil.str_utf_encode(value)
                    item_list.append(self.listToJson(['title', 'index'], [value, indx]))

        return item_list

    def __getDescription(self):
        item_list = []
        node_collection = self.getElementValues("//h1[@class='product-name']|//div[@itemprop='description']/*")
        if node_collection is not None and len(node_collection) > 0:
            indx = 0
            for node in node_collection:
                value = ''.join(node.xpath("text()").extract())
                if len(value) > 0:
                    indx += 1
                    value = str(value.strip().encode('utf-8'))
                    value = StringUtil.str_utf_encode(value)
                    item_list.append(value)
        return StringUtil.remove_html_tags(str(' '.join(item_list)))
