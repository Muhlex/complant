from uasyncio import create_task

from motion import MotionSensor

class Motion():
	def __init__(self, sensor: MotionSensor):
		self._sensor = sensor
		sensor.on_activate = self._on_motion

	def init(self):
		self._sensor.init()

	def _on_motion(self):
		from . import models
		models.lights.reset_timeout()
		if models.wifi.is_host:
			models.conversation.trigger()
		elif models.wifi.is_client:
			create_task(models.plants.host.api.post("/host/motion"))
