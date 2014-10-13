# txtblocks - Helper for network device CLI screen scraping adventures

I'll try to write a parser which helps me through my Cisco CLI screen scraping adventures.
This is just one of my toy projects.

If you are looking for a good parser you should give [textfsm](https://code.google.com/p/textfsm/) a try.


## Usage Examples


Some text from "show cdp neigh detail"

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



```python
# Parse a single line within a text block
deviceid = TextLine('deviceid', '^Device ID: (?P<deviceid>.+)$')
# cdpentry -> Name of the text block
# [deviceid, ...] -> TextLine elements within the TextBlock
# Last parameter defines how the start of a text block looks like
txtblock = TextBlock('cdpentry', [deviceid], '^Device ID:')
blockparser = BlockParser(text, [txtblock])
```

TODO Add support for YAML config files to setup parsers

## Feedback

Bug reports, patches and ideas are welcome.

Just send me an e-mail (jochenbartl@mailbox.org) or open an issue on GitHub
