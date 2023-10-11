from moisture import MoistureSensor
from uasyncio import create_task, sleep_ms

class Moisture():
	def __init__(self, sensor: MoistureSensor):
		self._sensor = sensor
		self.value = 0.0

	def init(self):
		create_task(self._update())

	@property
	def dry(self) -> bool:
		from . import models
		return self.value < models.config["moisture"]

	async def _update(self):
		while True:
			self.value = await self._sensor.read()
			await sleep_ms(1000)
