# -*- coding: utf-8 -*-


def truncate_string(s, max_len):
    return (s[:max_len] + '..') if len(s) > max_len else s
