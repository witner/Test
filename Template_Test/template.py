#!/usr/bin/env python
# -*- coding: utf-8 -*-

# 导入系统模块
import re
import os
from enum import Enum

# 第三方模块
from Template_Test.node import *
from Template_Test.tag import library
# 导入自定义模块

# 设置环境变量


FILTER_SEPARATOR = '|'
FILTER_ARGUMENT_SEPARATOR = ':'
VARIABLE_ATTRIBUTE_SEPARATOR = '.'
BLOCK_TAG_START = '{%'
BLOCK_TAG_END = '%}'
VARIABLE_TAG_START = '{{'
VARIABLE_TAG_END = '}}'
COMMENT_TAG_START = '{#'
COMMENT_TAG_END = '#}'
TRANSLATOR_COMMENT_MARK = 'Translators'
SINGLE_BRACE_START = '{'
SINGLE_BRACE_END = '}'

tag_re = (re.compile('(%s.*?%s|%s.*?%s|%s.*?%s)' %
                     (re.escape(BLOCK_TAG_START), re.escape(BLOCK_TAG_END),
                      re.escape(VARIABLE_TAG_START), re.escape(VARIABLE_TAG_END),
                      re.escape(COMMENT_TAG_START), re.escape(COMMENT_TAG_END))))

# Expression to match some_token and some_token="with spaces" (and similarly
# for single-quoted strings).
smart_split_re = re.compile(r"""
    ((?:
        [^\s'"]*
        (?:
            (?:"(?:[^"\\]|\\.)*" | '(?:[^'\\]|\\.)*')
            [^\s'"]*
        )+
    ) | \S+)
""", re.VERBOSE)


def smart_split(text):
    r"""
    Generator that splits a string by spaces, leaving quoted phrases together.
    Supports both single and double quotes, and supports escaping quotes with
    backslashes. In the output, strings will keep their initial and trailing
    quote marks and escaped quotes will remain escaped (the results can then
    be further processed with unescape_string_literal()).

    >>> list(smart_split(r'This is "a person\'s" test.'))
    ['This', 'is', '"a person\\\'s"', 'test.']
    >>> list(smart_split(r"Another 'person\'s' test."))
    ['Another', "'person\\'s'", 'test.']
    >>> list(smart_split(r'A "\"funky\" style" test.'))
    ['A', '"\\"funky\\" style"', 'test.']
    """
    for bit in smart_split_re.finditer(str(text)):
        yield bit.group(0)


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

    def split_contents(self):
        split = []
        bits = smart_split(self.contents)
        for bit in bits:
            # Handle translation-marked template pieces
            if bit.startswith(('_("', "_('")):
                sentinel = bit[2] + ')'
                trans_bit = [bit]
                while not bit.endswith(sentinel):
                    bit = next(bits)
                    trans_bit.append(bit)
                bit = ' '.join(trans_bit)
            split.append(bit)
        return split


class Template:
    """
    作用：将模板页面进行解析转换
    """

    def __init__(self, template_file_path):
        self.source = self.load_template_source(template_file_path)
        self.tokens = self.source_to_token()

    @staticmethod
    def load_template_source(template_file_path):
        if os.path.exists(template_file_path):
            with open(template_file_path, 'r', encoding='UTF-8') as f:
                template_string = f.read()
                return template_string
        else:
            raise FileExistsError('The file %s not exist' % template_file_path)

    @staticmethod
    def create_token(token_string, position, lineno, in_tag):
        """
        作用：创建token
        :param token_string:
        :param position:
        :param lineno:
        :param in_tag:
        :return:
        """
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

    def source_to_token(self):
        """
        作用：将模板source转换成三类token，普通html文本TextToken，变量VarToken，块BLOCKToken
        :return:
        """
        lineno = 1
        result = []
        upto = 0
        for match in tag_re.finditer(self.source):
            start, end = match.span()
            if start > upto:
                token_string = self.source[upto:start]
                result.append(self.create_token(token_string, (upto, start), lineno, in_tag=False))
                lineno += token_string.count('\n')
                upto = start
            token_string = self.source[start:end]
            result.append(self.create_token(token_string, (start, end), lineno, in_tag=True))
            lineno += token_string.count('\n')
            upto = end
        last_bit = self.source[upto:]
        if last_bit:
            result.append(self.create_token(last_bit, (upto, upto + len(last_bit)), lineno, in_tag=False))
        return result


class Parser:
    """
    作用：将token 变为node 给后续程序解析
    """

    def __init__(self, tokens, libraries=None):
        self.tokens = tokens
        self.command_stack = []
        self.tags = {}
        self.libraries = libraries

    def add_library(self, lib):
        self.tags.update(lib.tags)

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


if __name__ == '__main__':
    k = {
        'a': 1,
        'b': [0, 1, 2, 3],
        'c': {'c1': 1, 'c2': 'c2', 'c3': ['c31', 'c32']}
    }
    t = Template('test_html/1.html')
    p = Parser(t.tokens)
    # print(library.items())
    p.add_library(library)

    nl = p.parse()
    r = nl.render(k)
    with open('new.html', 'w', encoding='UTF-8') as f:
        f.write(r)


