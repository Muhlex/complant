from uasyncio.funcs import gather

from .plant import Plant

class Plants:
	def __init__(self):
		self.host: Plant | None = None
		self.clients: list[Plant] = []

	def set_host(self, ip: str):
		self.host = Plant(ip=ip)
		return self.host

	def clear_host(self):
		self.host = None
		return self.host

	def register_client(self, ip: str):
		self.clients.append(Plant(ip=ip))

	def clear_clients(self):
		self.clients.clear()

	async def check_client_heartbeats(self):
		if len(self.clients) == 0:
			return
		clients_alive: list[bool] = await gather(*map(lambda client: client.heartbeat(), self.clients))
		for i, alive in enumerate(clients_alive):
			if not alive:
				print("Client {} died, removing them.".format(self.clients[i].ip))
				del self.clients[i]
