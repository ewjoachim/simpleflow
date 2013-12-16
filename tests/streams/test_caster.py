# -*- coding:utf-8 -*-
import unittest
import logging
from StringIO import StringIO

from cdf.log import logger
from cdf.streams.mapping import str_to_bool
from cdf.streams.utils import split_file
from cdf.streams.caster import Caster

logger.setLevel(logging.DEBUG)


class TestCaster(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_caster(self):
        f = StringIO()
        f.write('1\thttp://www.site.com\t1\n')
        f.write('2\thttp://www.site.com/page.html\t0\n')
        f.write('3\thttp://www.site.com/another_page.html\t1\n')
        f.seek(0)

        INFOS_FIELDS = [('id', int),
                        ('url', str),
                        ('gzipped', str_to_bool)]
        cast = Caster(INFOS_FIELDS).cast
        urls = cast(split_file(f))
        expected_urls = [
            [1, 'http://www.site.com', True],
            [2, 'http://www.site.com/page.html', False],
            [3, 'http://www.site.com/another_page.html', True]
        ]
        self.assertEquals(list(urls), expected_urls)

    def test_empty_string(self):
        f = StringIO()
        f.write('1\t/some/thing\t\n')
        f.seek(0)

        FIELDS = [('id', int),
                  ('path', str),
                  ('query', str)]
        cast = Caster(FIELDS).cast
        urls = cast(split_file(f))
        expected = [
            [1, '/some/thing', ''],
        ]
        self.assertEquals(list(urls), expected)


