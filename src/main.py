from complant import io, models

from uasyncio import run, create_task, sleep_ms

async def main():
	models.ledring.transition(600)
	models.ledring.circle(models.ledring.COLOR_PRIMARY, gap=io.pixels.n - 2, interval=80)

	models.moisture.init()

	await models.wifi.init()
	models.ledring.transition()
	models.ledring.static(models.ledring.COLOR_MOISTURE)

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
