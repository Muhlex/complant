from microdot_asyncio import Microdot, Request, HTTPException

from ..plant import ClientPlant

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

		@root.post("/config")
		async def _(request: Request):
			from .. import models
			new_config = request.json

			if (new_config["brightness"] != models.config["brightness"]
			or new_config["periods"]["light"] != models.config["periods"]["light"]):
				models.lights.reset_timeout()

			if new_config["periods"]["conversation"] != models.config["periods"]["conversation"]:
				models.conversation.reset_timeout()

			if new_config["volume"] != models.config["volume"]:
				await models.audio.set_volume(new_config["volume"])

			models.config.values = new_config
			models.config.save()

		@root.get("/state")
		async def _(_):
			from .. import models
			return { "moisture": models.moisture.value }

		@root.get("/characters")
		async def _(_):
			from .. import models
			return { "value": [{ "name": c.name, "trait": c.trait } for c in models.characters] }

		@root.get("/dry")
		async def _(_):
			from .. import models
			return { "value": models.moisture.dry }

		@root.get("/trait")
		async def _(_):
			from .. import models
			return { "value": models.characters.active.trait }

		@root.post("/talk")
		async def _(request: Request):
			from .. import models
			await models.characters.active.talk(request.json["topic"], *request.json["sample"])

		@host.before_request
		async def verify_is_host(request: Request):
			if not request.path.startswith("/api/host/"):
				return
			from .. import models
			if not models.wifi.is_host:
				return { "error": "Not configured as a Complant host." }, 400

		@client.before_request
		async def verify_is_client(request: Request):
			if not request.path.startswith("/api/client/"):
				return
			from .. import models
			if not models.wifi.is_client:
				return { "error": "Not configured as a Complant client." }, 400

		def verify_is_known_client(request: Request):
			from .. import models
			if not request.client_addr[0] in models.plants.clients_by_ip:
				raise HTTPException(401, { "error": "Unrecognized Complant client." })

		@host.get("/heartbeat")
		async def _(request: Request):
			verify_is_known_client(request)
			pass

		@client.get("/heartbeat")
		async def _(_):
			pass

		@host.get("/clients")
		async def _(_):
			from .. import models
			return { "value": list(models.plants.clients_by_ip.keys()) }

		@host.put("/register")
		async def _(request: Request):
			from .. import models
			ip = request.client_addr[0]
			if ip in models.plants.clients_by_ip:
				print("Ignoring registration of already registered Complant client.")
			else:
				models.plants.register_client(ClientPlant(ip=ip))
				print("Client", ip, "registered.")

		@host.post("/motion")
		async def _(_):
			from .. import models
			models.conversation.trigger()


		root.mount(host, "/host")
		root.mount(client, "/client")
		self.app = root
