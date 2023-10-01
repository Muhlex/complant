try:
	from typing import Literal, overload
except ImportError:
	pass

from uasyncio import sleep_ms, TimeoutError
from uasyncio.funcs import wait_for_ms
from uasyncio.stream import Stream
from uasyncio.lock import Lock
from machine import UART

class DFPlayerError(Exception):
	pass
class DFPlayerUnavailableError(DFPlayerError):
	pass
class DFPlayerResponseError(DFPlayerError):
	pass
class DFPlayerUnexpectedResponseError(DFPlayerError):
	pass

class DFPlayer:
	debug = True

	_START_BIT = 0x7E
	_END_BIT   = 0xEF
	_VERSION   = 0xFF

	STATE_STOPPED = 0
	STATE_PLAYING = 1
	STATE_PAUSED  = 2

	EQ_NORMAL  = 0
	EQ_POP     = 1
	EQ_ROCK    = 2
	EQ_JAZZ    = 3
	EQ_CLASSIC = 4
	EQ_BASS    = 5

	def __init__(self, uart_id: int, tx = None, rx = None, retries = 9):
		kwargs = {};
		if tx is not None: kwargs["tx"] = tx
		if rx is not None: kwargs["rx"] = rx

		self._uart = UART(uart_id)
		self._uart.init(
			baudrate=9600, bits=8, parity=None, stop=1, timeout=0,
			**kwargs
		)
		self._stream = Stream(self._uart)
		self._lock = Lock()
		self.retries = retries

		self._buffer_send = bytearray([
			DFPlayer._START_BIT,
			DFPlayer._VERSION,
			6, # number of byes w/o start, end, verification
			0, # command
			1, # whether to use ACK
			0, # param1
			0, # param2
			0, # checksum
			0, # checksum
			DFPlayer._END_BIT
		])
		self._buffer_read = bytearray(10)

	def _log(self, *args, **kwargs):
		print("[DF]", *args, **kwargs)

	async def send_cmd(self, *args, **kwargs):
		try:
			await self._lock.acquire()
			result = await self._send_cmd(*args, **kwargs)
			return result
		except Exception as e:
			raise e
		finally:
			self._lock.release()
	async def _send_cmd(self, cmd: int, param1 = 0, param2: int | None = None, timeout = 100):
		if param2 == None:
			param1, param2 = self._uint16_to_bytes(param1)

		bytes = self._buffer_send
		bytes[3] = cmd
		bytes[5] = param1
		bytes[6] = param2
		bytes[7], bytes[8] = self._uint16_to_bytes(self._get_checksum(bytes))

		for retries in reversed(range(self.retries + 1)):
			if DFPlayer.debug:
				self._log("<-- Sending CMD", hex(cmd))

			while count := self._uart.any():
				self._uart.read(count)
				if DFPlayer.debug:
					self._log("Discarded", count, "bytes from RX")
				await sleep_ms(0)
			self._stream.write(bytes)
			await self._stream.drain()

			try:
				await self._read(timeout) # try to read the ACK response
			except DFPlayerError as error:
				if retries == 0:
					raise error
				if DFPlayer.debug and retries > 0:
					self._log("ERROR:", error)
					self._log("Retrying command...")
				continue

			command = self._buffer_read[3]
			if command != 0x41: # ACK
				raise DFPlayerUnexpectedResponseError("ACK expected, instead received: " + hex(command))
			if DFPlayer.debug:
				self._log("--> ACKed CMD", hex(cmd) + "\n")
			break

	async def send_query(self, *args, **kwargs):
		try:
			await self._lock.acquire()
			result = await self._send_query(*args, **kwargs)
			return result
		except Exception as e:
			raise e
		finally:
			self._lock.release()
	async def _send_query(self, cmd: int, param1 = 0, param2: int | None = None, timeout = 100):
		await self._send_cmd(cmd, param1, param2, timeout)
		await self._read()
		bytes = self._buffer_read
		command = bytes[3]
		if command != cmd:
			raise DFPlayerUnexpectedResponseError("Query for " + hex(cmd) + " returned command " + hex(command))
		return bytes

	async def _read(self, timeout = 100):
		bytes = self._buffer_read
		try:
			read_count = await wait_for_ms(self._stream.readinto(bytes), timeout)
		except TimeoutError:
			raise DFPlayerUnavailableError("Response timed out")
		if read_count != 10 or bytes[0] != DFPlayer._START_BIT or bytes[1] != DFPlayer._VERSION or bytes[9] != DFPlayer._END_BIT:
			raise DFPlayerUnavailableError("Malformed response");
		if (bytes[7], bytes[8]) != self._uint16_to_bytes(self._get_checksum(bytes)):
			raise DFPlayerUnavailableError("Malformed response: Invalid checksum");
		if bytes[3] == 0x40: # error response
			err_code = bytes[6]
			err_code_readable = "(" + hex(err_code) + ")"
			if err_code == 0x00:
				raise DFPlayerResponseError("Module is busy " + err_code_readable)
			elif err_code == 0x01:
				raise DFPlayerResponseError("Received incomplete frame " + err_code_readable)
			elif err_code == 0x02:
				raise DFPlayerResponseError("Received corrupt frame " + err_code_readable)
			else:
				raise DFPlayerResponseError("Unknown error " + err_code_readable)
		if (0xF0 & bytes[3]) == 0x30: # event notification
			# ignore them for now
			if DFPlayer.debug:
				self._log("Received event notification (" + hex(bytes[3]) + "), re-reading...")
			return await self._read()


	def _get_checksum(self, bytes: bytearray):
		result = 0
		for i in range(1, 7):
			result += bytes[i]
		return -result

	def _uint16_to_bytes(self, value: int):
		return (value >> 8 & 0xFF), (value & 0xFF)

	async def play_root(self, file: int):
		await self.send_cmd(0x03, file)

	async def play(self, folder: int | Literal["mp3"] | Literal["advert"], file: int):
		if folder == "mp3":
			await self.send_cmd(0x12, file) # play from "MP3" folder
		elif folder == "advert":
			await self.send_cmd(0x13, file) # play from "ADVERT" folder
		else:
			await self.send_cmd(0x0F, folder, file) # play from numbered folder

	async def resume(self):
		# DFPlayer seems to take long to process resuming
		await self.send_cmd(0x0D, timeout=150)

	async def pause(self):
		await self.send_cmd(0x0E)

	async def stop(self):
		await self.send_cmd(0x16)

	async def stop_advert(self):
		await self.send_cmd(0x15)

	async def next(self):
		await self.send_cmd(0x01)

	async def previous(self):
		await self.send_cmd(0x02)

	async def state(self):
		bytes = await self.send_query(0x42)
		return bytes[6]

	async def volume(self, volume: int | None = None):
		if volume is None:
			bytes = await self.send_query(0x43)
			return bytes[6]
		else:
			await self.send_cmd(0x06, volume)

	async def eq(self, eq: int | None = None):
		if eq is None:
			bytes = await self.send_query(0x44)
			return bytes[6]
		else:
			await self.send_cmd(0x07, eq)

	async def sleep(self):
		await self.send_cmd(0x0A)

	async def wake(self):
		await self.send_cmd(0x0B)

	async def reset(self):
		await self.send_cmd(0x0C, timeout=250)

	try:
		@overload
		async def send_cmd(self, cmd: int) -> None: ...
		@overload
		async def send_cmd(self, cmd: int, param1: int) -> None: ...
		@overload
		async def send_cmd(self, cmd: int, param1: int, param2: int) -> None: ...
		@overload
		async def send_cmd(self, cmd: int, param1: int, param2: int, timeout: int) -> None: ...

		@overload
		async def send_query(self, cmd: int) -> bytearray: ...
		@overload
		async def send_query(self, cmd: int, param1: int) -> bytearray: ...
		@overload
		async def send_query(self, cmd: int, param1: int, param2: int) -> bytearray: ...
		@overload
		async def send_query(self, cmd: int, param1: int, param2: int, timeout: int) -> bytearray: ...

		@overload
		async def volume(self) -> int: ...
		@overload
		async def volume(self, volume: int) -> None: ...

		@overload
		async def eq(self) -> int: ...
		@overload
		async def eq(self, eq: int) -> None: ...
	except NameError:
		pass
