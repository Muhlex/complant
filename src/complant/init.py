from os import mkdir
from machine import Pin

from neopixel import NeoPixel
from moisture import MoistureSensor
from dfplayer import DFPlayer

from .config import Config
from .wifi import WiFi
from .webserver import API, Webserver
from .plants import Plants
from .ledring import LEDRing
from .moisture import Moisture

try: mkdir("data")
except: pass

class IO:
	def __init__(self):
		self.led = Pin(2, Pin.OUT)
		self.pixels = NeoPixel(Pin(23, Pin.OUT), n=24)
		self.dfplayer = DFPlayer(2)

		self.motion = Pin(21, Pin.IN)
		self.moisture = MoistureSensor(Pin(34, Pin.IN))
io = IO()

class Models:
	def __init__(self):
		self.config = Config("data/config.json")
		self.wifi = WiFi()
		self.api = API()
		self.webserver = Webserver(api=self.api, root="webgui/")
		self.plants = Plants()

		self.ledring = LEDRing(io.pixels)

		self.moisture = Moisture(io.moisture)
models = Models()
