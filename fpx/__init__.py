import logging
from .main import FunPayTools
from .classes.runner.subclasses.router import Router
from .utils import errors as fpx_error
from .models.chat import Message
from .models.account import Order, CurReview
from .models.lots import CategoryLastLot
from .utils.dependencies import Dependency

logger = logging.getLogger('fpx')
logger.addHandler(logging.NullHandler())