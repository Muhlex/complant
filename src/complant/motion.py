from motion import MotionSensor

class Motion():
	def __init__(self, sensor: MotionSensor):
		self._sensor = sensor
		sensor.on_activate = self._on_movement

	def init(self):
		self._sensor.init()

	async def _on_movement(self):
		from . import models
		models.lights.reset_standby()
