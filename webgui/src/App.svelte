<script lang="ts">
	import { onDestroy } from "svelte";

	import { Plants } from "./models/Plants";

	import PlantsComponent from "./lib/Plants.svelte";

	const plants = new Plants();
	onDestroy(() => plants.release());
</script>

<main>
	<h1>
		<span>🪴️</span>
		<span>Complant</span>
	</h1>
	<PlantsComponent {plants} />
</main>

<style>
	main {
		width: 100%;
		max-width: 800px;
		margin: 0 auto;
		padding: 4em 0.5em;

		display: flex;
		flex-direction: column;
		gap: 4em;
	}

	h1 {
		display: flex;
		flex-direction: column;
		gap: 0.25em;

		text-align: center;
	}
</style>
