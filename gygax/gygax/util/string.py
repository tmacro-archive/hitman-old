from base64 import urlsafe_b64decode, urlsafe_b64encode

def enc(s):
	return str(s).encode()

def enc64(s):
	return urlsafe_b64encode(s.encode())

def dec64(s):
	return urlsafe_b64decode(s).decode()