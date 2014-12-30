__author__ = 'Tim Martin'
import unittest
from cassandra_rest.viewsets import _convert_to_underscore


class UtilitiesTestCase(unittest.TestCase):

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
            new_name = _convert_to_underscore(old_name)
            self.assertEqual( underscore_names[i], new_name)