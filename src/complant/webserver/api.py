from microdot_asyncio import Microdot, Request

class API:
	def __init__(self):
		app = Microdot()
		self.app = app

		@app.route("/")
		async def _(_):
			return "<html><body><h1>Complant REST API</h1></body></html>", { "Content-Type": "text/html" }

		@app.get("/heartbeat")
		async def _(_):
			return {}

		@app.put("/register")
		async def _(request: Request):
			from .. import models
			if not models.wifi.is_host:
				print("Client tried to register, but we are not host.")
				return { "success": False }

			ip = request.client_addr[0]
			if any(plant.ip == ip for plant in models.plants.clients):
				print("Client tried to register, but already is known.")
				return { "success": False }
			else:
				models.plants.register_client(ip)
				print("Client registered from:", ip)
				return { "success": True }

		@app.get("/config")
		async def _(_):
			from .. import models
			return models.config.values

		@app.get("/volume")
		async def _(_):
			from .. import models
			return { "value": models.config.values["volume"] }

		@app.post("/volume")
		async def _(request: Request):
			from .. import models
			try:
				volume = request.json["value"]
				await models.audio.volume(volume)
				models.config.values["volume"] = volume
				models.config.save()
				return {}
			except Exception as error:
				return { "error": str(error) }, 500
