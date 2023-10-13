<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { colord } from "colord";
	import { getID } from "../util";

	const dispatch = createEventDispatcher<{
		input: { color: string }
	}>();

	export let color: string;
	export let type: "hue" | "saturation" = "hue";

	const id = getID();

	$: col = colord(color);
	$: ({ r, g, b } = col.rgba);
	let value = colord(color).toHsv()[({ "hue": "h", "saturation": "s" } as const)[type]];
	let prevValue = value;
	$: if (value !== prevValue) {
		if (type === "hue") {
			col = col.hue(value);
		} else if (type === "saturation") {
			const { h, v } = col.toHsv();
			col = colord({ h, s: value, v });
		}
		color = col.toHex();
		prevValue = value;
	}
	$: dispatch("input", { color });
</script>

<svg xmlns="http://www.w3.org/2000/svg">
	<filter id={`color-${id}`}>
		<feColorMatrix
			in="SourceGraphic"
			type="matrix"
			values="0 0 0 0 {r / 255}
							0 0 0 0 {g / 255}
							0 0 0 0 {b / 255}
							0 0 0 1 0"
		/>
	</filter>
</svg>
<input
	style:--filter={`url('#color-${id}')`}
	class={type}
	type="range"
	min="0"
	max={type === "hue" ? 360 : 100}
	bind:value
	{...$$restProps}
/>

<style>
	svg {
		position: absolute;
		width: 0;
		height: 0;
		visibility: hidden;
	}

	input {
		accent-color: white;
	}

	input {
		filter: var(--filter);
	}
</style>
