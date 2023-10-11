
from machine import Pin, ADC
from uasyncio import sleep_ms

from util import create_remap, clamp, median

class MoistureSensor:
	def __init__(self, pin = Pin, read_count = 5):
		self._adc = ADC(pin, atten=ADC.ATTN_11DB)
		self._normalize = create_remap(144, 2060, 0.0, 1.0)
		self._readings = [0] * read_count

	async def read(self):
		for i in range(len(self._readings)):
			self._readings[i] = self._adc.read_uv()
			await sleep_ms(0)
		return clamp(self._normalize(median(self._readings) // 1000), 0.0, 1.0)
