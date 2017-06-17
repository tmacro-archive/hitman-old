'''
	This module defines constant for use 
	when interacting with the bot module
'''

from collections import namedtuple

def const_type(label, const):
	'''
		Generates a namedtuple of `label` type with 
		`const` as the field names, assigning 
		each one a successive unique integer
	'''
	l = len(const)
	return namedtuple(label, const)(**{const[x]:x for x in range(l)})

EVENT_TYPES = [
		'NULL',
		'BASE',
		'MSG',
		'CMD',
		'USER'
	]

EVENT_TYPES = const_type('EVENT_TYPES', EVENT_TYPES)

CMD_TYPES = [
		'NULL',
		'REGISTER',
		'REPORT',
		'TARGET'
	]

CMD_TYPES = const_type('CMD_TYPES', CMD_TYPES)
