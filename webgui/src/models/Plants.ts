import { Store } from "./Store";
import { Plant } from "./Plant";

import { request, HOST_IP } from "../api";

export class Plants extends Store {
	private plants: Map<string, Plant>;
	private refreshIntervalID: number;

	constructor() {
		super();
		this.plants = new Map();
		this.fetchClients();
		this.refreshIntervalID = setInterval(() => this.fetchClients(), 1000 * 8);
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

	private async fetchClients() {
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
		this.notify();
	}
}
