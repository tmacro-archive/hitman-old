from .config import config
from .log import getLogger
from .time  import convert_delta, timestamp, is_expired
from .string import enc64, dec64, enc
import os
import hashlib
import hmac
from base64 import b64encode, b64decode
import json

_log = getLogger('util.crypto')

token_ttl = convert_delta(config.token.ttl)

def h512(data):
	return hashlib.sha512(data.encode('utf-8')).hexdigest()

def rand_key():
	seed = os.urandom(256)
	h = h512(str(seed))
	for x in range(50):
		h = h512(h)
	return h

def gen_signature(secret, key, extra = None, exp = None, ttl = token_ttl):
	_log.debug('Generating signature for %s, exp: %s'%(h512(secret), exp))
	if isinstance(ttl, str):
		ttl = convert_delta(ttl)
	expiration = timestamp(ttl) if not exp else exp
	to_sign = enc('%s_%s'%(secret, expiration))
	digest = hmac.new(enc(key), to_sign, hashlib.sha512)
	if extra:
		for item in extra:
			digest.update(enc(str(extra)))
	_log.debug('Generated signature for %s, expire: %s'%(h512(secret), expiration))
	return h512(digest.hexdigest()), expiration
	
def expiring_token(secret, key, extra = None, exp = None, ttl = token_ttl):
	_log.debug('Generating expiring token for %s exp: %s'%(h512(secret), exp))
	signature, expiration = gen_signature(secret, key, extra, exp, ttl)
	token = json.dumps(dict(sig=signature, exp=expiration))
	_log.debug('Generated token %s for %s, expire: %s'%(token, h512(secret), expiration))
	return enc64(token)

def check_token(secret, key, token, extra = None):
	try:
		data = json.loads(dec64(token))
		_log.debug(data)
		if 'sig' in data and 'exp' in data:
			gend , exp = gen_signature(secret, key, extra, exp = data['exp'])
			if hmac.compare_digest(gend, data['sig']):
				if is_expired(data['exp']):
					_log.debug('Token %s for %s is expired'%(token, h512(secret)))
					return False
				return True
			else:
				_log.debug('Token %s is not valid'%json.loads(dec64(token)))
				_log.debug('%s - %s'%(gend, data['sig']))
		else:
			_log.debug('Not enough info in token')
	except Exception as e:
		_log.debug('Failed to decode token %s'%token)
		_log.exception(e)
	return False

def token_info(token):
	try:
		data = json.loads(b64decode(token))
		return str(data)
	except:
		pass
	return None	