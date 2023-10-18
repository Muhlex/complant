<script lang="ts">
	import { PlantsLoadState, type Plants } from "../models/Plants";

	import Panel from "../lib/Panel.svelte";
	import Period from "../lib/Period.svelte";
	import Plant from "../lib/Plant.svelte";

	export let plants: Plants;
	$: referencePlant = [...$plants][0];
</script>

{#if $plants.state === PlantsLoadState.Loading}
	<h2>Finding Plants...</h2>
{:else if $plants.state === PlantsLoadState.Error}
	<h2>❌️ Error fetching Plants.</h2>
{:else}
	<section>
		<h2>Global Settings</h2>
		<Panel>
			{#if !$referencePlant.config}
				<h3>Loading...</h3>
			{:else}
				<div class="setting">
					<label>
						<h4>💬️ Time between Conversations</h4>
						<div class="row">
							<input
								type="range"
								min="0" max={60 * 60 * 4} step="30"
								value={$referencePlant.config.periods.conversation}
								on:input={({ currentTarget: { valueAsNumber } }) => {
									plants.updateConfig(c => ({ ...c, periods: { ...c.periods, conversation: valueAsNumber } }));
								}}
							/>
							<span>
								<Period seconds={$referencePlant.config.periods.conversation} />
							</span>
						</div>
					</label>
				</div>
			{/if}
		</Panel>
	</section>
	<section>
		<h2>Your Plants</h2>
		{#each $plants as plant (plant.ip)}
			<Panel>
				<Plant {plant} />
			</Panel>
		{/each}
	</section>
{/if}

<style>
	h2 {
		margin-top: 1em;
		text-align: center;
	}

	section {
		display: flex;
		flex-direction: column;
		gap: 1em;
	}

	.row {
		display: flex;
		align-items: center;
		gap: 0.5em;
	}

	input {
		min-width: 0;
		flex-grow: 1;
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
