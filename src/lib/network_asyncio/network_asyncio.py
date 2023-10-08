from network import WLAN
from uasyncio.event import ThreadSafeFlag
from _thread import allocate_lock, start_new_thread

class AsyncWLAN():
	"""
	Wraps a subset of WLAN features to make them awaitable by executing them on another thread.
	(Requires experimental `_thread` module!)
	"""
	def __init__(self):
		self._wlan = None
		# self._args = ()
		# self._kwargs = {}

		self._scan_start_lock = allocate_lock()
		self._scan_start_lock.acquire()
		self._scan_complete_flag = ThreadSafeFlag()
		self._scan_results = None
		start_new_thread(self._scan_thread, ())

	def _scan_thread(self):
		while True:
			self._scan_start_lock.acquire()
			self._scan_results = self._wlan.scan()
			self._scan_complete_flag.set()

	async def scan(self, wlan: WLAN):
		self._wlan = wlan
		self._scan_start_lock.release()
		await self._scan_complete_flag.wait()
		return self._scan_results
