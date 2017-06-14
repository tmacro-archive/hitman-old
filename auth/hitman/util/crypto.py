from .config import config
from .time  import convert_delta, timestamp, is_expired
from .string import enc
import os
import hashlib
import hmac
from base64 import b64encode, b64decode
import json

token_ttl = convert_delta(config.token.ttl)

def h512(data):
	return hashlib.sha512(data.encode('utf-8')).hexdigest()

def rand_key():
	seed = os.urandom(256)
	h = h512(str(seed))
	for x in range(50):
		h = h512(h)
	return h

def gen_signature(secret, key, exp = None, ttl = token_ttl):
	if isinstance(ttl, str):
		ttl = convert_delta(ttl)
	expiration = timestamp(ttl) if not exp else exp
	to_sign = enc('%s_%s'%(secret, expiration))
	digest = hmac.new(enc(key), to_sign, hashlib.sha512)
	return h512(digest.hexdigest()), expiration
	
def expiring_token(secret, key, exp = None, ttl = token_ttl):
	signature, expiration = gen_signature(secret, key, exp, ttl)
	token = json.dumps(dict(sig=signature, exp=expiration))
	return b64encode(enc(token))

def check_token(secret, key, token):
	try:
		data = json.loads(b64decode(token))
		if 'sig' in data and 'exp' in data:
			gend , exp = gen_signature(secret, key, data['exp'])
			if hmac.compare_digest(gend, data['sig']):
				return is_expired(data['exp'])
	except:
		pass
	return False

def token_info(token):
	try:
		data = json.loads(b64decode(token))
		return str(data)
	except:
		pass
	return None		