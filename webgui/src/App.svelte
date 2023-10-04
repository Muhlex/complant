<script lang="ts">
let config: any = {};
let volume = 0;

$: configDisplay = JSON.stringify(config, undefined, 2);

async function logConfig() {
	const response = await fetch("http://192.168.4.1/api/config");
	config = await response.json();
	volume = config.volume;
}
</script>

<main>
	<h1>🪴 Complant</h1>
	<button on:click={logConfig}>fetch config</button>
	<pre>{configDisplay}</pre>

	<label>
		Volume: {volume}<br>
		<input type="range" bind:value={volume} min="0" max="30" />
	</label>
	<button on:click={async () => await fetch("http://192.168.4.1/api/volume", {
		method: "POST",
		headers: { "Content-Type": "application/json" },
		body: JSON.stringify({ value: volume }),
	})}>
		Change volume
	</button>
</main>

<style>
	main {
		width: 100%;
		max-width: 800px;
		margin: 0 auto;
		padding: 1em;
	}

	h1 {
		margin-bottom: 1em;
	}
</style>
