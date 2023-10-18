import { Store } from "./Store";
import { Plant } from "./Plant";

import { request, HOST_IP } from "../api";

export const enum PlantsLoadState {
	Loading,
	Error,
	Ready,
}

export class Plants extends Store {
	state: PlantsLoadState;
	private plants: Map<string, Plant>;
	private refreshIntervalID: number;

	constructor() {
		super();
		this.state = PlantsLoadState.Loading;
		this.plants = new Map();
		this.fetchClients();
		this.refreshIntervalID = setInterval(this.fetchClients.bind(this), 1000 * 8);
	}

	release() {
		for (const plant of this.plants.values()) {
			plant.release();
		}
		clearInterval(this.refreshIntervalID);
	}

	[Symbol.iterator]() {
		return this.plants.values();
	}

	get size() {
		return this.plants.size;
	}

	updateConfig(...args: Parameters<Plant["updateConfig"]>) {
		for (const plant of this.plants.values()) {
			plant.updateConfig(...args);
		}
	}

	private async fetchClients() {
		try {
			const clientIPs = (await request("host/clients"))["value"] as string[];
			const newIPs = new Set([HOST_IP, ...clientIPs]);
			for (const knownIP of this.plants.keys()) {
				if (newIPs.has(knownIP)) continue;
				this.plants.get(knownIP)?.release();
				this.plants.delete(knownIP);
			}
			for (const newIP of newIPs) {
				if (this.plants.has(newIP)) continue;
				this.plants.set(newIP, new Plant(newIP));
			}
			this.state = PlantsLoadState.Ready;
		} catch (error) {
			console.error(error);
			this.state = PlantsLoadState.Error;
		} finally {
			this.notify();
		}
	}
}
