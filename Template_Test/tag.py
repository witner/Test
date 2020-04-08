#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入系统模块
import re
# 第三方模块
from Template_Test.node import *
# 导入自定义模块

# 设置环境变量


class Library:

    def __init__(self):
        self.tags = {}

    def tag(self, name=None):
        def out_wrapper(func):
            self.tags[name] = func

            def wrapper(*args, **kwargs):
                func(*args, **kwargs)
            return wrapper
        return out_wrapper


library = Library()


@library.tag('for')
def do_for(parser, token):
    bits = token.split_contents()
    if len(bits) < 4:
        raise ValueError("'for' statements should have at least four"
                         " words: %s" % token.contents)

    is_reversed = bits[-1] == 'reversed'
    in_index = -3 if is_reversed else -2
    if bits[in_index] != 'in':
        raise ValueError("'for' statements should use the format"
                         " 'for x in y': %s" % token.contents)

    invalid_chars = frozenset((' ', '"', "'", '|'))
    loop_vars = re.split(r' *, *', ' '.join(bits[1:in_index]))
    for var in loop_vars:
        if not var or not invalid_chars.isdisjoint(var):
            raise ValueError("'for' tag received an invalid argument:"
                             " %s" % token.contents)

    loop_sequence = bits[in_index + 1]
    nodelist_loop = parser.parse(('empty', 'endfor',))
    token = parser.next_token()
    if token.contents == 'empty':
        nodelist_empty = parser.parse(('endfor',))
        parser.delete_first_token()
    else:
        nodelist_empty = None

    return ForNode(token.contents, loop_vars, loop_sequence, nodelist_loop)
