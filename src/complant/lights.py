from machine import Timer
from uasyncio import create_task
from uasyncio.event import ThreadSafeFlag

from .ledring import LEDRing

class Lights:
	def __init__(self, ledring: LEDRing):
		self._leds = ledring
		self._timeout_timer = Timer(0)
		self._timeout_flag = ThreadSafeFlag()
		self._timeout_active = False

	def reset_timeout(self):
		from . import models
		self._timeout_timer.init(mode=Timer.ONE_SHOT,
		                         period=models.config["periods"]["light"] * 1000,
		                         callback=lambda _: self._timeout_flag.set())
		if self._timeout_active:
			self._timeout_active = False
			self.idle()
		else:
			self._timeout_active = False

	def init(self):
		create_task(self.wait_timeout())
		self.reset_timeout()

	async def wait_timeout(self):
		while True:
			await self._timeout_flag.wait()
			self._timeout()

	def _timeout(self):
		self._timeout_active = True
		leds = self._leds
		leds.transition(3000)
		leds.clear()

	def boot(self):
		if self._timeout_active: return
		leds = self._leds
		leds.transition(600)
		leds.circle(leds.COLOR_PRIMARY, gap=-2, interval=80)

	def idle(self):
		if self._timeout_active: return
		leds = self._leds
		leds.transition()
		leds.static(leds.COLOR_MOISTURE)

	def talk(self):
		if self._timeout_active: return
		leds = self._leds
		leds.transition(300)
		leds.circle(leds.COLOR_MOISTURE)
