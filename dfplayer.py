try:
	from typing import Literal, overload
except ImportError:
	pass

from machine import UART

class DFPlayerError(Exception):
	pass
class DFPlayerUnavailableError(DFPlayerError):
	pass
class DFPlayerRequestRetransmitError(DFPlayerError):
	pass
class DFPlayerUnexpectedResponseError(DFPlayerError):
	pass

class DFPlayer:
	debug = True

	_START_BIT = 0x7E
	_END_BIT   = 0xEF
	_VERSION   = 0xFF
	_CMD_RETRIES = 4

	EQ_NORMAL  = 0
	EQ_POP     = 1
	EQ_ROCK    = 2
	EQ_JAZZ    = 3
	EQ_CLASSIC = 4
	EQ_BASS    = 5

	def __init__(self, uart_id: int, tx: int | None = None, rx: int | None = None):
		self.uart = UART(uart_id)
		self.uart.init(
			baudrate=9600, bits=8, parity=None, stop=1, timeout=100,
			tx=tx or -1, rx=rx or -1
		)
		self.buffer_send = bytearray([
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
		self.buffer_read = bytearray(10)

	def send_cmd(self, cmd: int, param1 = 0, param2: int | None = None):
		if param2 == None:
			param1, param2 = self._uint16_to_bytes(param1)

		bytes = self.buffer_send
		bytes[3] = cmd
		bytes[5] = param1
		bytes[6] = param2
		bytes[7], bytes[8] = self._uint16_to_bytes(self._checksum(bytes))

		exception: DFPlayerError | None = None
		for _ in range(DFPlayer._CMD_RETRIES):
			if DFPlayer.debug: print("<-- Sending CMD", hex(cmd))

			self.uart.write(bytes)
			self.uart.flush()
			try:
				self._read() # try to read the ACK response
			except DFPlayerError as e:
				exception = e
				if DFPlayer.debug:
					print(e)
					print("Retrying command...")
				continue

			command = self.buffer_read[3]
			if command != 0x41: # ACK
				raise DFPlayerUnexpectedResponseError("ACK expected, instead received: " + hex(command))
			if DFPlayer.debug: print("--> ACKed CMD", hex(cmd))
			return

		raise exception

	def send_query(self, cmd: int, param1 = 0, param2: int | None = None):
		self.send_cmd(cmd, param1, param2)
		self._read()
		bytes = self.buffer_read
		command = bytes[3]
		if command != cmd:
			raise DFPlayerUnexpectedResponseError("Query for " + hex(cmd) + " returned command " + hex(command))
		return bytes

	def _read(self):
		bytes = self.buffer_read
		# Invalidate old readings:
		bytes[0] = 0
		bytes[1] = 0
		bytes[9] = 0
		readinto = self.uart.readinto(bytes)
		if readinto is None:
			raise DFPlayerUnavailableError("Response timed out")
		if bytes[0] != DFPlayer._START_BIT or bytes[1] != DFPlayer._VERSION or bytes[9] != DFPlayer._END_BIT:
			raise DFPlayerUnavailableError("Malformed response");
		if (bytes[7], bytes[8]) != self._uint16_to_bytes(self._checksum(bytes)):
			raise DFPlayerUnavailableError("Malformed response: Invalid checksum");
		if bytes[3] == 0x40: # error response
			if bytes[6] == 0:
				raise DFPlayerRequestRetransmitError("Was busy")
			elif bytes[6] == 1:
				raise DFPlayerRequestRetransmitError("Frame data not fully received")
			elif bytes[6] == 2:
				raise DFPlayerRequestRetransmitError("Verification error")
			else:
				raise DFPlayerRequestRetransmitError()

	def _checksum(self, bytes: bytearray):
		result = 0
		for i in range(1, 7):
			result += bytes[i]
		return -result

	def _uint16_to_bytes(self, value: int):
		return (value >> 8 & 0xFF), (value & 0xFF)

	def play(self, file: int, folder: int | Literal["mp3"] | None = None):
		if folder is None:
			self.send_cmd(0x03, file) # play from root
		elif folder == "mp3":
			self.send_cmd(0x12, file) # play from "MP3" folder
		else:
			self.send_cmd(0x0F, folder, file) # play from numbered folder

	def resume(self):
		self.send_cmd(0x0D)

	def pause(self):
		self.send_cmd(0x0E)

	def stop(self):
		self.send_cmd(0x16)

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
		def send_query(self, cmd: int) -> bytearray: ...
		@overload
		def send_query(self, cmd: int, param1: int) -> bytearray: ...
		@overload
		def send_query(self, cmd: int, param1: int, param2: int) -> bytearray: ...

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
