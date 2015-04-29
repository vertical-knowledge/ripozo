from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.tests.python2base import TestBase

import logging
import random
import string


def logger():
    return logging.getLogger(__name__)


def generate_random_name():
    return ''.join(random.choice(string.ascii_letters) for _ in range(15))


class TestManagerMixin(TestBase):
    """
    manager, does_not_exist_exception, and all_person_models proeprties need to be implemented
    get_person_model_by_id method needs to be implemented
    """
    def test_create(self):
        """
        Tests that the model is appropriately created
        """
        assert False

    def test_create_not_exists(self):
        """
        Tests that a DoesNotExistException exception
        is raised if the model does not exists
        """
        assert False

    def test_create_specific_fields(self):
        """
        Tests that the model only updates the create_fields
        if the _create_fields attribute is set.
        """
        assert False

    def test_update(self):
        """
        Tests that a model is appropriately updated
        """
        assert False

    def test_update_not_exists(self):
        """
        Tests that a DoesNotExistException exception
        is raised if the model does not exists
        """
        assert False

    def test_update_specific_fields(self):
        """
        Tests that a model specifically only allows the
        update_fields and not the fields if update_fields
        is specified
        """
        assert False

    def test_retrieve_list(self):
        """
        Tests that the retrieve_list appropriately
        returns a list of resources
        """
        assert False

    def test_retrieve_empty_list(self):
        """
        Tests that an empty list is returned if
        no results match.
        """
        assert False

    def test_retrieve_filtering(self):
        """
        Tests that the basic filtering works
        for the manager
        """
        assert False

    def test_retrieve_list_specific_fields(self):
        """
        Tests that the retrieve_list retrieves
        only the _retrieve_list fields if specified
        """
        assert False

    def test_retrieve_list_paginations(self):
        """
        Tests that the pagination works correctly with
        retrieve_list
        """
        assert False

    def test_retrieve_list_pagination_links(self):
        """
        Tests that the pagination links are appropriately
        set.
        """
        assert False

    def test_delete(self):
        """
        Tests that a resource is deleted appropriately.
        """
        assert False

    def test_delete_not_exists(self):
        """
        Tests that a DoesNotExistException exception
        is raised if the model does not exists
        """
        assert False