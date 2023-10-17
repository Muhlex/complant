from micropython import const
_COUNT = const(-1)
_OFFSET = const(-2)

class Character:
	TOPIC_GENERAL = 0
	TOPIC_HUMAN = 1
	TOPIC_COUNT = 2

	MOISTURE_DRY = 0
	MOISTURE_WET = 1

	TRAIT_KIND = 0
	TRAIT_RUDE = 1

	def __init__(self, name: str, trait: int, samples: dict):
		self.name = name
		self.trait = trait
		self.samples = samples

	def get_sample(self, topic: int, *sample: int) -> tuple[int, int]:
		result = self.samples[topic]
		for arg in sample:
			result = result[arg]
		return (result[_COUNT], result[_OFFSET])

	async def talk(self, topic: int, *sample: int):
		from . import models
		models.lights.reset_timeout()
		models.lights.talk()
		await models.audio.talk(topic, *sample)
		models.lights.idle()

class Characters:
	def __init__(self):
		C = Character
		self.characters = [
			Character("Donald Trump", trait=C.TRAIT_RUDE, samples={
				C.TOPIC_GENERAL: {
					C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 0,
						C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 20,
							C.TRAIT_KIND: { _COUNT: 1, _OFFSET: 60 },
							C.TRAIT_RUDE: { _COUNT: 1, _OFFSET: 80 }
						},
						C.MOISTURE_WET: { _COUNT: 3, _OFFSET: 40,
							C.TRAIT_KIND: { _COUNT: 1, _OFFSET: 100 },
							C.TRAIT_RUDE: { _COUNT: 1, _OFFSET: 120 }
						}
					}
				},
				C.TOPIC_HUMAN: {
					C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 0,
						C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 20,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 60 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 80 }
						},
						C.MOISTURE_WET: { _COUNT: 3, _OFFSET: 40,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 100 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 120 }
						}
					}
				}
			}),
			Character("TikTok Announcer", trait=C.TRAIT_RUDE, samples={
				C.TOPIC_GENERAL: {
					C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 0,
						C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 20,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 60 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 80 }
						},
						C.MOISTURE_WET: { _COUNT: 3, _OFFSET: 40,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 100 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 120 }
						}
					}
				},
				C.TOPIC_HUMAN: {
					C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 0,
						C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 20,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 60 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 80 }
						},
						C.MOISTURE_WET: { _COUNT: 3, _OFFSET: 40,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 100 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 120 }
						}
					}
				}
			}),
			Character("Snoop Dogg", trait=C.TRAIT_RUDE, samples={
				C.TOPIC_GENERAL: {
					C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 0,
						C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 20,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 60 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 80 }
						},
						C.MOISTURE_WET: { _COUNT: 3, _OFFSET: 40,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 100 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 120 }
						}
					}
				},
				C.TOPIC_HUMAN: {
					C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 0,
						C.MOISTURE_DRY: { _COUNT: 3, _OFFSET: 20,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 60 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 80 }
						},
						C.MOISTURE_WET: { _COUNT: 3, _OFFSET: 40,
							C.TRAIT_KIND: { _COUNT: 3, _OFFSET: 100 },
							C.TRAIT_RUDE: { _COUNT: 3, _OFFSET: 120 }
						}
					}
				}
			})
		]

	def __getitem__(self, key):
		return self.characters[key]

	@property
	def active(self) -> Character:
		from . import models
		return self.characters[models.config["character"]]
