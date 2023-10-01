import os # might fix a pymakr error

from uasyncio import run, create_task, sleep_ms
from machine import Pin
from neopixel import NeoPixel

from moisture import MoistureSensor
from dfplayer import DFPlayer

# "Abuse" static classes as namespaces to organize our stuff:
class IO:
	led = Pin(2, Pin.OUT)
	pixels = NeoPixel(Pin(23, Pin.OUT), n=24)
	audio = DFPlayer(2)

	motion = Pin(21, Pin.IN)
	moisture = MoistureSensor(Pin(34, Pin.IN))

async def main():
	create_task(demo_pixels(IO.pixels))

	volume = 5
	eq = DFPlayer.EQ_JAZZ

	print("Setting volume to", volume)
	await IO.audio.volume(volume)
	print("DFPlayer volume reports:", await IO.audio.volume())

	print("Setting equalizer to", eq)
	await IO.audio.eq(eq)
	print("DFPlayer equalizer reports:", await IO.audio.eq())

	await IO.audio.play_root(1)

	print("Doing stupid things...")
	create_task(IO.audio.volume())
	create_task(IO.audio.eq())

	while True:
		print("Moisture:", IO.moisture.read() * 100, "%")
		await sleep_ms(1000)

async def demo_pixels(np: NeoPixel):
	while True:
		n = np.n

		for i in range(n):
			np.fill((1, 0, 0))
			np[i % n] = (0, 0, 0)
			np[(i + 1) % n] = (0, 0, 0)
			np.write()
			await sleep_ms(60)
		for i in range(n):
			np.fill((0, 1, 0))
			np[i % n] = (0, 0, 0)
			np[(i + 1) % n] = (0, 0, 0)
			np.write()
			await sleep_ms(60)
		for i in range(n):
			np.fill((0, 0, 1))
			np[i % n] = (0, 0, 0)
			np[(i + 1) % n] = (0, 0, 0)
			np.write()
			await sleep_ms(60)

try:
	run(main())

	# print("Showing motion sensor data on internal LED.")
	# while True:
	# 	IO.led.value(IO.motion.value())
	# 	sleep_ms(20)

	# print("Running NeoPixel demo.")
	# demo_pixels(IO.pixels)
	# volume = 15
	# play = (1, 1)
	# eq = DFPlayer.EQ_JAZZ
	# states = [None] * 3
	# states[DFPlayer.STATE_PAUSED] = "paused"
	# states[DFPlayer.STATE_PLAYING] = "playing"
	# states[DFPlayer.STATE_STOPPED] = "stopped"

	# print("Setting volume to", volume)
	# IO.audio.volume(volume)
	# print("DFPlayer volume reports:", IO.audio.volume())

	# print("Setting equalizer to", eq)
	# IO.audio.eq(eq)
	# print("DFPlayer equalizer reports:", IO.audio.eq())

	# print("Playing track", play[0], "in folder", play[1])
	# IO.audio.play(*play)

	# print("DFPlayer state:", states[IO.audio.state()])

	# sleep_ms(300)
	# IO.audio.play("advert", 1)
	# sleep_ms(300)
	# IO.audio.play("advert", 1)

	# sleep_ms(4000)
	# print("Pausing")
	# IO.audio.pause()
	# print("DFPlayer state:", IO.audio.state())

	# sleep_ms(1500)
	# print("Resuming")
	# IO.audio.resume()
	# print("DFPlayer state:", IO.audio.state())

	# sleep_ms(1500)
	# print("Stopping")
	# IO.audio.stop()
	# print("DFPlayer state:", IO.audio.state())

except KeyboardInterrupt:
	print("Exiting gracefully...")

finally:
	print("Cleaning up...")
	IO.led.off()
	IO.pixels.fill((0, 0, 0))
	IO.pixels.write()
	try:
		run(IO.audio.reset())
	except Exception as e:
		print("DF Player couldn't reset:", e)
