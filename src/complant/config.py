from io import StringIO
from json import load, dump

from util import path_exists

class Config:
	def __init__(self, path: str):
		self._path = path
		self.values = { # default values
			"volume": 15,
			"brightness": 2,
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
