from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import random
import string


def random_string(length=50):
    return ''.join(random.choice(string.ascii_letters) for _ in range(length))
