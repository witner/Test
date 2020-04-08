#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入系统模块

# 第三方模块
from .node import NodeList, TextNode, VariableNode, ForNode
# 导入自定义模块

# 设置环境变量


class Parser:
    """
    作用：将template token 变为node 给后续程序解析
    """

    def __init__(self, tokens):
        self.tokens = tokens
        self.command_stack = []
        self.tags = {
            'for': do_for,
        }

    def next_token(self):
        return self.tokens.pop(0)

    def prepend_token(self, token):
        self.tokens.insert(0, token)

    @staticmethod
    def extend_nodelist(nodelist, node, token):
        node.token = token
        nodelist.append(node)

    def parse(self, parse_until=None):
        """
        作用：解析token，
        :param parse_until:
        :return:
        """
        if parse_until is None:
            parse_until = []
        nodelist = NodeList()
        while self.tokens:
            token = self.next_token()
            if token.token_type.value == 0:  # TokenType.TEXT
                self.extend_nodelist(nodelist, TextNode(token.contents), token)
            elif token.token_type.value == 1:  # TokenType.VAR
                if not token.contents:
                    raise ValueError(token, 'Empty variable tag on line %d' % token.lineno)

                self.extend_nodelist(nodelist, VariableNode(token.contents), token)
            elif token.token_type.value == 2:  # TokenType.BLOCK
                try:
                    command = token.contents.split()[0]
                    print(command)
                except IndexError:
                    raise self.error(token, 'Empty block tag on line %d' % token.lineno)

                if command in parse_until:
                    # A matching token has been reached. Return control to
                    # the caller. Put the token back on the token list so the
                    # caller knows where it terminated.
                    self.prepend_token(token)
                    return nodelist

                compile_func = self.tags[command]
                compiled_result = compile_func(self, token)

                self.extend_nodelist(nodelist, compiled_result, token)
        return nodelist