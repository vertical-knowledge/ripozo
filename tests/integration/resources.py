from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import translate, apimethod
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
            @translate(manager_field_validators=True, validate=True)
            def hello(cls, request, *args, **kwargs):
                return cls(properties=request.body_args)

        self.help_test_validate_with_manager_field_validators(TestValidateIntegrations)

    def test_validate_with_manager_field_validators_inherited(self):
        """
        Same as test_validate_with_manager_field_validators,
        except that it checks it on an inherited class.  This was
        done to ensure no regressions in regards to issue #10 on github.
        """
        fake_manager = mock.MagicMock()
        fake_manager.field_validators = [BaseField('first', required=True), BaseField('second', required=False)]

        class TestValidateIntegrationsParent(ResourceBase):
            manager = fake_manager

            @apimethod(methods=['GET'])
            @translate(manager_field_validators=True, validate=True)
            def hello(cls, request, *args, **kwargs):
                return cls(properties=request.body_args)

        self.help_test_validate_with_manager_field_validators(TestValidateIntegrationsParent)

        class TestValidateIntegrationsInherited(TestValidateIntegrationsParent):
            _resource_name = 'another'
            pass

        self.help_test_validate_with_manager_field_validators(TestValidateIntegrationsInherited)

    def help_test_validate_with_manager_field_validators(self, klass):
        """
        Helper for the couple test_validate_with_manager_field_validators.
        Just checks that it gets the right responses.  Abstracted out poorly
        to reduce code duplication and because I hate typing.

        :param type klass: The class that you are checking.
        """
        request = RequestContainer(body_args=dict(first=[1], second=[2]))
        response = klass.hello(request)
        self.assertDictEqual(dict(first=1, second=2), response.properties)
        self.assertDictEqual(request.body_args, response.properties)

        # Without list inputs since requests are mutable
        response = klass.hello(request)
        self.assertDictEqual(dict(first=1, second=2), response.properties)
        self.assertDictEqual(request.body_args, response.properties)

        request2 = RequestContainer(body_args=dict(second=[2]))
        self.assertRaises(ValidationException, klass.hello, request2)

        request3 = RequestContainer(body_args=dict(first=[1]))
        response = klass.hello(request3)
        self.assertDictEqual(dict(first=1), response.properties)