from tinyweb import Webserver
from dfplayer import DFPlayer

from .config import Config

class API:
	def __init__(self, config: Config, audio: DFPlayer):
		api = Webserver(debug=True)
		self._api = api

		# tinyweb has been extended to support `_async` suffixed resource methods, as it otherwise
		# doesn't support async resource handlers (treats them as regular generators)

		@api.route("/")
		async def _(request, response):
			await response.start_html()
			await response.send("<html><body><h1>Complant REST API</h1></body></html>\n")

		class RouteConfig:
			def get(self, data):
				return config.values

		class RouteVolume:
			def get(self, data):
				return { "value": config.values["volume"] }
			async def post_async(self, data):
				try:
					volume = data["value"]
					await audio.volume(volume)
					config.values["volume"] = volume
					config.save()
					return { "success": True }
				except Exception as error:
					return { "success": False, "error": str(error) }, 500

		api.add_resource(RouteConfig, "/config")
		api.add_resource(RouteVolume, "/volume")

	def init(self, host="0.0.0.0", port=80):
		self._api.run(host=host, port=port, loop_forever=False)
