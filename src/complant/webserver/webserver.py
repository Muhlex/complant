from uasyncio import create_task, Task
from microdot_asyncio import Microdot, Response, HTTPException, send_file
from microdot_cors import CORS

from .api import API

Response.types_map["svg"] = "image/svg+xml"

class Webserver:
	def __init__(self, api: API, root=""):
		app = Microdot()
		self._app = app
		self._task: Task | None = None

		app.mount(api.app, "/api")

		@app.route("/")
		async def _(_):
			return send_file(root + "index.html")

		@app.route("/<path:path>")
		async def _(_, path: str):
			if ".." in path:
				raise HTTPException(404)
			try:
				return send_file(root + path)
			except:
				raise HTTPException(404)

		@app.errorhandler(400)
		def _(_):
			return {"error": "Bad request"}, 400

		@app.errorhandler(404)
		def _(_):
			return {"error": "Not found"}, 404

		@app.errorhandler(405)
		def _(_):
			return {"error": "Method not allowed"}, 405

		@app.errorhandler(413)
		def _(_):
			return {"error": "Payload too large"}, 413

		@app.errorhandler(500)
		def _(_):
			return {"error": "Internal server error"}, 500

		@app.errorhandler(Exception)
		def _(_, error: Exception):
			return {"error": "{}: {}".format(type(error).__name__, str(error))}, 500

		CORS(app, allowed_origins="*", allow_credentials=True)

	def init(self, host: str):
		if self._task is not None:
			self._app.shutdown() # also ends the task
		self._task = create_task(self._app.start_server(host=host, port=80, debug=True))
