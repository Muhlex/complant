try: from typing import Literal
except ImportError: pass

from urequests_asyncio import get, head, post, put, delete
from microdot import HTTPException

class Plant:
	def __init__(self, ip: str):
		self.ip = ip
		self.api = API(self)
		self.type: Literal["host", "client"] = "host"

	async def heartbeat(self):
		try:
			await self.api.get(self.type + "/heartbeat")
			return True
		except:
			return False

class API:
	def __init__(self, plant: Plant):
		self._plant = plant

	async def _request(self, method_handler, endpoint, **kwargs) -> dict:
		url = "http://" + self._plant.ip + "/api/" + endpoint.strip("/")
		response = await method_handler(url, timeout=5, **kwargs)
		json = response.json()
		if response.status_code < 200 or response.status_code > 299:
			raise HTTPException(response.status_code, json["error"])
		return json

	def get(self, endpoint: str):
		return self._request(get, endpoint)
	def head(self, endpoint: str):
		return self._request(head, endpoint)
	def post(self, endpoint: str, json: dict):
		return self._request(post, endpoint, json=json)
	def put(self, endpoint: str, json: dict):
		return self._request(put, endpoint, json=json)
	def delete(self, endpoint: str, json: dict | None = None):
		return self._request(delete, endpoint, json=json)
