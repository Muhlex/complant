<script lang="ts">
	import { createEventDispatcher } from "svelte";
	import { clickOutside } from "./directives";

	const dispatch = createEventDispatcher<{
		input: { currentTarget: EventTarget & HTMLInputElement }
		blur: { currentTarget: EventTarget & HTMLInputElement }
	}>();

	export let value: string;

	let editing = false;
	let inputEl: HTMLInputElement | null = null;
	$: if (inputEl && editing) inputEl.focus();
	$: if (inputEl && !editing) {
		dispatch("blur", { currentTarget: inputEl });
	}
</script>

{#if editing}
<input
	type="text"
	value={value}
	bind:this={inputEl}
	on:keydown={({ key }) => { if (["Escape", "Enter"].includes(key)) editing = false; }}
	on:input={event => dispatch("input", event)}
	use:clickOutside={() => editing = false}
/>
{:else}
<span
	role="button" tabindex="0"
	on:click={() => editing = true}
	on:keydown={({ key }) => { if ([" ", "Enter"].includes(key)) editing = true; }}
>
	{value}
</span>
{/if}
