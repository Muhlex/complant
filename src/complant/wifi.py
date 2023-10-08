from micropython import const
from uasyncio import create_task, sleep, sleep_ms
from network import WLAN, STA_IF, AP_IF, AUTH_WPA_WPA2_PSK, hostname

from network_asyncio import AsyncWLAN
from .plant import Plant

HOST_IP = const("192.168.6.1")

class WiFi():
	def __init__(self):
		hostname("complant")
		self._sta = WLAN(STA_IF)
		self._ap = WLAN(AP_IF)
		self._async = AsyncWLAN()
		self.is_client = False
		self.is_host = False

	async def init(self):
		if not await self._init_client():
			await self._init_host()

		create_task(self._watch_status())

	async def _init_host(self):
		from . import models, io
		ap = self._ap
		sta = self._sta
		wifi_config = models.config["wifi"]

		self.is_host = True
		io.led.on()

		if self.is_client:
			self.is_client = False
			models.plants.clear_host()
			sta.active(False)
			print("Terminated client WiFi station for this Complant.")

		ap.active(True)
		# This blocks for quite a while, but seems impossible to work around
		# (using another thread doesn't work):
		ap.config(ssid=wifi_config["ssid"], key=wifi_config["key"], security=AUTH_WPA_WPA2_PSK)
		ap.ifconfig((HOST_IP, "255.255.255.0", HOST_IP, "1.1.1.1"))

		models.webserver.init(HOST_IP)

		while ap.active() == False:
			await sleep_ms(50)

		print("Successfully initialized as Complant host.")
		return True

	async def _init_client(self):
		from . import models, io
		sta = self._sta
		ap = self._ap
		wifi_config = models.config["wifi"]

		print("Scanning for Complant host network...")
		sta.active(True)
		networks = await self._async.scan(sta)
		if not any(network[0].decode("UTF-8") == wifi_config["ssid"] for network in networks):
			print("No Complant host network available.")
			sta.active(False)
			return False

		print("Host Complant found. Connecting to their network...")
		sta.connect(wifi_config["ssid"], wifi_config["key"])
		timeout = 8000
		while sta.isconnected() == False:
			await sleep_ms(50)
			timeout -= 50
			if (timeout <= 0):
				print("Connection to host network failed.")
				sta.active(False)
				return False

		print("Connected. Registering this Complant client with host...")
		host = Plant(ip=HOST_IP)
		try:
			await host.api.put("/host/register", {})
		except Exception as error:
			print("Registration failed. Error:", error)
			sta.active(False)
			return False

		self.is_client = True
		models.plants.set_host(host)

		models.webserver.init(sta.ifconfig()[0])

		if self.is_host:
			self.is_host = False
			io.led.off()
			models.plants.clear_clients()
			ap.active(False)
			print("Terminated host WiFi access point for this Complant.")

		print("Successfully initialized as Complant client.")
		return True

	async def _watch_status(self):
		from . import models
		while True:
			await sleep(15)

			if self.is_host:
				await models.plants.update_clients()
				if len(models.plants.clients) == 0:
					print("No clients connected. Scanning for another Complant host to connect to...")
					await self._init_client()
			elif self.is_client:
				if not await models.plants.host.heartbeat():
					print("Complant host unavailable, initializing this Complant as host...")
					await self._init_host()

	def reset(self):
		self._ap.active(False)
		self._sta.active(False)
