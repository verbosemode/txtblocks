txtblocks - Parser for screen scraping CLI output from network devices
======================================================================

!!!WARNING!!! This parser is totally broken. I need to rewrite the whole thing one day, maybe :D

Use `textfsm <https://code.google.com/p/textfsm/>`_  or `pyparsing <http://pyparsing.wikispaces.com/>`_ instead.




I'll try to write a parser which helps me through my Cisco CLI screen scraping adventures.
This is just one of my toy projects.

The parser can match each line of a text block against a regular expression or treat the
entire block as just a single string. The latter means, all new lines are removed and
multiple whitespace characters are replaced by a single space.


Usage Examples
--------------


Some text from "show cdp neigh detail" ::

	-------------------------
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
	Protocol Hello:  OUI=0x00000C, Protocol ID=0x0112; payload len=27, value=
	VTP Management Domain: ''
	Native VLAN: 1
	Duplex: full
	Management address(es): 
	  IP address: 192.168.0.2

	-------------------------
        ...


.. code-block:: python

        # Parse a single line within a text block
        deviceid = TextLine('^Device ID: (?P<deviceid>.+)$')
        ifaces = TextLine('^Interface: (?P<ifremote>.+),\s+Port ID.+: (?P<iflocal>.+)$')
        # cdpentry -> Name of the text block
        # [deviceid, ...] -> TextLine elements within the TextBlock
        # Last parameter defines how the start of a text block looks like.
        txtblock = TextBlock('cdpentry', [deviceid, ifaces], '^Device ID:')
        blockparser = BlockParser([txtblock])
        blockparser.parse(text)

        # Result
        {'cdpentry': [{'deviceid': ['switch1.lab.example.com'], 'ifremote': ['FastEthernet0/18'], 'iflocal': ['GigabitEthernet0/1']},
                      {'deviceid': ['switch2.lab.example.com'], 'ifremote': ['FastEthernet0/23'], 'iflocal': ['GigabitEthernet0/2']}]}



This is what the parser return data structure looks like at the moment

.. code-block:: python

        result = {
            'block1': [],
            'cdpneigh': [
                         {
                          'deviceid': ['switch1.lab.example.com'],
                          'ifremote': ['FastEthernet0/18'],
                          'iflocal': ['GigabitEthernet0/1']
                          },
                         {
                          'deviceid': ['switch2.lab.example.com'],
                          'ifremote': ['GigabitEthernet0/1'],
                          'iflocal': ['FastEthernet0/18']
                         }
            ]
        }


TODO
----

Add support for YAML config files to setup parsers


How to run the tests?
---------------------

::

        python txtblocks/tests/test_txtblocks.py
        python3 txtblocks/tests/test_txtblocks.py


Windows
-------

If you run the setup on Windows you'll need to have git installed. Pbr tries to figure out the version number via git. I'll need to fix this "soon".


Feedback
--------


Bug reports, patches and ideas are welcome.

Just send me an e-mail (jochenbartl@mailbox.org) or open an issue on GitHub














