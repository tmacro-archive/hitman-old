'''
	This module defines constant for use 
	when interacting with the bot module
'''

from collections import namedtuple

EVENT_TYPES = [
		'BASE',
		'MSG'
	]

EVENT_TYPES = namedtuple('EVENT_TYPES', EVENT_TYPES)(**{EVENT_TYPES[x]:x for x in range(len(EVENT_TYPES))})
