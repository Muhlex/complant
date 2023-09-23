from machine import Pin
from time import sleep_ms
from neopixel import NeoPixel

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


try:
	print("Running NeoPixel demo.")
	demo_pixels(IO.pixels)
	print("Blinking inbuilt LED.")
	while True:
		IO.led.on()
		sleep_ms(800)
		IO.led.off()
		sleep_ms(2000)

except KeyboardInterrupt:
	print("Exiting gracefully...")

finally:
	print("Cleaning up...")
	IO.led.off()
	IO.pixels.fill((0, 0, 0))
	IO.pixels.write()
