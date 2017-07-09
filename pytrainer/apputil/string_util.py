# -*- coding: utf-8 -*-
import urllib
import urllib2
import re
import hashlib

from decimal import Decimal
from HTMLParser import HTMLParser
from lxml import etree


class StringUtil:
    @staticmethod
    def str_utf_decode(str_val):
        return urllib.unquote(str_val).decode('utf8')

    @staticmethod
    def str_utf_encode(str_val):
        return urllib.unquote(str_val).encode('utf8')

    @staticmethod
    def str_cleaner(str_val, str_pattern, replace_with):
        # str = re.sub("[^0-9a-zA-Z\s\-]+", "", str) #allow numbers, alpha, space, dash
        val = re.sub(str_pattern, replace_with, str_val)
        return val

    @staticmethod
    def str_search_str(str_val, str_pattern):
        mstr = re.compile(str_pattern, re.IGNORECASE)

        # matches = mstr.findall(str)
        # count = 0
        # for match in matches:
        #     count +=1
        #     print count
        #     print match[5]

        m = mstr.search(str_val)
        if m is None or (m is not None and m is False):
            return ''
        else:
            return m.group(0)

            # matches = mstr.findall(str_val)[0]
            # return matches

    @staticmethod
    def str_extract(str_val, first_str, last_str, ex_first_str, ex_last_str):
        value = ""

        if (len(first_str) > 0 and len(last_str) > 0):
            rx = re.compile(first_str + '(.*?)' + last_str)
            m = rx.search(str_val)
            if m:
                value = m.group(1).strip()

        if (len(first_str) > 0 and len(last_str) == 0):
            str_index = str_val.index(first_str)
            if (str_index > -1):
                value = str_val[(str_index + len(first_str)):].strip()

        if (len(first_str) == 0 and len(last_str) > 0):
            str_index = str_val.index(last_str)
            if (str_index > -1):
                value = str_val[0:str_index].strip()

        if (value is not None and ex_first_str == False):
            value = '{}{}'.format(first_str, value)

        if (value is not None and ex_last_str == False):
            value = '{}{}'.format(value, last_str)

        return value

    @staticmethod
    def str_hash(str_val, mode=1):
        _hash_value = int(hashlib.sha1(str_val).hexdigest(), 16) % (10 ** 8)
        return _hash_value

    @staticmethod
    def str_to_float(str_val):

        try:
            value = Decimal(re.sub(r'\d+(\.\d{1,2})?', '', str_val))  # Decimal(_regular_price.strip('$'))
            float(value)
        except Exception:
            value = 0

        return value

    @staticmethod
    def str_find_str(str_val, str_pattern):
        mstr = re.compile(str_pattern, re.IGNORECASE)
        if (mstr.search(str_val)):
            return True
        else:
            return False

    @staticmethod
    def try_parse(dtype, value):

        if (dtype == 'float'):
            try:
                inNumberfloat = float(value)
                if type(inNumberfloat) == float:
                    return True
                else:
                    return False
            except ValueError:
                return False
        elif (dtype == 'int'):
            try:
                inNumberInt = int(value)
                if type(inNumberInt) == int:
                    return True
                else:
                    return False
            except ValueError:
                return False
        elif (dtype == 'long'):
            try:
                inNumberLong = long(value)
                if type(inNumberLong) == long:
                    return True
                else:
                    return False
            except ValueError:
                return False

    @staticmethod
    def remove_html_tags(html):
        return re.sub('<[^>]*>"', "", html)

    @staticmethod
    def str_to_byte_array(str_val):
        return str.encode(str_val)

    @staticmethod
    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

    @staticmethod
    def writeToFile(filename, body):
        with open(filename, 'wb') as f:
            f.write(body)

    @staticmethod
    def createXmlNode(root, element_name, element_attr_names, element_attr_values, element_value=None):
        if len(element_name) == 0:
            return ''
        if len(element_attr_names) != len(element_attr_values):
            return ''

        attr = {}
        if len(element_attr_names) == len(element_attr_values):
            for index in range(len(element_attr_names)):
                attr[element_attr_names[index]] = element_attr_values[index]

        if attr:
            etree.SubElement(root, element_name, attr)

        return root

    @staticmethod
    def requestUrl(url, url_referer, content_type):
        try:
            req = urllib2.Request(url)
            req.add_header('Referer', url_referer)
            req.add_header('Content-Type', content_type)
            req.add_header('charset', 'UTF-8')
            req.add_header('accept', '*/*')
            req.add_header('User-Agent',
                           'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.82 Safari/537.36')
            response = urllib2.urlopen(req)

            response_data = ""
            while 1:
                data = response.read()
                if not data:
                    break
                response_data += data

            return response_data
        except Exception, e:
            print e.message
            return {"Error": e.message}

    @staticmethod
    def is_valid_url(url):
        regex = re.compile(r'^https?://'  # http:// or https://
                           r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
                           r'localhost|'  # localhost...
                           r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                           r'(?::\d+)?'  # optional port
                           r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url is not None and regex.search(url)

    @staticmethod
    def get_min_price(price):
        min_price = float(0)
        if price:
            price_range = str(price).replace('$', '').strip().split('-')
            if len(price_range) > 1 and StringUtil.try_parse('float', price_range[0]):
                return float(price_range[0])
        return min_price


class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)