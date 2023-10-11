from urequests_asyncio import get, head, post, put, delete

from microdot import HTTPException

class Plant():
	def __init__(self, ip: str):
		self.ip = ip
		self.api = API(self)

	async def heartbeat(self):
		try:
			await self.api.get(self.endpoint + "/heartbeat")
			return True
		except:
			return False

	async def get_dry(self) -> bool:
		return (await self.api.get("/dry"))["value"]

	async def get_trait(self) -> int:
		return (await self.api.get("/trait"))["value"]

	async def talk(self, topic: int, *sample: int):
		await self.api.post("/talk", { "topic": topic, "sample": sample }, timeout=20)

class API:
	def __init__(self, plant: Plant):
		self._plant = plant

	async def _request(self, method_handler, endpoint, **kwargs) -> dict:
		url = "http://" + self._plant.ip + "/api/" + endpoint.strip("/")
		response = await method_handler(url, **kwargs)
		json = {} if response.status_code == 204 else response.json()
		if response.status_code < 200 or response.status_code > 299:
			raise HTTPException(response.status_code, json["error"])
		return json

	def get(self, endpoint: str, timeout = 5):
		return self._request(get, endpoint, timeout=timeout)

	def head(self, endpoint: str, timeout = 5):
		return self._request(head, endpoint, timeout=timeout)

	def post(self, endpoint: str, json: dict | None = None, timeout = 5):
		return self._request(post, endpoint, json=json, timeout=timeout)

	def put(self, endpoint: str, json: dict | None = None, timeout = 5):
		return self._request(put, endpoint, json=json, timeout=timeout)

	def delete(self, endpoint: str, json: dict | None = None, timeout = 5):
		return self._request(delete, endpoint, json=json, timeout=timeout)


class HostPlant(Plant):
	def __init__(self, ip: str):
		super().__init__(ip)
		self.endpoint = "/host"

	async def get_dry(self):
		from . import models
		if models.wifi.is_host:
			return models.moisture.dry
		else:
			return await Plant.get_dry(self)

	async def get_trait(self):
		from . import models
		if models.wifi.is_host:
			return models.characters.active.trait
		else:
			return await Plant.get_trait(self)

	async def talk(self, topic: int, *sample: int):
		from . import models
		if models.wifi.is_host:
			return await models.characters.active.talk(topic, *sample)
		else:
			return await Plant.talk(self, topic, *sample)

class ClientPlant(Plant):
	def __init__(self, ip: str):
		super().__init__(ip)
		self.endpoint = "/client"
