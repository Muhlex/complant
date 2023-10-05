from micropython import const
from uasyncio import create_task, sleep, sleep_ms
from network import WLAN, STA_IF, AP_IF, AUTH_WPA_WPA2_PSK, hostname

HOST_IP = const("192.168.6.1")

class WiFi():
	def __init__(self):
		hostname("complant")
		self._sta = WLAN(STA_IF)
		self._ap = WLAN(AP_IF)

	@property
	def is_host(self) -> bool:
		return self._ap.active()

	@property
	def is_client(self) -> bool:
		return self._sta.active()

	async def init(self):
		if not await self._init_client():
			await self._init_host()

		create_task(self._watch_status())

	async def _init_client(self):
		from . import models
		sta = self._sta
		wifi = models.config.values["wifi"]

		print("Scanning for Complant host network...")
		sta.active(True)
		networks = sta.scan() # TODO: make this non-blocking
		print(networks)
		if not any(network[0].decode("UTF-8") == wifi["ssid"] for network in networks):
			sta.active(False)
			print("No Complant host found.")
			return False

		print("Other Complant found, connecting to their network...")
		sta.connect(wifi["ssid"], wifi["key"])
		timeout = 5000
		while sta.isconnected() == False:
			await sleep_ms(50)
			timeout -= 50
			if (timeout <= 0):
				print("Connection to host failed.")
				return False
		print("Connected.")

		models.webserver.init(sta.ifconfig()[0])

		if self.is_host:
			models.plants.clear_clients()
			self._ap.active(False)
			print("Terminated host access point.")

		print("Registering as client...")
		host = models.plants.set_host(HOST_IP)
		await host.api.put("/register", {})

		print("Registered ourselves with host.")
		return True

	async def _init_host(self):
		from . import models
		ap = self._ap

		if self.is_client:
			models.plants.clear_host()
			self._sta.active(False)
			print("Disabled WiFi station.")

		ap.active(True)
		ap.config(ssid="Complant", security=AUTH_WPA_WPA2_PSK, key=models.config.values["wifi"]["key"])
		ap.ifconfig((HOST_IP, "255.255.255.0", HOST_IP, "1.1.1.1"))

		models.webserver.init(HOST_IP)

		while ap.active() == False:
			await sleep_ms(50)

		print("Initialized host access point.")
		return True

	async def _watch_status(self):
		from . import models
		while True:
			await sleep(15)
			print("Checking WiFi status...")

			if self.is_host:
				print("Checking for client heartbeats...")
				await models.plants.check_client_heartbeats()
				if len(models.plants.clients) == 0:
					print("No client connections, testing if there is another Complant host to connect to...")
					await self._init_client()
			elif self.is_client:
				if self._sta.isconnected(): # TODO: simply use a heartbeat api call for both sides
					print("Connected to host, remaining their client.")
					continue
				else:
					print("Previous host unavailable, initializing as host...")
					await self._init_host()

	def reset(self):
		self._ap.active(False)
		self._sta.active(False)
