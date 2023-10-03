<script lang="ts">
let config = {};
$: configDisplay = JSON.stringify(config, undefined, 2);

async function logConfig() {
	const response = await fetch("http://192.168.4.1/config");
	config = await response.json();
}
</script>

<main>
	<h1>Complant</h1>
	<button on:click={logConfig}>fetch config</button>
	<pre>{configDisplay}</pre>
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
