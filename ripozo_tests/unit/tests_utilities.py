from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import datetime
import decimal

import mock
import six
import unittest2

from ripozo.utilities import titlize_endpoint, join_url_parts, \
    picky_processor, convert_to_underscore, make_json_safe
from ripozo_tests.bases.manager import generate_random_name


class UtilitiesTestCase(unittest2.TestCase):

    def test_convert_to_underscore(self):
        camel_case_names = ['CamelCase', 'camelCase', 'camel_case', '_CamelCase',
                            'APICamelCase', 'CamelCaseAPI', 'Camel2Case',
                            'CamelCase2', 'CamelCase2API2']

        underscore_names = ['camel_case', 'camel_case', 'camel_case', '__camel_case',
                            'api_camel_case', 'camel_case_api', 'camel2_case',
                            'camel_case2', 'camel_case2_api2']
        if len(camel_case_names) != len(underscore_names):
            raise Exception("The number of entries in camel_case_names must match underscore_names")

        for i in range(len(camel_case_names)):
            old_name = camel_case_names[i]
            new_name = convert_to_underscore(old_name)
            self.assertEqual(underscore_names[i], new_name)

    def test_titlelize_endpoint(self):
        """
        Tests whether an underscored function name
        is properly converted into a title
        """
        name = "some_name_or_something"
        expected = "Some Name Or Something"
        updated = titlize_endpoint(name)
        self.assertEqual(updated, expected)

        name = '_some_name_or_something'
        updated = titlize_endpoint(name)
        self.assertEqual(updated, expected)

        name = 'some_name_or_something_'
        updated = titlize_endpoint(name)
        self.assertEqual(updated, expected)

    def test_join_url_parts(self):
        url = join_url_parts()
        self.assertIsInstance(url, six.text_type)
        self.assertEqual('', url)

        url = join_url_parts('/something', '/another', '/thing')
        self.assertEqual(url, '/something/another/thing')

        url = join_url_parts('something/', '/another/', '/thing')
        self.assertEqual(url, 'something/another/thing')

        url = join_url_parts('something//', '/another')
        self.assertEqual(url, 'something/another')

        url = join_url_parts('/', '/another')
        self.assertEqual('/another', url)

        url = join_url_parts('/', '/')
        self.assertEqual('/', url)

    def test_picky_processor(self):
        processor = mock.Mock()
        if six.PY2:
            processor.__name__ = six.binary_type('FAKE')
        else:
            processor.__name__ = six.text_type('FAKE')
        does_run = picky_processor(processor)
        does_run(mock.Mock(), 'runs')
        self.assertEqual(processor.call_count, 1)

        does_run = picky_processor(processor, include=['runs'])
        does_run(mock.Mock(), 'runs')
        self.assertEqual(processor.call_count, 2)

        does_run = picky_processor(processor, exclude=['nope'])
        does_run(mock.Mock(), 'runs')
        self.assertEqual(processor.call_count, 3)

        does_run = picky_processor(processor, include=['runs'], exclude=['nope'])
        does_run(mock.Mock(), 'runs')
        self.assertEqual(processor.call_count, 4)

        doesnt_run = picky_processor(processor, include=['nope'])
        doesnt_run(mock.MagicMock(), 'runs')
        self.assertEqual(processor.call_count, 4)

        doesnt_run = picky_processor(processor, exclude=['runs'])
        doesnt_run(mock.MagicMock(), 'runs')
        self.assertEqual(processor.call_count, 4)

    def test_make_json_safe(self):
        """
        Tests whether the make_json_safe method correctly
        returns values.
        """
        # Test times
        resp = make_json_safe(datetime.datetime.now())
        self.assertIsInstance(resp, six.text_type)
        resp = make_json_safe(datetime.date.today())
        self.assertIsInstance(resp, six.text_type)
        resp = make_json_safe(datetime.time())
        self.assertIsInstance(resp, six.text_type)
        resp = make_json_safe(datetime.timedelta(days=1))
        self.assertIsInstance(resp, six.text_type)

        # Test decimals
        resp = make_json_safe(decimal.Decimal('1.02'))
        self.assertEqual(resp, 1.02)
        self.assertIsInstance(resp, float)

        # Test lists
        l = [datetime.time(), datetime.date.today(), datetime.datetime.now()]
        resp = make_json_safe(l)
        self.assertIsInstance(resp, list)
        for item in resp:
            self.assertIsInstance(item, six.text_type)

        # Test dictionary
        d = dict(a=datetime.datetime.now(), b=datetime.time(), c=datetime.date.today())
        resp = make_json_safe(d)
        self.assertIsInstance(resp, dict)
        for key, value in six.iteritems(resp):
            self.assertIsInstance(value, six.text_type)

