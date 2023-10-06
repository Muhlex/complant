from microdot_asyncio import Microdot, Request, HTTPException

from ..plant import Plant

class API:
	def __init__(self):
		root = Microdot()
		host = Microdot()
		client = Microdot()

		@root.route("/")
		async def _(_):
			return "<html><body><h1>Complant REST API</h1></body></html>", { "Content-Type": "text/html" }

		@root.get("/config")
		async def _(_):
			from .. import models
			return models.config.values

		@root.get("/volume")
		async def _(_):
			from .. import models
			return { "value": models.config.values["volume"] }

		@root.post("/volume")
		async def _(request: Request):
			from .. import models
			try:
				volume = request.json["value"]
				await models.audio.volume(volume)
				models.config.values["volume"] = volume
				models.config.save()
				return { "success": True }
			except Exception as error:
				return { "success": False, "error": str(error) }, 500

		@host.before_request
		async def verify_is_host(request: Request):
			if not request.path.startswith("/api/host/"):
				return
			from .. import models
			if not models.wifi.is_host:
				return { "success": False, "error": "Not configured as a Complant host." }, 400

		@client.before_request
		async def verify_is_client(request: Request):
			if not request.path.startswith("/api/client/"):
				return
			from .. import models
			if not models.wifi.is_client:
				return { "success": False, "error": "Not configured as a Complant client." }, 400

		def verify_is_known_client(request: Request):
			from .. import models
			if not request.client_addr[0] in models.plants.clients_by_ip:
				raise HTTPException(401, { "success": False, "error": "Unrecognized Complant client." })

		@host.get("/heartbeat")
		async def _(request: Request):
			verify_is_known_client(request)
			return { "success": True }

		@client.get("/heartbeat")
		async def _(_):
			return { "success": True }

		@host.put("/register")
		async def _(request: Request):
			from .. import models
			ip = request.client_addr[0]
			if ip in models.plants.clients_by_ip:
				print("Ignoring registration of already registered Complant client.")
			else:
				models.plants.register_client(Plant(ip=ip))
				print("Client {} registered.".format(ip))
			return { "success": True }

		root.mount(host, "/host")
		root.mount(client, "/client")
		self.app = root
