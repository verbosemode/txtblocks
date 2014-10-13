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

import sys
import re
import pprint


class TextLine(object):
    """Object for parsing a line of text ;-)
    
    >>> deviceid = TextLine('deviceid', '^Device ID: (?P<deviceid>.+)$')
    >>> deviceid.parse('Device ID: switch1.lab.example.com')
    {'deviceid': 'switch1.lab.example.com'}
    >>> deviceid.parse('Some random string')
    {}
    """

    def __init__(self, name, regex):
        self._name = name
        self._regex = re.compile(regex)


    def parse(self, text):
        """Parses a text string and returns all regular expression matches as dictionary"""

        match = self._regex.match(text)

        if match:
            groupdict = match.groupdict()

            if len(match.groups()) > 0 and len(groupdict) == 0:
                raise Exception("Some regexes in {} have no name. Use ?P<myregexname>".format(self._name))
            else:
                return groupdict
        else: 
            return {}

    def get_name(self):
        return self._name


class TextBlock(object):
    """Container for TextLine instances"""

    def __init__(self, name, textelements, startregex, endregex=''):
        """
        name - Text block name
        textelements - List of TextLine instances
        startregex - String containing a regular expression that marks the beginning of a text block
        endregex (optional) - Marks end of a text block

        If endregex is not defined, the text block will end at EOF or when the startregex pattern
        is seen again.
        """

        self._name = name
        self._textelements = textelements
        self._startregex = re.compile(startregex)

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
        text - String contains of one or more lines which are separated by a new line character

        returns a dictionary where keys are TextLine instance names

        """
        data = {}

        for line in text.split('\n'):
            for textelement in self._textelements:
                match = textelement.parse(line)

                if len(match) > 0:
                    data[textelement.get_name()] = match
                    continue

        return data

    def get_name(self):
        return self._name


class Parser(object):
    def __init__(self, inputstr):
        self._inputstr = inputstr
        self._linenum = 0

    def set_inputstr(self, inputstr):
        self._inputstr = inputstr

    def read_lines(self, strip=True):
        for l in self._inputstr.split('\n'):
            if strip:
                l = l.strip()
            self._linenum += 1
            yield l


class BlockParser(Parser):
    def __init__(self, text, textblocks):
        Parser.__init__(self, text)
        self._textblocks = textblocks


    def parse(self):
        buffer = ""
        blocks = {}
        inblock = False
        currblock = None

        for line in self.read_lines():
            if currblock:
                if currblock.matches_start_pattern(line) and inblock:
                    buffer += line
                   
                    if not currblock.get_name() in blocks:
                        blocks[currblock.get_name()] = []

                    result = currblock.parse(buffer)

                    if len(result) > 0:
                        blocks[currblock.get_name()].append(result)

                    buffer = ""
                    currblock = None
                    inblock = False
                    continue
                elif inblock:
                    buffer += line + "\n"
            else:
                for textblock in self._textblocks:
                    if textblock.matches_start_pattern(line):
                        currblock = textblock
                        buffer += line + "\n"
                        inblock = True
                        break


        if inblock:
            buffer += line
            if not currblock.get_name() in blocks:
                blocks[currblock.get_name()] = []

            result = currblock.parse(buffer)

            if len(result) > 0:
                blocks[currblock.get_name()].append(result)
            buffer = ""
            currblock = None
            inblock = False

        return blocks
