from ..util.crypto import gen_signature, expiring_token, check_token, token_ttl, rand_key
from ..util.time import timestamp, from_timestamp, convert_delta
from ..util.string import enc64, dec64
import time
import json



def test_generation():
	for x in range(150):
		key = rand_key()
		secret = rand_key()
		exp = timestamp()
		sig1 = gen_signature(secret, key, dict(x=x), exp)
		sig2 = gen_signature(secret, key, dict(x=x), exp)
		assert sig1 == sig2

def test_expiration():
	for x in range(10):
		key = rand_key()
		secret = rand_key()
		sig = expiring_token(secret, key, dict(x=x), None, token_ttl)
		time.sleep(1)
		assert check_token(secret, key, sig, dict(x=x)) == True
	for x in range(10):
		key = rand_key()
		secret = rand_key()
		exp = timestamp()
		sig = expiring_token(secret, key, dict(x=x), exp)
		time.sleep(1)
		assert check_token(secret, key, sig, dict(x=x)) == False

def bad_sig():
	for x in range(150):
		key = rand_key()
		secret = rand_key()
		exp = timestamp()
		sig1 = gen_signature(secret, key, dict(x=x), exp)
		sig2 = gen_signature(secret, key, dict(x=x-1), exp)
		assert sig1 != sig2

def inject_timestamp(ts, token):
	data = json.loads(dec64(token))
	data['exp'] = ts
	return enc64(json.dumps(data))

def false_expiry():
	for x in range(50):
		key = rand_key()
		secret = rand_key()
		good_exp = timestamp(offset=convert_delta('5m'))
		bad_exp = timestamp(offset=convert_delta('30m'))
		sig1 = expiring_token(secret, key, dict(x=x), good_exp)
		sig2 = inject_timestamp(bad_exp, sig1)
		assert check_token(secret, key, sig2, dict(x=x)) == False
		assert check_token(secret, key, sig1, dict(x=x)) == True
		
def run_all():
	test_generation()
	test_expiration()
	bad_sig()
	false_expiry()
