import gc

from complant import io, models
gc.collect()

from uasyncio import run, sleep, new_event_loop
from uasyncio.funcs import gather

async def main():
	models.lights.init()
	models.moisture.init()

	models.lights.boot()

	await gather(models.wifi.init(), models.audio.init())

	models.lights.idle()
	await models.audio.startup()
	models.motion.init()

	while True:
		await sleep(600)

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
	except Exception as error:
		print("Error occured on cleanup:\n", error)
