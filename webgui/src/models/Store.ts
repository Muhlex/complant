import { writable, type Updater, type Subscriber } from "svelte/store";

export class Store {
	private store = writable(this);

	subscribe(run: Subscriber<this>, invalidate?: () => void) {
		return this.store.subscribe(run, invalidate);
	}
	set(value: this) {
		return this.store.set(value);
	}
	update(updater: Updater<this>) {
		return this.store.update(updater);
	}

	// Notify the Svelte store that data has been changed.
	// Needs to be called every time (public) fields are changed.
	notify() {
		this.store.set(this);
	}
}
