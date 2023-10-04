from microdot_asyncio import Microdot
from dfplayer import DFPlayer

from .config import Config

class API:
	def __init__(self, config: Config, audio: DFPlayer):
		app = Microdot()
		self.app = app

		@app.route("/")
		async def _(_):
			return "<html><body><h1>Complant REST API</h1></body></html>", {"Content-Type": "text/html"}

		@app.get("/config")
		async def _(_):
			return config.values

		@app.get("/volume")
		async def _(_):
			return { "value": config.values["volume"] }

		@app.post("/volume")
		async def _(request):
			try:
				volume = request.json["value"]
				await audio.volume(volume)
				config.values["volume"] = volume
				config.save()
				return {}
			except Exception as error:
				return { "error": str(error) }, 500
