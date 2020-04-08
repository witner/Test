#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入系统模块
import re


# 第三方模块

# 导入自定义模块

# 设置环境变量


class Variable:
    """
    作用：A template variable, resolvable against a given context. The variable may
    be a hard-coded string (if it begins and ends with single or double quote
    marks)::
    >>> a = 'test'
    >>> Variable('').resolve(a)
    >>> 'test'
    >>> b = [1, 2, 3]
    >>> Variable('[1]').resolve(b)
    >>> 2
    >>> c = {'article': {'section':'News'}}
    >>> Variable('article.section').resolve(c)
    'News'
    >>> Variable('article').resolve(c)
    {'section': 'News'}
    >>> d = {'book': {'language': ['Chinese', 'English']}}
    >>> Variable('book.language[1]').resolve(d)
    >>> 'English'
    (The example assumes VARIABLE_ATTRIBUTE_SEPARATOR is '.')
    """

    def __init__(self, var_str):
        self.var_str = None

        if isinstance(var_str, str):
            self.var_str = var_str
        else:
            raise TypeError("Variable must be a string or number, got %s" % type(var_str))

    def resolve(self, context):
        var_list = re.split(r'[.\[\]]', self.var_str)
        value = context
        for var in var_list:
            if re.fullmatch(r'-?\d+', var):
                value = value[int(var)]
            elif re.fullmatch(r'\w+', var):
                value = value[var] if var in value else 'NotFound'
            else:
                continue

        return value


if __name__ == '__main__':
    a = 'test'
    print(Variable('').resolve(a))
    b = [1, 2, 3]
    print(Variable('[1]').resolve(b))
    c = {'article': {'section': 'News'}}
    print(Variable('article.section').resolve(c))
    d = {'book': {'language': ['Chinese', 'English']}}
    print(Variable('book.language[1]').resolve(d))
