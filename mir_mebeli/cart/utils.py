# -*- coding: utf-8 -*-
from functools import wraps


def cart_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not args[0].cart:
            raise CartDoesNotExist
        return fn(*args, **kwargs)
    return wrapper


class CartDoesNotExist(Exception):
    pass


class CartItemDoesNotExist(Exception):
    pass
