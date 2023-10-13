export type PlantConfig = {
	name: string
	volume: number
	brightness: number
	moisture: number
	character: number
	periods: {
		light: number
		conversation: number
	}
	wifi: {
		ssid: string
		key: string
	}
}

export type PlantState = {
	moisture: number
}

export enum CharacterTrait {
	Kind,
	Rude,
}

export type Character = {
	name: string
	trait: CharacterTrait
}
