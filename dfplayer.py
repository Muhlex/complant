try:
	from typing import Literal, overload
except ImportError:
	pass

from machine import UART
from time import sleep_ms

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
	_CMD_TRIES = 6

	STATE_STOPPED = 0
	STATE_PLAYING = 1
	STATE_PAUSED  = 2

	EQ_NORMAL  = 0
	EQ_POP     = 1
	EQ_ROCK    = 2
	EQ_JAZZ    = 3
	EQ_CLASSIC = 4
	EQ_BASS    = 5

	def __init__(self, uart_id: int, tx: int | None = None, rx: int | None = None):
		self._uart = UART(uart_id)
		self._uart.init(
			baudrate=9600, bits=8, parity=None, stop=1, timeout=100,
			tx=tx or -1, rx=rx or -1
		)
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

	def _log(self, *args):
		print("[DF]", *args)

	def send_cmd(self, cmd: int, param1 = 0, param2: int | None = None, read_delay = 0):
		if param2 == None:
			param1, param2 = self._uint16_to_bytes(param1)

		bytes = self._buffer_send
		bytes[3] = cmd
		bytes[5] = param1
		bytes[6] = param2
		bytes[7], bytes[8] = self._uint16_to_bytes(self._checksum(bytes))

		exception: DFPlayerError | None = None
		for i in reversed(range(DFPlayer._CMD_TRIES)):
			if DFPlayer.debug: self._log("<-- Sending CMD", hex(cmd))

			self._uart.write(bytes)
			self._uart.flush()
			sleep_ms(read_delay)
			try:
				self._read() # try to read the ACK response
			except DFPlayerError as e:
				exception = e
				if DFPlayer.debug and i > 0:
					self._log(e)
					self._log("Retrying command...")
				continue

			command = self._buffer_read[3]
			if command != 0x41: # ACK
				raise DFPlayerUnexpectedResponseError("ACK expected, instead received: " + hex(command))
			if DFPlayer.debug: self._log("--> ACKed CMD", hex(cmd))
			return

		raise exception

	def send_query(self, cmd: int, param1 = 0, param2: int | None = None, read_delay = 0):
		self.send_cmd(cmd, param1, param2, read_delay)
		self._read()
		bytes = self._buffer_read
		command = bytes[3]
		if command != cmd:
			raise DFPlayerUnexpectedResponseError("Query for " + hex(cmd) + " returned command " + hex(command))
		return bytes

	def _read(self):
		bytes = self._buffer_read
		# Invalidate old readings:
		bytes[0] = 0
		bytes[1] = 0
		bytes[9] = 0
		readinto = self._uart.readinto(bytes)
		if readinto is None:
			raise DFPlayerUnavailableError("Response timed out")
		if bytes[0] != DFPlayer._START_BIT or bytes[1] != DFPlayer._VERSION or bytes[9] != DFPlayer._END_BIT:
			raise DFPlayerUnavailableError("Malformed response");
		if (bytes[7], bytes[8]) != self._uint16_to_bytes(self._checksum(bytes)):
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
			if DFPlayer.debug: self._log("Received event notification (" + hex(bytes[3]) + "), re-reading...")
			self._read()


	def _checksum(self, bytes: bytearray):
		result = 0
		for i in range(1, 7):
			result += bytes[i]
		return -result

	def _uint16_to_bytes(self, value: int):
		return (value >> 8 & 0xFF), (value & 0xFF)

	def play_root(self, file: int):
		self.send_cmd(0x03, file)

	def play(self, folder: int | Literal["mp3"] | Literal["advert"], file: int):
		if folder == "mp3":
			self.send_cmd(0x12, file) # play from "MP3" folder
		elif folder == "advert":
			self.send_cmd(0x13, file) # play from "ADVERT" folder
		else:
			self.send_cmd(0x0F, folder, file) # play from numbered folder

	def resume(self):
		# DFPlayer seems to take long to process resuming
		self.send_cmd(0x0D, read_delay=50)

	def pause(self):
		self.send_cmd(0x0E)

	def stop(self):
		self.send_cmd(0x16)

	def stop_advert(self):
		self.send_cmd(0x15)

	def next(self):
		self.send_cmd(0x01)

	def previous(self):
		self.send_cmd(0x02)

	def state(self):
		bytes = self.send_query(0x42)
		return bytes[6]

	def volume(self, volume: int | None = None):
		if volume is None:
			bytes = self.send_query(0x43)
			return bytes[6]
		else:
			self.send_cmd(0x06, volume)

	def eq(self, eq: int | None = None):
		if eq is None:
			bytes = self.send_query(0x44)
			return bytes[6]
		else:
			self.send_cmd(0x07, eq)

	def sleep(self):
		self.send_cmd(0x0A)

	def wake(self):
		self.send_cmd(0x0B)

	def reset(self):
		self.send_cmd(0x0C)

	try:
		@overload
		def send_cmd(self, cmd: int) -> None: ...
		@overload
		def send_cmd(self, cmd: int, param1: int) -> None: ...
		@overload
		def send_cmd(self, cmd: int, param1: int, param2: int) -> None: ...
		@overload
		def send_cmd(self, cmd: int, param1: int, param2: int, read_delay: int) -> None: ...

		@overload
		def send_query(self, cmd: int) -> bytearray: ...
		@overload
		def send_query(self, cmd: int, param1: int) -> bytearray: ...
		@overload
		def send_query(self, cmd: int, param1: int, param2: int) -> bytearray: ...
		@overload
		def send_query(self, cmd: int, param1: int, param2: int, read_delay: int) -> bytearray: ...

		@overload
		def volume(self) -> int: ...
		@overload
		def volume(self, volume: int) -> None: ...

		@overload
		def eq(self) -> int: ...
		@overload
		def eq(self, eq: int) -> None: ...
	except NameError:
		pass
