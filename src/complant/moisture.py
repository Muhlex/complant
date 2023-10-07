from moisture import MoistureSensor
from uasyncio import create_task, sleep

class Moisture():
	def __init__(self, sensor: MoistureSensor):
		self._sensor = sensor
		self.value = 0.0

	def init(self):
		create_task(self._update())

	async def _update(self):
		# using mock data for now:
		self.value = 1.0
		while True:
			# self.value = self._sensor.read()
			value = self.value - 0.05
			if value < 0.0: value = 1.0
			self.value = value
			await sleep(1.5)
