from complant import io, models

from uasyncio import run, create_task, sleep_ms

async def main():
	models.lights.init()
	models.moisture.init()
	models.motion.init()

	models.lights.on_boot()

	await models.wifi.init()

	models.lights.on_idle()

	volume = models.config["volume"]
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
