<script lang="ts">
	export let value: number;
	export let type: "hue" | "saturation" = "hue";
	export let hue: number | undefined = undefined;
</script>

<div
	class={`color-range ${type}`}
	style:--hue={hue || 0}
>
	<input
		type="range"
		min="0"
		max={type === "hue" ? 360 : 100}
		step="any"
		bind:value
		on:input
		on:change
		on:blur
		{...$$restProps}
	/>
	<div class="scale" />
</div>

<style>
	.color-range {
		position: relative;
		display: inline-flex;
		transform: translate(0);
	}

	input {
		accent-color: #555;
		margin: 4px 2px;
	}

	.scale {
		position: absolute;
		top: 0;
		left: -5px;
		right: -5px;
		bottom: 0;

		pointer-events: none;
		mix-blend-mode: multiply;
		border-radius: 99999px;
	}
	.hue .scale {
		background-image: linear-gradient(to right,
			hsl(  0, 80%, 60%) 9px,
			hsl( 30, 80%, 60%),
			hsl( 60, 80%, 60%),
			hsl( 90, 80%, 60%),
			hsl(120, 80%, 60%),
			hsl(150, 80%, 60%),
			hsl(180, 80%, 60%),
			hsl(210, 80%, 60%),
			hsl(240, 80%, 60%),
			hsl(270, 80%, 60%),
			hsl(300, 80%, 60%),
			hsl(330, 80%, 60%),
			hsl(360, 80%, 60%) calc(100% - 9px)
		);
	}
	.saturation .scale {
		background-image: linear-gradient(to right,
			hsl(var(--hue),   0%, 100%) 9px,
			hsl(var(--hue), 100%,  60%) calc(100% - 9px)
		);
	}
</style>
