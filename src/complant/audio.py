from random import randint
from dfplayer import DFPlayer

from .characters import Character

class Audio:
	def __init__(self, dfplayer: DFPlayer):
		self._df = dfplayer

	async def init(self):
		from . import models
		await self._df.volume(models.config["volume"])

	async def startup(self):
		await self._df.play_advert(0)
		await self._df.wait_advert()

	async def set_volume(self, volume: int):
		from . import models
		await self._df.volume(volume)
		models.config["volume"] = volume
		models.config.save()

	async def talk(self, topic: int, *sample: int):
		from . import models
		char_index: int = models.config["character"]
		char: Character = models.characters[char_index]

		folder_index = char_index * Character.TOPIC_COUNT + topic
		sample_count, sample_offset = char.get_sample(topic, *sample)
		file_index = sample_offset + randint(0, sample_count - 1)
		print("Talking as {} (Folder: {}, File: {}).".format(char.name, folder_index, file_index))
		await self._df.play(folder_index, file_index)
		await self._df.wait_track()
		print("Done talking.")
