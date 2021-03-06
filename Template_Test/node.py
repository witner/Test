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


class Node:
    def __init__(self, content):
        """
        作用：初始化
        :param content: 文本内容
        """
        self.content = content

    def __repr__(self):
        return "<{}:{}>".format(self.__class__.__name__, self.content[:25])

    def render(self, context):
        """
        作用：节点进行渲染成字符串，用于html, 子类必须重写实现该方法
        :param context: python传递给模板的字典参数
        :return: 字符串
        """
        pass

    def __iter__(self):
        yield self


class TextNode(Node):
    """
    文本Node
    """
    def __init__(self, content):
        super().__init__(content)

    def render(self, context):
        return self.content


class VariableNode(Node):
    """
    变量Node
    """
    def __init__(self, content):
        super().__init__(content)

    def render(self, context):
        v = Variable(self.content).resolve(context)
        return str(v)


class ForNode(Node):
    """
    For循环Node
    """
    def __init__(self, content, loop_vars, loop_sequence, nodelist_loop):
        """
        {% for i in items %} a {% endfor %}
        :param content: 文本内容
        :param loop_vars: 循环变量比如 i
        :param loop_sequence: 循环序列比如 items
        :param nodelist_loop: 属于循环的 NodeList
        """
        super().__init__(content)

        self.loop_vars, self.loop_sequence = loop_vars, loop_sequence
        self.nodelist_loop = nodelist_loop

    def render(self, context):
        """
        :param context: 上下文相关变量
        :return:
        """

        values = Variable(self.loop_sequence).resolve(context)  # 获取对于变量
        # 对变量进行预处理
        if values is None:
            values = []
        if not hasattr(values, '__len__'):
            values = list(values)
        len_values = len(values)
        if len_values < 1:
            pass

        num_loop_vars = len(self.loop_vars)
        unpack = num_loop_vars > 1

        bits = []
        for i, item in enumerate(values):
            if unpack:
                unpacked_vars = dict(zip(self.loop_vars, item))
                context.update(unpacked_vars)
            else:
                context[self.loop_vars[0]] = item

            bits.append(self.nodelist_loop.render(context))

        return ''.join(bits)


class NodeList(list):
    """
    Node 列表
    """
    def render(self, context):
        bits = []
        for node in self:
            if isinstance(node, Node):
                bit = node.render(context)
            else:
                bit = ''
            bits.append(str(bit))

        return ''.join(bits)



if __name__ == '__main__':
    a = 'test'
    print(Variable('').resolve(a))
    b = [1, 2, 3]
    print(Variable('[1]').resolve(b))
    c = {'article': {'section': 'News'}}
    print(Variable('article.section').resolve(c))
    d = {'book': {'language': ['Chinese', 'English']}}
    print(Variable('book.language[1]').resolve(d))