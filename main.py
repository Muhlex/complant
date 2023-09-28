from machine import Pin
from time import sleep_ms
from neopixel import NeoPixel
from dfplayer import DFPlayer

def demo_pixels(np: NeoPixel):
	n = np.n

	# cycle
	for i in range(4 * n):
		for j in range(n):
			np[j] = (0, 0, 0)
		np[i % n] = (255, 255, 255)
		np.write()
		sleep_ms(25)

	# bounce
	for i in range(4 * n):
		for j in range(n):
			np[j] = (0, 0, 128)
		if (i // n) % 2 == 0:
			np[i % n] = (0, 0, 0)
		else:
			np[n - 1 - (i % n)] = (0, 0, 0)
		np.write()
		sleep_ms(60)

	# fade in/out
	for i in range(0, 4 * 256, 8):
		for j in range(n):
			if (i // 256) % 2 == 0:
				val = i & 0xff
			else:
				val = 255 - (i & 0xff)
			np[j] = (val, 0, 0)
		np.write()

	# clear
	np.fill((0, 0, 0))
	np.write()


# "Abuse" static classes as namespaces to organize our stuff:
class IO:
	led = Pin(2, Pin.OUT)
	pixels = NeoPixel(Pin(23, Pin.OUT), 24)
	# audio = DFPlayer(2, tx=17, rx=16)
	audio = DFPlayer(2)

	motion = Pin(22, Pin.IN)


try:
	# print("Running NeoPixel demo.")
	# demo_pixels(IO.pixels)
	# print("Showing motion sensor data on internal LED.")
	# while True:
	# 	IO.led.value(IO.motion.value())
	# 	sleep_ms(20)
	volume = 15
	play = (1, 1)
	eq = DFPlayer.EQ_JAZZ
	states = [None] * 3
	states[DFPlayer.STATE_PAUSED] = "paused"
	states[DFPlayer.STATE_PLAYING] = "playing"
	states[DFPlayer.STATE_STOPPED] = "stopped"

	print("Setting volume to", volume)
	IO.audio.volume(volume)
	print("DFPlayer volume reports:", IO.audio.volume())

	print("Setting equalizer to", eq)
	IO.audio.eq(eq)
	print("DFPlayer equalizer reports:", IO.audio.eq())

	# print("Playing track", play[0], "in folder", play[1])
	# IO.audio.play(*play)

	IO.audio.play("mp3", 1)

	print("DFPlayer state:", states[IO.audio.state()])

	sleep_ms(300)
	IO.audio.play("advert", 1)
	sleep_ms(300)
	IO.audio.play("advert", 1)

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

	while True:
		sleep_ms(100)
		pass

except KeyboardInterrupt:
	print("Exiting gracefully...")

finally:
	print("Cleaning up...")
	IO.led.off()
	IO.pixels.fill((0, 0, 0))
	IO.pixels.write()
	IO.audio.reset()
