from complant import io, models

from uasyncio import run, create_task, sleep_ms
from neopixel import NeoPixel

async def demo_pixels(np: NeoPixel):
	print("Running NeoPixel Demo.")
	n = np.n
	while True:
		for i in range(n):
			np.fill((1, 1, 1))
			np[i % n] = (0, 0, 0)
			np[(i + 1) % n] = (0, 0, 0)
			np.write()
			await sleep_ms(60)

async def main():
	create_task(demo_pixels(io.pixels))
	await sleep_ms(0)

	await models.wifi.init()

	volume = models.config.values["volume"]
	print("Setting volume to", volume)
	await io.dfplayer.volume(volume)
	print("DFPlayer volume reports:", await io.dfplayer.volume())

	await io.dfplayer.play_root(2)

	print("Entering main loop")
	while True:
		await sleep_ms(1000)

try:
	run(main())

except KeyboardInterrupt:
	print("Exiting gracefully...")

finally:
	print("Cleaning up...")
	try:
		io.led.off()
		io.pixels.fill((0, 0, 0))
		io.pixels.write()
		models.wifi.reset()
		create_task(io.dfplayer.reset())
	except Exception as error:
		print("Error occured on cleanup:\n", error)
