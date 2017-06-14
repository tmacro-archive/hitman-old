def enc(s):
	if isinstance(s, str):
		return s.encode('utf-8')
	return s