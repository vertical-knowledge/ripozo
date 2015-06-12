from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.decorators import translate, apimethod
from ripozo.exceptions import ValidationException
from ripozo.resources.fields import BaseField
from ripozo.resources.relationships import ListRelationship
from ripozo.resources.request import RequestContainer
from ripozo.resources.resource_base import ResourceBase

import mock
import unittest2


class TestResourceIntegration(unittest2.TestCase):
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

    def test_relationships_resource_instance(self):
        """
        Tests whether the relationships are appropriately created.
        """
        lr = ListRelationship('resource_list', relation='Resource')
        class ResourceList(ResourceBase):
            _resource_name = 'resource_list'
            _relationships = [
                lr,
            ]

        class Resource(ResourceBase):
            _pks = ['id']

        self.assertEqual(ResourceList._relationships, [lr])
        props = dict(resource_list=[dict(id=1), dict(id=2)])
        res = ResourceList(properties=props)
        self.assertEqual(len(res.related_resources), 1)
        resources = res.related_resources[0][0]
        self.assertIsInstance(resources, list)
        self.assertEqual(len(resources), 2)

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