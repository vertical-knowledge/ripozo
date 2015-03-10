from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.utilities import convert_to_underscore, serialize_fields,\
    titlize_endpoint, join_url_parts

from ripozo_tests.python2base import TestBase
from ripozo_tests.bases.manager import generate_random_name

import six
import unittest


class UtilitiesTestCase(TestBase, unittest.TestCase):

    def test_convert_to_underscore(self):
        camel_case_names = ['CamelCase', 'camelCase', 'camel_case', '_CamelCase',
                            'APICamelCase', 'CamelCaseAPI', 'Camel2Case',
                            'CamelCase2', 'CamelCase2API2']

        underscore_names = ['camel_case', 'camel_case', 'camel_case', '_camel_case',
                            'api_camel_case', 'camel_case_api', 'camel2_case',
                            'camel_case2', 'camel_case2_api2']
        if len(camel_case_names) != len(underscore_names):
            raise Exception("The number of entries in camel_case_names must match underscore_names")

        for i in range(len(camel_case_names)):
            old_name = camel_case_names[i]
            new_name = convert_to_underscore(old_name)
            self.assertEqual( underscore_names[i], new_name)

    def test_serialize_fields(self):
        """
        Tests whether the fields are properly serialized
        """
        t = dict()
        for i in six.moves.range(10):
            t[generate_random_name()] = generate_random_name()
        t2 = t.copy()
        t3 = serialize_fields(six.iterkeys(t2), six.itervalues(t2))
        self.assertDictEqual(t2, t3)
        t4 = serialize_fields(list(six.iterkeys(t2)), list(six.itervalues(t2)))
        self.assertDictEqual(t2, t4)

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
