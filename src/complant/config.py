from io import StringIO
from json import load, dump

from util import path_exists

class Config:
	def __init__(self, path: str):
		self._path = path
		self.values = { # default values
			"name": "Unnamed Complant",
			"volume": 15,
			"brightness": 0.5,
			"moisture": 0.25,
			"character": 0,
			"periods": {
				"light": 60 * 5,
				"conversation": 60 * 60,
			},
			"wifi": {
				"ssid": "Complant",
				"key": "complant"
			}
		}

		if not path_exists(self._path):
			self.save()
		else:
			self.load()

	def save(self):
		file: StringIO = open(self._path, "w")
		dump(self.values, file)
		file.close()

	def load(self):
		file: StringIO = open(self._path, "r")
		self.values = load(file)
		file.close()

	def __getitem__(self, key):
		return self.values[key]

	def __setitem__(self, key, value):
		self.values[key] = value
