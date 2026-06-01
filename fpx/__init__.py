import logging
from .main import FunPayTools
from .classes.runner.subclasses.handler import Router

logger = logging.getLogger('fpx')
logger.addHandler(logging.NullHandler())