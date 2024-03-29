try: from typing import Callable
except ImportError: pass

from machine import Pin
from uasyncio import create_task
from uasyncio.event import ThreadSafeFlag

class MotionSensor:
	def __init__(self, pin = Pin, on_activate: Callable | None = None):
		self._pin = pin
		self._irq_flag = ThreadSafeFlag()
		self.on_activate = on_activate

	def init(self):
		self._pin.irq(self._isr, trigger=Pin.IRQ_RISING)
		create_task(self._wait_activate())

	def _isr(self, _):
		self._irq_flag.set()

	async def _wait_activate(self):
		while True:
			await self._irq_flag.wait()
			if self.on_activate is not None:
				self.on_activate()
