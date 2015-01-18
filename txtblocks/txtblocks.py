#!/usr/bin/env python3
# License:
#
# The MIT License (MIT)
#
# Copyright (c) 2014 Jochen Bartl <jochenbartl@mailbox.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import re
from collections import defaultdict


__VERSION__ = "0.3.0"


class TextElement(object):
    def __init__(self, pattern, name=''):
        """
        :param pattern: String - Regular expression
        :param name: String - Optional. Give the TextElement a name for
                     better debugging
        """
        self.name = name
        self._pattern = pattern

    def parse(self, text):
        """Parses a text string and returns all regular expression matches as
           tuple (element name, dictionary with matches)"""

        d = defaultdict(list)

        for match in re.finditer(self._pattern, text):
            groupdict = match.groupdict()
            if len(match.groups()) > 0 and len(groupdict) == 0:
                raise Exception("Some regexes in {} have no name. Use ?P<myregexname>".format(self.name))
            else:
                # iteritems not available in Python3
                for k, v in groupdict.items():
                    d[k].append(v)

        return d


class TextLine(TextElement):
    """Object for parsing a line of text ;-)"""

    def __init__(self, pattern, name=''):
        """
        :param pattern: String - Regular expression
        :param name: String - Optional. Give the TextElement a name for
                     better debugging
        """
        TextElement.__init__(self, pattern, name)
        self._pattern = re.compile(pattern)

    def parse(self, text):
        """Parses a text string and returns all regular expression matches as
           tuple (element name, dictionary with matches)"""

        d = defaultdict(list)

        match = self._pattern.match(text)

        if match:
            groupdict = match.groupdict()

            if len(match.groups()) > 0 and len(groupdict) == 0:
                raise Exception("Some patternes in {} have no name. Use ?P<mypatternname>".format(self.name))
            else:
                for k, v in groupdict.items():
                    d[k].append(v)
        
        return d


class TextBlock(object):
    """Container for TextLine instances"""

    def __init__(self, name, textelements, startregex, endregex='',
                 oneliner=False):
        """
        name - Text block name
        textelements - List of TextLine instances
        startregex - String containing a regular expression that marks the
                     beginning of a text block
        endregex (optional) - Marks end of a text block
        oneliner (optional) - If True, all whitespaces will be replaced with
                              a single space

        If endregex is not defined, the text block will end at EOF or when the
        startregex pattern is seen again.
        """

        self.name = name
        self._textelements = textelements
        self._startregex = re.compile(startregex)
        self._oneliner = oneliner

        if len(endregex) > 0:
            self._endregex = re.compile(endregex)
        else:
            self._endregex = endregex

    def matches_start_pattern(self, text):
        match = self._startregex.match(text)

        if match:
            return True
        else:
            return False

    def matches_end_pattern(self, text):
        match = self._endregex.match(text)

        if match:
            return True
        else:
            return False

    def parse(self, text):
        """
        text - String contains of one or more lines which are separated by a
               new line character

        returns dict-text-regexname-matches

        """
        data = {}

        if self._oneliner:
            text = re.sub('\s+', ' ', text.strip())

        for line in text.split('\n'):
            for textelement in self._textelements:
                match = textelement.parse(line)

                if match:
                    for e in match:
                        data[e] = match[e]
                    continue

        return data


class Parser(object):
    def __init__(self):
        self._linenum = 0
        self._text = ''

    def _set_input_text(self, text):
        self._text = text

    def read_lines(self, strip=True):
        for line in self._text.split('\n'):
            if strip:
                line = line.strip()
            self._linenum += 1
            yield line


class BlockParser(Parser):
    def __init__(self, textblocks):
        Parser.__init__(self)
        self._textblocks = textblocks

    def find_textblock(self, line):
        for textblock in self._textblocks:
            if textblock.matches_start_pattern(line):
                return textblock

        return None

    def parse(self, text):
        textbuffer = ""
        blocks = defaultdict(list)
        currblock = None

        self._set_input_text(text)

        # Code duplication, somewhat ugly, need to #FIXIT someday
        for line in self.read_lines():
            textblock = self.find_textblock(line)

            if textblock and currblock:
                currblockname = currblock.name
                match = currblock.parse(textbuffer)

                # Save data if any of the patterns in the TextBlock did match
                if match:
                    blocks[currblock.name].append(match)

                currblock = textblock
                textbuffer = line + '\n'
            elif textblock:
                currblock = textblock
                textbuffer += line + '\n'
            elif currblock:
                textbuffer += line + '\n'

        if len(textbuffer) > 0:
            currblockname = currblock.name
            match = currblock.parse(textbuffer)

            # Save data if any of the patterns in the TextBlock did match
            if match:
                blocks[currblock.name].append(match)

        return blocks
