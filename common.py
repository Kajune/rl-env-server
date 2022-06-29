import pickle, base64, zlib


def encode(obj):
	return base64.b64encode(zlib.compress(pickle.dumps(obj))).decode("utf-8")


def decode(text):
	return pickle.loads(zlib.decompress(base64.b64decode(text.encode())))
