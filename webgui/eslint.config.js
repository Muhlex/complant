import globals from "globals";

import js from "@eslint/js";
import ts from "@typescript-eslint/eslint-plugin";
import svelte from "eslint-plugin-svelte";

import tsParser from "@typescript-eslint/parser";
import svelteParser from "svelte-eslint-parser";

const tsParserOptions = {
	extraFileExtensions: [".svelte"],
	project: ["./tsconfig.json", "./tsconfig.node.json"],
};

const rules = {
	"indent": ["error", "tab", { "SwitchCase": 1 }],
	"no-mixed-spaces-and-tabs": ["error", "smart-tabs"],
	"no-trailing-spaces": "error",
	"eol-last": ["error", "always"],

	"comma-dangle": ["warn", "always-multiline"],
	"quotes": ["warn", "double"],
	"semi": ["error", "always"],
	"array-bracket-spacing": ["warn", "never"],
	"object-curly-spacing": ["warn", "always"],
	"space-infix-ops": ["warn", { "int32Hint": false }],
	"camelcase": "warn",
	"keyword-spacing": "warn",

	"eqeqeq": ["error", "always"],
	"no-var": "error",
	"prefer-const": "error",
	"no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
};

const tsRules = {
	...ts.configs["eslint-recommended"].overrides[0].rules,
	...ts.configs["recommended"].rules,
	...rules,
	"no-unused-vars": "off",
	"@typescript-eslint/no-unused-vars": ["warn", { "argsIgnorePattern": "^_" }],
	"@typescript-eslint/no-this-alias": "off",
};

const svelteRules = {
	...svelte.configs.recommended.rules,
	...tsRules,
	"no-inner-declarations": "off",
};

export default [
	js.configs.recommended,
	{
		files: ["*.{js,ts}"], // top level
		languageOptions: {
			globals: {
				...globals.node,
			},
		},
	},
	{
		files: ["**/*.{js,jsx}"],
		rules,
	},
	{
		files: ["**/*.{ts,tsx}"],
		plugins: { "@typescript-eslint": ts },
		languageOptions: {
			parser: tsParser,
			parserOptions: tsParserOptions,
		},
		rules: tsRules,
	},
	{
		files: ["**/*.svelte"],
		plugins: { "@typescript-eslint": ts, svelte },
		languageOptions: {
			parser: svelteParser,
			parserOptions: {
				parser: { // parsers for <script> tags
					ts: tsParser,
				},
				...tsParserOptions,
			},
		},
		rules: svelteRules,
	},
];
