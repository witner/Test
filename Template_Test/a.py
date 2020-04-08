#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入系统模块
import re
import os
from enum import Enum
from node import Node, TextNode, VariableNode, NodeList

# 第三方模块

# 导入自定义模块

# 设置环境变量

BLOCK_TAG_START = '{%'
BLOCK_TAG_END = '%}'
VARIABLE_TAG_START = '{{'
VARIABLE_TAG_END = '}}'
COMMENT_TAG_START = '{#'
COMMENT_TAG_END = '#}'
# TRANSLATOR_COMMENT_MARK = 'Translators'
# SINGLE_BRACE_START = '{'
# SINGLE_BRACE_END = '}'

tag_re = (re.compile('(%s.*?%s|%s.*?%s|%s.*?%s)' %
                     (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END),
                      re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
                      re.escape(COMMENT_TAG_START), re.escape(COMMENT_TAG_END))))


class TokenType(Enum):
    TEXT = 0
    VAR = 1
    BLOCK = 2
    COMMENT = 3


class Token:
    def __init__(self, token_type, contents, position=None, lineno=None):
        """
        表示模板中字符串的标记。
        :param token_type: 标记类型，可以是.TEXT、.VAR、.BLOCK或.COMMENT。
        :param contents: 源字符串
        :param position: 包含令牌的起始和结束索引的可选元组
        :param lineno: 标记出现在模板源中的行号。
        """
        self.token_type, self.contents = token_type, contents
        self.lineno = lineno
        self.position = position
        pass

    def __str__(self):
        token_name = self.token_type.name.capitalize()
        return ('<%s token: "%s...">' %
                (token_name, self.contents[:20].replace('\n', '')))

    # def split_contents(self):
    #     split = []
    #     bits = smart_split(self.contents)
    #     for bit in bits:
    #         # Handle translation-marked template pieces
    #         if bit.startswith(('_("', "_('")):
    #             sentinel = bit[2] + ')'
    #             trans_bit = [bit]
    #             while not bit.endswith(sentinel):
    #                 bit = next(bits)
    #                 trans_bit.append(bit)
    #             bit = ' '.join(trans_bit)
    #         split.append(bit)
    #     return split


class Template(object):
    def __init__(self, template_file_path):
        self.template_string = self.load_template_string(template_file_path)

    @staticmethod
    def load_template_string(template_file_path):
        with open(template_file_path, 'r', encoding='UTF-8') as f:
            template_string = f.read()
            return template_string

    def tokenize(self):
        """
        Split a template string into tokens and annotates each token with its
        start and end position in the source. This is slower than the default
        lexer so only use it when debug is True.
        """
        lineno = 1
        result = []
        upto = 0
        # r = tag_re.finditer(self.template_string)
        # print(r)
        for match in tag_re.finditer(self.template_string):
            start, end = match.span()
            if start > upto:
                token_string = self.template_string[upto:start]
                result.append(self.create_token(token_string, (upto, start), lineno, in_tag=False))
                lineno += token_string.count('\n')
                upto = start
            token_string = self.template_string[start:end]
            result.append(self.create_token(token_string, (start, end), lineno, in_tag=True))
            lineno += token_string.count('\n')
            upto = end
        last_bit = self.template_string[upto:]
        if last_bit:
            pass
            result.append(self.create_token(last_bit, (upto, upto + len(last_bit)), lineno, in_tag=False))
        return result

    def create_token(self, token_string, position, lineno, in_tag):
        # # return Token(TokenType.TEXT, token_string, position, lineno)
        # if in_tag and token_string.startswith(BLOCK_TAG_START):
        #     block_content = token_string[2:-2].strip()
        #     print(block_content)

        if in_tag:
            if token_string.startswith(VARIABLE_TAG_START):
                return Token(TokenType.VAR, token_string[2:-2].strip(), position, lineno)
            elif token_string.startswith(BLOCK_TAG_START):
                block_content = token_string[2:-2].strip()
                return Token(TokenType.BLOCK, block_content, position, lineno)
            else:
                return Token(TokenType.COMMENT, token_string[2:-2].strip(), position, lineno)
        else:
            return Token(TokenType.TEXT, token_string, position, lineno)


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.command_stack = []

    def parse(self):
        nodelist = NodeList()
        while self.tokens:
            token = self.next_token()
            if token.token_type.value == 0:    # TokenType.TEXT
                self.extend_nodelist(nodelist, TextNode(token.contents), token)
            elif token.token_type.value == 1:  # TokenType.VAR
                if not token.contents:
                    raise ValueError(token, 'Empty variable tag on line %d' % token.lineno)

                self.extend_nodelist(nodelist, VariableNode(token.contents), token)
            elif token.token_type.value == 2:  # TokenType.BLOCK
                pass
                try:
                    command = token.contents.split()[0]
                    print(command)
                except IndexError:
                    raise self.error(token, 'Empty block tag on line %d' % token.lineno)

                self.command_stack.append((command, token))
                new_nodelist = NodeList()
                self.extend_nodelist(nodelist, new_nodelist, token)
                nodelist = new_nodelist

    def next_token(self):
        return self.tokens.pop(0)


    def extend_nodelist(self, nodelist, node, token):
        # node.token = token
        nodelist.append(node)


if __name__ == '__main__':
    t = Template('1.html')
    r = t.tokenize()
    p = Parser(r)
    p.parse()