import pickle, base64, zlib


def encode(obj):
	return zlib.compress(pickle.dumps(obj))


def decode(text):
	return pickle.loads(zlib.decompress(text))
