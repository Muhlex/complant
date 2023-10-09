from complant import io, models

from gc import collect as gc_collect
from uasyncio import run, sleep_ms, new_event_loop

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
	await sleep_ms(5000)
	await io.dfplayer.play(1, 1)
	await sleep_ms(5000)
	await io.dfplayer.play("mp3", 1)
	await sleep_ms(5000)
	await io.dfplayer.play("advert", 1)
	await io.dfplayer.wait_done()
	print("done playing the button sound")

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
		new_event_loop()
		io.led.off()
		io.pixels.fill((0, 0, 0))
		io.pixels.write()
		models.wifi.reset()
		run(io.dfplayer.reset())
		gc_collect()
	except Exception as error:
		print("Error occured on cleanup:\n", error)
