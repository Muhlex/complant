import type { PlantConfig, PlantState, Character } from "../types";

import { Store } from "./Store";

import { debounce, shuffle } from "../util";
import { request } from "../api";

const getIcon = (() => {
	const ICONS = shuffle(["🪴️", "🌱️", "🌿️", "🎍️"]);
	let nextID = 0;

	return () => ICONS[nextID++ % ICONS.length];
})();

export class Plant extends Store {
	ip: string;
	icon: string;
	config: PlantConfig | null;
	private configDirty: boolean;
	state: PlantState | null;
	characters: Character[];
	private refreshIntervalID: number;

	constructor(ip: string) {
		super();
		this.ip = ip;
		this.icon = getIcon();
		this.config = null;
		this.configDirty = false;
		this.state = null;
		this.characters = [];
		this.fetchCharacters();

		const refresh = () => {
			this.fetchConfig();
			this.fetchState();
		};
		this.refreshIntervalID = setInterval(refresh, 1000 * 12);
		refresh();
	}

	release() {
		clearInterval(this.refreshIntervalID);
	}

	private updateConfigRemote = debounce(async (config: PlantConfig) => {
		await request("config", { host: this.ip, method: "POST", json: config });
		this.configDirty = false;
	}, 1000);

	updateConfig(updater: (value: PlantConfig) => PlantConfig) {
		if (!this.config) throw new Error("No plant config available to be updated.");
		this.config = updater(this.config);
		this.notify();
		this.configDirty = true;
		this.updateConfigRemote(this.config);
	}

	private async fetchConfig() {
		if (this.configDirty) return;
		const config = await request("config", { host: this.ip }) as PlantConfig;
		if (this.configDirty) return;
		this.config = config;
		this.notify();
	}

	private async fetchState() {
		this.state = await request("state", { host: this.ip }) as PlantState;
		this.notify();
	}

	private async fetchCharacters() {
		const json = await request("characters", { host: this.ip });
		this.characters = json.value as Character[];
		this.notify();
	}
}
