# Copyright (c) 2009 J-Pascal Mercier
#
#
import logging
import traceback
import new

from functools import wraps
from itertools import izip

logger = logging.getLogger(__name__)

class buggy(object):
    """
    This is a decorator which can be used to mark functions
    as not implemented. It will result in a warning being emitted when
    the function is called.
    """
    def __init__(self, date):
        self.date = date

    def __call__(self, fct):
        @wraps(fct)
        def wrapper(*args, **kwargs):
            logger.warning("%s is buggy, use at your own risk. Expected fix : %s" % (fct.__name__, self.date))
            try:
                return_value = fct(*args, **kwargs)
            except Exception:
                print "%s Crashed : Didn't i told you it was buggy ?" % (fct.__name__)
                raise
            return return_value
        return wrapper


class unimplemented(object):
    """
    This is a decorator which can be used to mark functions
    as not implemented. It will result in a warning being emitted and 
    the function is never called.
    """
    def __init__(self, date):
        self.date = date

    def __call__(self, fct):
        @wraps(fct)
        def wrapper(*args, **kwargs):
            logger.warning("%s is not_implemented ... now. Expected : %s " % (fct.__name__, self.date))
        return wrapper


class broken(object):
    """
    This is a decorator which can be used to mark functions
    as broken. It will result in a warning being emitted and 
    the function is never called.
    """
    def __init__(self, date):
        self.date = date

    def __call__(self, fct):
        @wraps(fct)
        def wrapper(*args, **kwargs):
            logger.critical("%s is broken -- DON'T USE IT. Expected fix : %s" % (fct.__name__, self.date))
        return wrapper


def deprecated(fct):
    """
    This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """
    @wraps(fct)
    def wrapper(*args, **kwargs):
        logger.warning("Call to deprecated function %s." % (fct.__name_))
        return fct(*args, **kwargs)
    return wrapper

def logcall(fct):
    """
    This is a decorator which log function call.
    """
    @wraps(fct)
    def wrapper(*args, **kwargs):
        logger.info("Function -- %s--  called with arguments -- %s -- and keywords -- %s --" % \
                    (fct.__name__, str(args), str(kwargs)))
        return_value = fct(*args, **kwargs)
        logger.info("Function -- %s -- returned -- %s --" % \
                    (fct.__name__, return_value))
        return return_value
    return wrapper


def addmethod(instance):
    def decorator(fct):
        setattr(instance, fct.func_name, fct)
        return fct
    return decorator


