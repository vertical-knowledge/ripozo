__author__ = 'Tim Martin'
import unittest

from tests.integration.apitests import TestApiSimple
from tests.unit.test_serializer import TestSerializerSimple
from tests.unit.tests_utilities import UtilitiesTestCase
from tests.integration.test_custom_routes import TestCustomRoutes
from tests.integration.test_siren import TestSiren


class Fake(unittest.TestCase):

    def _fake(self):
        pass

if __name__ == "__main__":
    test_cases = [TestSerializerSimple, TestApiSimple, UtilitiesTestCase, TestCustomRoutes, TestSiren]
    loader = unittest.TestLoader()
    suites_list = []
    for tc in test_cases:
        suite = loader.loadTestsFromTestCase(tc)
        suites_list.append(suite)
    main_suite = unittest.TestSuite(suites_list)
    runner = unittest.TextTestRunner()
    results = runner.run(main_suite)