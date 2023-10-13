<script lang="ts">
	export let seconds = 0;
	$: ({ h, m, s } = (() => {
		const date = new Date(1000 * seconds);
		return { h: date.getUTCHours(), m: date.getUTCMinutes(), s: date.getUTCSeconds() };
	})());
	const pad = (value: number) => String(value).padStart(2, "0");
</script>

<span class="period">
	<span>{pad(h)}</span>:<span>{pad(m)}</span>:<span>{pad(s)}</span>
</span>

<style>
	.period {
		display: inline-flex;
		gap: 0.0625em;
		font-variant-numeric: tabular-nums;
	}
</style>
