
from machine import Pin, ADC
from util import create_remap, median

class MoistureSensor:
	def __init__(self, pin = Pin, read_count = 5):
		self._adc = ADC(pin)
		self._adc.width(ADC.WIDTH_10BIT)
		self._normalize = create_remap(0, 2 ** ADC.WIDTH_10BIT - 1, 0, 1)
		self._readings = [0] * read_count

	def read(self):
		for i in range(len(self._readings)):
			self._readings[i] = self._adc.read()
		return self._normalize(median(self._readings))
