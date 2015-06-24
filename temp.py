from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

def method(first=1, *args):
    for a in args:
        print(a)
    print('first={0}'.format(first))


if __name__ == '__main__':
    method('a', 'b', 'c')
