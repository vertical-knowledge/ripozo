from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from ripozo.exceptions import RestException, DispatchException, NotFoundException, \
    TranslationException, ValidationException, AdapterFormatAlreadyRegisteredException, FieldException, \
    ManagerException, NoResourceNameDeclaredException

import unittest2


class TestExceptions(unittest2.TestCase):
    """
    Seems stupid, but I've screwed it up multiple times.
    Long story short, test coverage, no matter how trivial,
    is valuable in case you did something really stupid.
    (Like initializing exceptions wrong.
    """
    exceptions = [RestException, DispatchException,
                  NotFoundException, TranslationException, ValidationException,
                  AdapterFormatAlreadyRegisteredException, FieldException,
                  ManagerException, NoResourceNameDeclaredException]

    def test_exceptions(self):
        """
        Just run through them, initialize them and check if
        they are an instance of RestException
        """
        for e in self.exceptions:
            exc = e(message='some message', status_code=102)
            self.assertEqual(str(exc), 'some message')
            self.assertEqual(exc.status_code, 102)
            exc = e('message')
            self.assertEqual(str(exc), 'message')
