<script lang="ts">
	export let seconds = 0;
	$: ({ h, m, s } = (() => {
		const date = new Date(1000 * seconds);
		return { h: date.getUTCHours(), m: date.getUTCMinutes(), s: date.getUTCSeconds() };
	})());
	const pad = (value: number) => String(value).padStart(2, "0");
</script>

<span class="period">
	<span>{pad(h)}<small>h</small></span>
	<span>{pad(m)}<small>m</small></span>
	<span>{pad(s)}<small>s</small></span>
</span>

<style>
	.period {
		display: inline-flex;
		gap: 0.125em;
		font-variant-numeric: tabular-nums;
	}

	small {
		font-size: 0.75em;
	}
</style>
