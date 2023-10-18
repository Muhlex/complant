<script lang="ts">
	import type { Plant } from "../models/Plant";

	import { colord, type Colord } from "colord";

	import TextEditable from "./TextEditable.svelte";
	import ColorRange from "./ColorRange.svelte";
	import Period from "./Period.svelte";

	export let plant: Plant;

	const moisturePresets = [["🌵️ Dry", 0.25], ["🪴️ Regular", 0.4], ["🌷️ Wet", 0.6]] as const;
	$: dry = ($plant.state && $plant.config && $plant.state.moisture < $plant.config.moisture);

	const lights: {
		colord: Colord | null
		h: number
		s: number
	} = { colord: null, h: 96, s: 96 };
	$: if ($plant.config?.color) {
		const [r, g, b] = $plant.config.color;
		const prev = lights.colord?.rgba;
		if (!prev || r !== prev.r && g !== prev.g && b !== prev.b) {
			lights.colord = colord({ r, g, b });
			const hsv = lights.colord.toHsv();
			lights.h = hsv.h;
			lights.s = hsv.s;
		}
	} else {
		lights.colord = null;
	}
	const updateLights = (reset = false) => {
		if (reset) {
			plant.updateConfig(c => ({ ...c, color: null }));
			return;
		}
		lights.colord = colord({ h: lights.h, s: lights.s, v: 100 });
		const { r, g, b } = lights.colord.rgba;
		plant.updateConfig(c => ({ ...c, color: [r, g, b] }));
	};
</script>

<div class="plant">
	{#if !($plant.config && $plant.state)}
		<h3>Loading Plant...</h3>
	{:else}
		<h3 class="row">
			<span class="row" style:flex-grow="1">
				<span>
					{$plant.icon}
				</span>
				<span class="name">
					<TextEditable
						value={$plant.config.name}
						on:blur={({ detail: { currentTarget: { value } } }) => {
							if (!value) value = "Unnamed Complant";
							plant.updateConfig(c => ({ ...c, name: value.trim() }));
						}}
					/>
					</span>
			</span>
			<span class:dry={dry}>
				{dry ? "🩸️" : "💧️"} {($plant.state.moisture * 100).toFixed(0)} %
			</span>
		</h3>

		<div class="setting">
			<label>
				<h4>💦️ Required Moisture</h4>
				<div class="row">
					<input
						type="range"
						min="0" max="1" step="0.01"
						value={$plant.config.moisture}
						on:input={({ currentTarget: { valueAsNumber } }) => {
							plant.updateConfig(c => ({ ...c, moisture: valueAsNumber }));
						}}
					/>
					<span>
						<span style:min-width="3ch" style:text-align="right">
							{($plant.config.moisture * 100).toFixed(0)}
						</span>
						%
					</span>
				</div>
			</label>
			<div class="row" style:margin-top="0.5em" style:justify-content="center">
				{#each moisturePresets as [label, moisture]}
					<button
						disabled={$plant.config.moisture === moisture}
						on:click={() => $plant.updateConfig(c => ({ ...c, moisture: moisture }))}
					>
						{label}
					</button>
				{/each}
			</div>
		</div>

		<div class="setting">
			<label>
				<h4>👄️ Voice Character</h4>
				<select
					value={$plant.config.character}
					on:change={({ currentTarget: { value } }) => {
						$plant.updateConfig(c => ({ ...c, character: Number(value) }));
					}}
				>
					{#each $plant.characters as character, i}
						<option value={i}>{character.name}</option>
					{/each}
				</select>
			</label>
		</div>

		<div class="setting">
			<label>
				<h4>🔊️ Volume</h4>
				<div class="row">
					<input
						type="range"
						min="0" max="30" step="1"
						value={$plant.config.volume}
						on:input={({ currentTarget: { valueAsNumber } }) => {
							plant.updateConfig(c => ({ ...c, volume: valueAsNumber }));
						}}
					/>
					<span>
						<span style:min-width="2ch" style:text-align="right">
							{$plant.config.volume}
						</span>
						/ 30
					</span>
				</div>
			</label>
		</div>

		<div class="setting">
			<label>
				<h4>🔆️ Brightness</h4>
				<div class="row">
					<input
						type="range"
						min="0" max="1" step="0.10"
						value={$plant.config.brightness}
						on:input={({ currentTarget: { valueAsNumber } }) => {
							plant.updateConfig(c => ({ ...c, brightness: valueAsNumber }));
						}}
					/>
					<span>
						<span style:min-width="3ch" style:text-align="right">
							{($plant.config.brightness * 100).toFixed(0)}
						</span>
						%
					</span>
				</div>
			</label>
		</div>

		<div class="setting">
			<label>
				<h4>🌆️ Standby Light after</h4>
				<div class="row">
					<input
						type="range"
						min="0" max={60 * 60} step="15"
						value={$plant.config.periods.light}
						on:input={({ currentTarget: { valueAsNumber } }) => {
							if (valueAsNumber === 0) valueAsNumber = 10;
							plant.updateConfig(c => ({ ...c, periods: { ...c.periods, light: valueAsNumber } }));
						}}
					/>
					<span>
						<Period seconds={$plant.config.periods.light} />
					</span>
				</div>
			</label>
		</div>

		<div class="setting">
			<label>
				<h4>
					🎨️ Override Light Color
					<input
						type="checkbox"
						checked={Boolean(lights.colord)}
						on:change={({ currentTarget: { checked } }) => updateLights(!checked)}
					/>
				</h4>
			</label>
			<div class="column">
				{#if lights.colord}
					<ColorRange
						type="hue"
						bind:value={lights.h}
						on:input={() => updateLights()}
					/>
					<ColorRange
						type="saturation"
						bind:value={lights.s}
						hue={lights.h}
						on:input={() => updateLights()}
					/>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.plant {
		display: flex;
		flex-direction: column;
		gap: 2em;
	}

	.name {
		flex-grow: 1;
		display: flex;
	}
	.name :global(input) {
		width: 0;
		flex-grow: 1;
	}

	.dry {
		color: #ff7e8a;
	}

	.row {
		display: flex;
		align-items: center;
		gap: 0.5em;
	}

	.plant :global(input) {
		min-width: 0;
		flex-grow: 1;
	}

	button, select {
		padding: 0.25em 0.5em;
	}

	label, .column {
		display: flex;
		flex-direction: column;
		gap: 0.5em;
	}
	.column {
		margin-top: 0.5em;
	}
	label span {
		display: inline-block;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
</style>
