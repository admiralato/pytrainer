# -*- coding: utf-8 -*-
import re
import operator
import math
import datetime

from scrapy.selector import HtmlXPathSelector
from enum import Enum
from pytrainer.apputil.string_util import StringUtil


class MBase:
    htmlObject = None
    availKw = ["in stock", "in-stock", "usually ships within", "released on", "expected to ship", "pre-order",
               "available from these sellers", "pre order"]

    dimensionPatterns = [
        r'(\d+(\.\d+)|\d+)(|�|") \([WHLD]\) ?x ?(\d+(\.\d+)|\d+)(|�|") \([WHLD]\) ?x ?(\d+(\.\d+)|\d+)(|�|") \([WHLD]\)?',
        r'(\d+(\.\d+)|\d+)(|�|") ?x ?(\d+(\.\d+)|\d+)(|�|") ?x ?(\d+(\.\d+)|\d+)(|�|")?',
        r'(\d+(\.\d+)|\d+)" [WHDL] ?x ?(\d+(\.\d+)|\d+)" [WHDL] ?x ?(\d+(\.\d+)|\d+)" [WHDL]',
        r'(\d+(\.\d+)|\d+)"[WHDL]?x?(\d+(\.\d+)|\d+)"[WHDL]?x?(\d+(\.\d+)|\d+)"[WHDL]',
        r'(\d+(\.\d+)|\d+) ?x ?(\d+(\.\d+)|\d+) ?x ?(\d+(\.\d+)|\d+)?',
        r'\b((\d*\.?\d+?)(["\']|[^"\'])\s?x).*\b(x[\s|\S](\d*\.?\d+)(["\']|[^"\']))?',
        r'\d+(\.\d+) ?x ?\d+(\.\d+) ?x ?\d+(\.\d+)?',
        r'(\d+(\.\d+)|\d+)(.*)[in.DWHL]?x[\s\S]?(\d+(\.\d+)|\d+)(.*)[in.DWHL]?x[\s\S]?(\d+(\.\d+)|\d+)?(.*)[in.DWHL]?']

    dimensionPatternsToRemove = [r'[-| ](\d+(\.\d+)|\d+)\/(\d+(\.\d+)|\d+)', r'&#034;', r'\([WHLD]\)', r'" [W,H,D,L]',
        r'"[W,H,D,L]', r'(inches)', r'[WHDL]', r'(in.)', r'(in)', r'(\s\s)', r'&quot;', r'&#189;', r'&#188;', r'&QUOT;']

    productWeightPatterns = [r'(item weight|Shipping Weight)(:|:\s|\s:)(\d+(\.\d{1,2})?)(\s|\S)(ounce|pound|lb\s|lbs)']

    def __init__(self, htmlDoc):
        self.dateAdded = datetime.datetime.strftime(datetime.datetime.now(), '%Y-%m-%d %H:%M:%S')
        self.htmlObject = htmlDoc
        self.category_dict = {"tops": 0.5, "dresses": 1, "prom dresses": 5, "gowns": 7, "rash guards": 1,
                              "coverup-up": 1, "swimwear": 0.5, "diving suits": 5, "coats": 5, "jeans": 2,
                              "casual pants": 1, "sweatshirts": 3, "capris & tights": 1, "vests": 1, "outdoor vests": 2,
                              "shorts & skirts": 0.5, "long skirts": 1, "activewear": 2, "underwear": 0.5,
                              "girls jumpsuits & rompers": 1, "jumpsuits & rompers": 3, "suits & sport coats": 5,
                              "watches": 1, "hats": 5, "gloves": 0.5, "eyewear": 0.5, "belts": 0.5, "handbags": 3,
                              "duffle bags": 5, "messenger bags": 3, "briefcases": 3, "lunch bags": 3, "diaper bags": 3,
                              "laptop bags": 5, "lumbar packs": 3, "backpacks": 3, "makeup bag": 1, "clutches": 1,
                              "wallets": 1, "luggage": 15, "1BR bowling bags": 12, "2BR bowling bags": 17,
                              "3BR bowling bags": 21, "4BR bowling bags": 22, "6BR bowling bags": 42, "slippers": 1,
                              "flip flops": 2, "booties": 3, "infant booties": 1, "mid-calf boots": 4, "tall boots": 5,
                              "over-the-knee boots": 5, "cold weather boots": 5, "extended-calf boots": 6,
                              "sandals & slides": 2, "heels": 2, "flats": 2, "loafers & slip-ons": 2,
                              "clogs & mules": 2, "oxfords & derbys": 2, "boat shoes": 2,
                              "sneakers & athletic shoes": 3, "jewelry": 0.5, "jackets": 3, "sackpacks": 2}

    # @classmethod
    def getElementValue(self, xpath):
        if self.htmlObject is None:
            return ""

        value = self.htmlObject.xpath(xpath).extract()
        if value is not None and len(value) > 0:
            value = str(value[0].strip().encode('utf-8'))
        else:
            value = ""
        return value

    def getElementValues(self, xpath):
        if self.htmlObject is None:
            return None
        value = ''
        collection = self.htmlObject.xpath(xpath)
        if collection is not None and len(collection) > 0:
            # for htmlTextNode in collection:
            #     value = value + htmlTextNode.strip()
            return collection
        else:
            return None

    def getSku(self, xpath):
        pass

    def writeToFile(self, filename, body):
        with open(filename, 'wb') as f:
            f.write(body)

    def getProductDimension(self, instance_of, instance_val):
        if self.htmlObject is None:
            return ''

        if instance_val is None:
            return ''

        content = None
        dimension = ''

        if instance_of == "DOCUMENT" and len(instance_val) > 0:
            content = self.getElementValue(instance_val)
        elif instance_of == "STRING" and len(instance_val) > 0:
            content = instance_val

        content = StringUtil.remove_html_tags(content)
        content = StringUtil.str_cleaner(content, r'\\([a-z0-9]{3})', '')
        content = StringUtil.str_cleaner(content, r'[^0-9a-zA-Z\s\-\(\).,"\'&]+', '')

        if content is not None and type(content) is not None and len(content) > 0:
            # for pat in self.dimensionPatternsToRemove:
            #     content = StringUtil.str_cleaner(content, pat, "")

            for sptf in self.dimensionPatterns:
                if StringUtil.str_find_str(str(content), sptf):
                    dimension = StringUtil.str_search_str(str(content), sptf)
                    break

        if dimension and len(dimension) == 0 or len(dimension) > 35:
            dimension = self.getProductWeight(content)

        return dimension

    def getProductWeight(self, instance_val):
        # self.writeToFile('content_raw.txt',instance_val)
        # self.writeToFile('content.txt',content.strip())
        content = ''
        if instance_val is not None:
            content = StringUtil.str_cleaner(instance_val, r'<[^>]*>', '')
            content = StringUtil.str_cleaner(content, r'\s\s', '')
            content = StringUtil.str_search_str(content,
                r"(item weight|Shipping Weight)(:|:\s|\s:)(\d+(\.\d{1,2})?)(\s|\S)(ounce|pound|lb\s|lbs)")
        # self.writeToFile('content.txt',content.strip())
        return content

    # def getCategory(self, __p_info):
    #     classifier = ApparelClassifier(ApparelConfiguration.model)
    #     __p_info = StringUtil.strip_tags(__p_info)
    #     try:
    #         probability_dict = classifier.classify(
    #             unicode(__p_info.strip().replace('"', '').replace('\n', '').replace('\r', '').replace('\t', ''),
    #                     'utf-8'))
    #     except TypeError:
    #         probability_dict = classifier.classify(
    #             __p_info.strip().replace('"', '').replace('\n', '').replace('\r', '').replace('\t', ''))
    #     finally:
    #         sorted_dict = sorted(probability_dict.items(), key=operator.itemgetter(1), reverse=True)
    #     self.probabilities = dict(probability_dict)
    #     result_list = [str(i[0]) for i in sorted_dict]
    #     # print '-----------------------------'
    #     # print result_list
    #     # print '-----------------------------'
    #     # Return the first element of the tuple
    #     return str(result_list[0])

    def getShippingWeight(self, key):
        result_dict = dict(self.category_dict)
        value = float("%0.4f" % result_dict.get(str(key), 0))
        if value <= 0:
            value = 1
        return value

    def listToJson(self, element_attr_names, element_attr_values):
        arr = {}
        if len(element_attr_names) == len(element_attr_values):
            for index in range(len(element_attr_names)):
                arr[element_attr_names[index]] = element_attr_values[index]

        return arr

    def getVolumetricWeight(self, dimension, ut):
        if len(dimension) == 0 or " x " not in dimension:
            return 0

        volumetric_weight = 0
        try:
            di_arr = dimension.split(' x ')
            dimensions = []
            if len(di_arr) == 3:
                for index in range(len(di_arr)):
                    di = di_arr[index]
                    for pat in self.dimensionPatternsToRemove:
                        di = StringUtil.str_cleaner(di, pat, "").strip()
                    if StringUtil.try_parse('float', di) is True:
                        if ut == UnitTypes.MM:
                            di = math.ceil(float(di) * 0.0393701)
                        elif ut == UnitTypes.CM:
                            di = math.ceil(float(di) * 0.393701)

                        dimensions.append(float(di))
                    else:
                        # Set value to 1 if the dimension value is invalid to convert to float.
                        # This idea is wrong. Temp solution only.
                        dimensions.append(1)

            if len(dimensions) == 3:
                volumetric_weight = reduce(lambda x, y: x * y, dimensions)
                volumetric_weight = volumetric_weight / 130
                volumetric_weight = math.ceil(volumetric_weight)
            else:
                volumetric_weight = 0
        except:
            volumetric_weight = 0

        return volumetric_weight

class UnitTypes(Enum):
    MM = 'millimeter'
    CM = 'centimeter'
    INCH = 'inch'
    FT = 'feet'
    KG = 'kilogram'
    LB = 'pound'
    OZ = 'ounce'
    GM = 'gram'
