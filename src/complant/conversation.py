from machine import Timer
from uasyncio import create_task
from uasyncio.funcs import gather
from random import choice

from .plant import Plant
from .characters import Character

class Conversation:
	def __init__(self):
		self._timer = Timer(1)
		self._active = False
		self._timeout = False

	def trigger(self):
		create_task(self._try_start())

	def reset_timeout(self):
		self._timer.deinit()
		self._timeout = False

	async def _try_start(self):
		if self._active or self._timeout:
			return

		from . import models
		plants = models.plants.all()
		plants_dry_per_index = await gather(*[plant.get_dry() for plant in plants])
		plants_dry = [plants[i] for i, dry in enumerate(plants_dry_per_index) if dry]
		if len(plants_dry) == 0:
			return

		a = choice(plants_dry)
		if len(plants) > 1:
			plants.remove(a)
			b = choice(plants)
		else:
			b = None

		self._active = True
		await self._start(a, b)
		self._active = False

		self._timeout = True
		def end_timeout(_): self._timeout = False
		self._timer.init(mode=Timer.ONE_SHOT,
		                 period=models.config["periods"]["conversation"] * 1000,
		                 callback=end_timeout)

	async def _start(self, a: Plant, b: Plant | None = None):
		if b is None:
			print("Starting solo conversation:", a.ip)
		else:
			print("Starting conversation between", a.ip, "&", b.ip)

		await a.talk(Character.TOPIC_SOIL, Character.MOISTURE_DRY)
		if b is None: return

		b_moisture = Character.MOISTURE_DRY if (await b.get_dry()) else Character.MOISTURE_WET
		await b.talk(Character.TOPIC_SOIL, Character.MOISTURE_DRY, b_moisture)

		b_trait = await b.get_trait()
		await a.talk(Character.TOPIC_SOIL, Character.MOISTURE_DRY, b_moisture, b_trait)
