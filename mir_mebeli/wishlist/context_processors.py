# -*- coding: utf-8 -*-
from wishlist import Wishlist


def wishlist(request):
    return {'wishlist': Wishlist(request)}
