from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import validate, translate, apimethod
from ripozo.exceptions import ValidationException
from ripozo.viewsets.fields import BaseField
from ripozo.viewsets.request import RequestContainer
from ripozo.viewsets.resource_base import ResourceBase

from ripozo_tests.python2base import TestBase
from ripozo_tests.helpers.hello_world_viewset import get_refreshed_helloworld_viewset

import mock
import unittest


class TestResourceIntegration(TestBase, unittest.TestCase):
    def test_validate_with_manager_field_validators(self):
        fake_manager = mock.MagicMock()
        fake_manager.field_validators = [BaseField('first', required=True), BaseField('second', required=False)]

        class TestValidateIntegrations(ResourceBase):
            manager = fake_manager

            @apimethod(methods=['GET'])
            @validate(manager_field_validators=True)
            def hello(cls, request, *args, **kwargs):
                return cls(properties=request.body_args)

        request = RequestContainer(body_args=dict(first=[1], second=[2]))
        response = TestValidateIntegrations.hello(request)
        self.assertDictEqual(dict(first=1, second=2), response.properties)
        self.assertDictEqual(request.body_args, response.properties)

        # Without list inputs since requests are mutable
        response = TestValidateIntegrations.hello(request)
        self.assertDictEqual(dict(first=1, second=2), response.properties)
        self.assertDictEqual(request.body_args, response.properties)

        request2 = RequestContainer(body_args=dict(second=[2]))
        self.assertRaises(ValidationException, TestValidateIntegrations.hello, request2)

        request3 = RequestContainer(body_args=dict(first=[1]))
        response = TestValidateIntegrations.hello(request3)
        self.assertDictEqual(dict(first=1), response.properties)
