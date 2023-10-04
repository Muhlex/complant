from microdot_asyncio import Microdot, Response, HTTPException, send_file
from microdot_cors import CORS

from .api import API

Response.types_map["svg"] = "image/svg+xml"

class Webserver:
	def __init__(self, api: API, root=""):
		app = Microdot()
		self.app = app

		app.mount(api.app, url_prefix="/api")

		@app.route("/")
		async def _(_):
			return send_file(root + "index.html")

		@app.route("/<path:path>")
		async def _(_, path):
			if ".." in path:
				raise HTTPException(404)
			return send_file(root + path)

		CORS(app, allowed_origins="*", allow_credentials=True)

	def init(self, debug=False):
		return self.app.start_server(port=80, debug=debug)
