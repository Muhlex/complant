from machine import Timer
from uasyncio import create_task
from uasyncio.event import ThreadSafeFlag

from .ledring import LEDRing

class Lights:
	def __init__(self, ledring: LEDRing):
		self._leds = ledring
		self._standby_timer = Timer(0)
		self._standby_flag = ThreadSafeFlag()
		self._standby_active = False

	def reset_standby(self):
		from . import models
		self._standby_timer.init(mode=Timer.ONE_SHOT,
		                         period=models.config["periods"]["light"] * 1000,
		                         callback=lambda _: self._standby_flag.set())
		if self._standby_active:
			self.on_idle()
		self._standby_active = False

	def init(self):
		create_task(self._wait_standby())
		self.reset_standby()

	async def _wait_standby(self):
		while True:
			await self._standby_flag.wait()
			self._on_standby()

	def _on_standby(self):
		self._standby_active = True
		leds = self._leds
		leds.transition(3000)
		leds.clear()

	def on_boot(self):
		leds = self._leds
		leds.transition(600)
		leds.circle(leds.COLOR_PRIMARY, gap=-2, interval=80)

	def on_idle(self):
		leds = self._leds
		leds.transition()
		leds.static(leds.COLOR_MOISTURE)

	def on_talk(self):
		leds = self._leds
		leds.transition(600)
		leds.circle(leds.COLOR_MOISTURE)
