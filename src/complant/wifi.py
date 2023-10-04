from uasyncio import sleep_ms
from network import WLAN, AP_IF, AUTH_WPA2_PSK, hostname

from .config import Config

async def init(config: Config):
	hostname("complant")

	ap = WLAN(AP_IF)
	ap.active(True)
	ap.config(ssid="Complant", security=AUTH_WPA2_PSK, key=config.values["wifi"]["key"])
	ap.ifconfig(("192.168.6.1", "255.255.255.0", "192.168.6.1", "1.1.1.1"))

	while ap.active() == False:
		await sleep_ms(50)

	print("AP creation successful")
	print("Interface config:", ap.ifconfig())
