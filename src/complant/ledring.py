try: from typing import Callable
except ImportError: pass

from neopixel import NeoPixel
from uasyncio import create_task, sleep_ms, Task

from util import remap, create_remap

def apply_brightness(color: tuple[int, ...]) -> tuple[int, ...]:
	from . import models
	brightness = models.config["brightness"]
	result = tuple(int(component * brightness) for component in color)
	return result

def create_colors_interp(from_color: tuple[int, ...], to_color: tuple[int, ...]):
	interp_funcs = tuple(create_remap(0, 1, from_color[i], to_color[i]) for i in range(len(from_color)))
	def fn(frac: float):
		return tuple(int(func(frac)) for func in interp_funcs)
	return fn

class LEDRing():
	@staticmethod
	def COLOR_NONE(): return (0, 0, 0)
	@staticmethod
	def COLOR_PRIMARY(): return apply_brightness((20, 255, 0))
	@staticmethod
	def COLOR_MOISTURE():
		from . import models
		color_neutral = (255, 160, 80)
		interp_dry_to_neutral = create_colors_interp((255, 25, 0), color_neutral)
		interp_neutral_to_wet = create_colors_interp(color_neutral, (60, 140, 230))
		moisture_value = models.moisture.value
		moisture_thresh = models.config["moisture"]
		moisture_neutral = moisture_thresh + 0.25
		if (moisture_value < moisture_neutral):
			color = interp_dry_to_neutral(moisture_value / moisture_neutral)
		else:
			color = interp_neutral_to_wet((moisture_value - moisture_neutral) / (1 - moisture_neutral))
		return apply_brightness(color)

	def __init__(self, neopixel: NeoPixel):
		self._np = neopixel
		self._anim_task: Task | None = None
		self._trans_task: Task | None = None
		# "Abuse" the NeoPixel class for it's API to hold different light states ("frames")
		self._anim_frame = NeoPixel(pin=neopixel.pin, n=neopixel.n)
		self._trans_frame_start = NeoPixel(pin=neopixel.pin, n=neopixel.n)
		self._trans_frac: float | None = None

	def _set_anim(self, coro):
		if self._anim_task is not None:
			self._anim_task.cancel()
		self._anim_task = create_task(coro())

	def transition(self, duration = 1000, fps = 20):
		delay = 1000 // fps
		frames = duration // delay

		async def coro():
			self._trans_frame_start.buf = self._np.buf[:]
			for i in range(frames):
				self._trans_frac = i / frames
				self._render()
				await sleep_ms(delay)
			self._trans_frac = None

		if self._trans_task is not None:
			self._trans_task.cancel()
		self._trans_task = create_task(coro())

	def _render(self):
		np = self._np
		if self._trans_frac is None: # no transition in progress, render animation
			np.buf = self._anim_frame.buf[:]
		else: # render transitioned animation
			trans_frame_start = self._trans_frame_start
			anim_frame = self._anim_frame
			for i in range(len(np.buf)):
				np.buf[i] = int(remap(self._trans_frac, 0.0, 1.0, trans_frame_start.buf[i], anim_frame.buf[i]))
		np.write()

	def clear(self):
		self.static(LEDRing.COLOR_NONE)

	def static(self, get_color: Callable[..., tuple[int, ...]]):
		async def anim():
			# Color getter result may change, thus also update the static color regularly:
			while True:
				self._anim_frame.fill(get_color())
				self._render()
				await sleep_ms(300)
		self._set_anim(anim)

	def circle(self, get_color: Callable[..., tuple[int, ...]], gap = 5, interval = 50):
		frame = self._anim_frame
		n = self._anim_frame.n
		async def anim():
			frame.fill(get_color())
			while True:
				for i in range(n):
					color = get_color()
					color_none = LEDRing.COLOR_NONE()
					interp = create_colors_interp(color_none, color)
					for gap_i in range(gap): # move gap by one
						if gap < 3 or (gap_i > 0 and gap_i < gap - 1):
							frame[(i + gap_i) % n] = color_none
						else:
							frame[(i + gap_i) % n] = interp(0.2)
					frame[(i - 1) % n] = color # close last pixel of previous gap
					self._render()
					await sleep_ms(interval)
		self._set_anim(anim)
