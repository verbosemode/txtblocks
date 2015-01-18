#!/usr/bin/env python3

import unittest
import sys
from collections import defaultdict
sys.path.append('txtblocks')
from txtblocks import TextElement, TextLine, TextBlock, BlockParser


class TestTextLine(unittest.TestCase):
    def test_parser_match(self):
        deviceid = TextLine('^Device ID: (?P<deviceid>.+)$')
        match = deviceid.parse('Device ID: switch1.lab.example.com')
        result = {'deviceid': ['switch1.lab.example.com']}
        self.assertEqual(match, result)

    def test_parser_no_match(self):
        deviceid = TextLine('^Device ID: (?P<deviceid>.+)$')
        match = deviceid.parse('some random string')
        result = {}
        self.assertEqual(match, result)


class TestTextBlock(unittest.TestCase):
    def test_matches_start_pattern(self):
        txtblock = TextBlock('foo', [], '^it all starts here')
        self.assertEqual(txtblock.matches_start_pattern('it all starts here'), True)

    def test_matches_not_start_pattern(self):
        txtblock = TextBlock('foo', [], '^foobar')
        self.assertEqual(txtblock.matches_start_pattern('it all starts here'), False)

    def test_matches_end_pattern(self):
        txtblock = TextBlock('foo', [], '', endregex='^block ends here')
        self.assertEqual(txtblock.matches_end_pattern('block ends here'), True)

    def test_matches_not_end_pattern(self):
        txtblock = TextBlock('foo', [], '', endregex='^foobar')
        self.assertEqual(txtblock.matches_end_pattern('block ends here'), False)

    def test_parse(self):
        text = "it all starts here\nfoo\nDevice ID: switch1.lab.example.com\nbar"

        deviceid = TextLine('^Device ID: (?P<deviceid>.+)$')
        txtblock = TextBlock('foo', [deviceid], '^it all starts here')

        result = defaultdict(list)
        result['deviceid'] = ['switch1.lab.example.com']

        self.assertEqual(txtblock.parse(text), result)

    def test_parse_oneliner(self):
        text = "it all starts here\nPlatform: foo,\nDevice ID: switch1.lab.example.com\nbar"

        platform = TextElement('Platform:\s(?P<platform>[\w+\-]+),')
        deviceid = TextElement('Device ID: (?P<deviceid>[\w\.]+)')
        txtblock = TextBlock('foo', [platform, deviceid], '^it all starts here', oneliner=True)

        result = {'platform': ['foo'], 'deviceid': ['switch1.lab.example.com']}

        self.assertEqual(txtblock.parse(text), result)

    def test_parse_oneliner_overlapping_matches(self):
        text = "it all starts here\nPlatform: foo,\nDevice ID: switch1.lab.example.com\nbar\n" \
               "Device ID: switch2.lab.example.com"

        platform = TextElement('Platform:\s(?P<platform>[\w+\-]+),')
        deviceid = TextElement('Device ID: (?P<deviceid>[\w\.]+)')
        txtblock = TextBlock('foo', [platform, deviceid], '^it all starts here', oneliner=True)

        result = {'platform': ['foo'], 'deviceid': ['switch1.lab.example.com','switch2.lab.example.com']}

        self.assertEqual(txtblock.parse(text), result)


class TestBlockParser(unittest.TestCase):
    def test_parse(self):
        text = """-------------------------
Device ID: switch1.lab.example.com
Entry address(es): 
  IP address: 192.168.0.2
Platform: cisco WS-C2960PD-8TT-L,  Capabilities: Switch IGMP 
Interface: FastEthernet0/18,  Port ID (outgoing port): GigabitEthernet0/1
Holdtime : 133 sec

Version :
Cisco IOS Software, C2960 Software (C2960-LANBASEK9-M), Version 15.0(2)SE4, RELEASE SOFTWARE (fc1)
Technical Support: http://www.cisco.com/techsupport
Copyright (c) 1986-2013 by Cisco Systems, Inc.
Compiled Wed 26-Jun-13 02:49 by prod_rel_team

advertisement version: 2
Protocol Hello:  OUI=0x00000C, Protocol ID=0x0112; payload len=27, value=00000000000
VTP Management Domain: ''
Native VLAN: 1
Duplex: full
Management address(es): 
  IP address: 192.168.0.2

-------------------------"""
        deviceid = TextLine('^Device ID: (?P<deviceid>.+)$')
        ifaces = TextLine('^Interface: (?P<ifremote>.+),\s+Port ID.+: (?P<iflocal>.+)$')
        txtblock = TextBlock('fooblock', [deviceid, ifaces], '^Device ID:')
        blockparser = BlockParser([txtblock])
        result = {'fooblock': [{'deviceid': ['switch1.lab.example.com'], 'ifremote': ['FastEthernet0/18'],
                                'iflocal': ['GigabitEthernet0/1']}]}
        self.assertEqual(blockparser.parse(text), result) 

    def test_parse_multiple_textlines(self):
        pass

if __name__ == '__main__':
    unittest.main()
