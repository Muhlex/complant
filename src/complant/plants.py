from uasyncio.funcs import gather

from .plant import HostPlant, ClientPlant

class Plants:
	def __init__(self):
		self.host: HostPlant | None = None
		# Important: Client list is only maintained when the plant is the host!
		self.clients: list[ClientPlant] = []
		self.clients_by_ip: dict[str, ClientPlant] = {}

	def all(self) -> list[ClientPlant | HostPlant]:
		plants = self.clients.copy()
		if self.host is not None:
			plants.append(self.host)
		return plants

	def set_host(self, plant: HostPlant):
		self.host = plant
		return self.host

	def register_client(self, plant: ClientPlant):
		self.clients.append(plant)
		self.clients_by_ip[plant.ip] = plant

	def clear_clients(self):
		self.clients.clear()
		self.clients_by_ip.clear()

	def _remove_client_by_index(self, index: int):
		client = self.clients[index]
		del self.clients[index]
		del self.clients_by_ip[client.ip]

	async def update_clients(self):
		if len(self.clients) == 0:
			return
		clients_alive: list[bool] = await gather(*tuple(client.heartbeat() for client in self.clients))
		for i, alive in enumerate(clients_alive):
			if not alive:
				print("Lost Complant client {} heartbeat, removing them.".format(self.clients[i].ip))
				self._remove_client_by_index(i)
