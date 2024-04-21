# -*- coding: utf-8 -*-
from functools import wraps


def wishlist_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not args[0].wishlist:
            raise WishlistDoesNotExist
        return fn(*args, **kwargs)
    return wrapper


class WishlistDoesNotExist(Exception):
    pass


class WishlistItemDoesNotExist(Exception):
    pass
