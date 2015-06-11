__author__ = 'Tim Martin'
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)s - [%(module)s - %(filename)s '
                           '- %(lineno)d - %(levelname)s]: %(message)s')
logger = logging.getLogger(__name__)

from ripozo_tests import unit, integration