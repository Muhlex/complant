<script lang="ts">
	import type { Plant } from "../models/Plant";

	import { colord } from "colord";

	import TextEditable from "./TextEditable.svelte";
	import ColorRange from "./ColorRange.svelte";
	import Period from "./Period.svelte";

	export let plant: Plant;

	const moisturePresets = [["🌵️ Dry", 0.1], ["🪴️ Regular", 0.25], ["🌷️ Wet", 0.4]] as const;
	$: dry = ($plant.state && $plant.config && $plant.state.moisture < $plant.config.moisture);

	$: lightColor = (() => {
		if (!$plant.config?.color) return null;
		const [r, g, b] = $plant.config.color;
		return colord({ r, g, b }).toHex();
	})();

	const updateLightColor = (hex: string) => {
		const { r, g, b } = colord(hex).rgba;
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
				<h4>🌆️ Standby Lights after</h4>
				<div class="row">
					<input
						type="range"
						min="0" max={60 * 60 * 4} step="30"
						value={$plant.config.periods.light}
						on:input={({ currentTarget: { valueAsNumber } }) => {
							if (valueAsNumber === 0) valueAsNumber = 10;
							plant.updateConfig(c => ({ ...c, periods: { ...c.periods, light: valueAsNumber } }));
						}}
					/>
					<span>
						<Period seconds={$plant.config.periods.light} />
						h
					</span>
				</div>
			</label>
		</div>

		<div class="setting">
			<label>
				<h4>
					🎨️ Light Color Override
					<input
						type="checkbox"
						checked={Boolean(lightColor)}
						on:change={({ currentTarget: { checked } }) => {
							plant.updateConfig(c => ({ ...c, color: checked ? [20, 255, 0] : null }));
						}}
					/>
				</h4>
				{#if lightColor}
				<ColorRange
					type="hue"
					color={lightColor}
					on:input={({ detail: { color } }) => updateLightColor(color)}
				/>
				<ColorRange
					type="saturation"
					color={lightColor}
					on:input={({ detail: { color } }) => updateLightColor(color)}
				/>
				{/if}
			</label>
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

	label {
		display: flex;
		flex-direction: column;
		gap: 0.5em;
	}
	label span {
		display: inline-block;
		font-variant-numeric: tabular-nums;
		white-space: nowrap;
	}
</style>
