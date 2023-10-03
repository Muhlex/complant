from os import stat

def median(data):
	data = sorted(data)
	n = len(data)
	if n & 1:
		return data[n // 2]
	else:
		i = n // 2
		return (data[i - 1] + data[i]) / 2

def create_remap(in_min: int | float, in_max: int | float, out_min: int | float, out_max: int | float):
	scale_factor = float(out_max - out_min) / float(in_max - in_min)
	def fn(value):
		return (value - in_min) * scale_factor + out_min
	return fn

def path_exists(path: str):
	try:
		stat(path)
		return True
	except OSError:
		return False
