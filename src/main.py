from complant.api import API
from complant.webserver import Webserver
from complant.config import Config
from complant.wifi import init as initWiFi

from uasyncio import get_event_loop, run, create_task, sleep_ms
from machine import Pin
from neopixel import NeoPixel

from moisture import MoistureSensor
from dfplayer import DFPlayer

config = Config("data/config.json")

# "Abuse" static classes as namespaces to organize our stuff:
class io:
	led = Pin(2, Pin.OUT)
	pixels = NeoPixel(Pin(23, Pin.OUT), n=24)
	audio = DFPlayer(2)

	motion = Pin(21, Pin.IN)
	moisture = MoistureSensor(Pin(34, Pin.IN))


async def demo_pixels(np: NeoPixel):
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

	await initWiFi(config)

	api = API(config=config, audio=io.audio)
	webserver = Webserver(api, root="webgui/")
	create_task(webserver.init())

	volume = config.values["volume"]
	print("Setting volume to", volume)
	await io.audio.volume(volume)
	print("DFPlayer volume reports:", await io.audio.volume())

	await io.audio.play_root(2)

	print("Entering main loop")
	while True:
		await sleep_ms(1000)

try:
	run(main())

except KeyboardInterrupt:
	print("Exiting gracefully...")

finally:
	print("Cleaning up...")
	get_event_loop().close()
	io.led.off()
	io.pixels.fill((0, 0, 0))
	io.pixels.write()
	try:
		run(io.audio.reset())
	except Exception as error:
		print("DF Player couldn't reset:", error)
