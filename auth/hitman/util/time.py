from datetime import timedelta, datetime
from .config import config

def convert_delta(interval):
	'''
		Converts a timespan represented as a space seperated string 
		Xy Xd Xh Xm Xs to a datetime.timedelta object
		all segments are optional eg '2d 12h', '10m 30s', '1y 30s'
	'''
	seg_map = dict( h='hours',
					m='minutes',
					s='seconds',
					y='years',
					d='days')
	segs = interval.split(' ')
	kwargs = { seg_map[seg[-1]]: int(seg[:-1]) for seg in segs }
	return timedelta(**kwargs)

def timestamp(offset = None):
	t = datetime.utcnow()
	if offset:
		t += offset
	return t.strftime(config.token.timestamp.format)

def is_expired(timestamp):
	t = datetime.strptime(timestamp, config.token.timestamp.format)
	return t <= datetime.utcnow()

def from_timestamp(timestamp):
	return datetime.strptime(timestamp, config.token.timestamp.format)
