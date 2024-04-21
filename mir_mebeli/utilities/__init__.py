# -*- coding: utf-8 -*-


def safe_int(value, default=0):
    try:
        return int(value)
    except:
        return default


def safe_float(value, default=0):
    try:
        return float(value)
    except:
        return default


def uniquify_list(seq):
    """удалить дубли из списка, сохраняя изначальный порядок элементов."""
    seen = set()
    seen_add = seen.add
    return [x for x in seq if x not in seen and not seen_add(x)]
