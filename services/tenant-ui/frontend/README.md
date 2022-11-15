# Vue 3 + TypeScript + Vite

This template should help get you started developing with Vue 3 and TypeScript in Vite. The template uses Vue 3 `<script setup>` SFCs, check out the [script setup docs](https://v3.vuejs.org/api/sfc-script-setup.html#sfc-script-setup) to learn more.

## Recommended IDE Setup

- [VS Code](https://code.visualstudio.com/) + [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) + [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode)
- disable [Vetur](https://marketplace.visualstudio.com/items?itemName=octref.vetur)

## Type Support For `.vue` Imports in TS

Since TypeScript cannot handle type information for `.vue` imports, they are shimmed to be a generic Vue component type by default. In most cases this is fine if you don't really care about component prop types outside of templates. However, if you wish to get actual prop types in `.vue` imports (for example to get props validation when using manual `h(...)` calls), you can enable Volar's Take Over mode by following these steps:

1. Run `Extensions: Show Built-in Extensions` from VS Code's command palette, look for `TypeScript and JavaScript Language Features`, then right click and select `Disable (Workspace)`. By default, Take Over mode will enable itself if the default TypeScript extension is disabled.
2. Reload the VS Code window by running `Developer: Reload Window` from the command palette.

You can learn more about Take Over mode [here](https://github.com/johnsoncodehk/volar/discussions/471).

## Formatting - Prettier and EsLint

Under the tenant-ui .vscode folder, we have added `extensions.json` and `settings.json`.

Extentions recommend [Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar) and [Prettier](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode) as noted above. This combined with the settings will allow you to format files on save or right-click and format using the eslint and prettier rules.

You can also run lint and lintfix commands to ensure your code is formatted correctly.

```sh
npm run lint
```

```sh
npm run lintfix
```

## Generating Typescript Schema for the API

### Examples

Generate schema from the **test** API

```bash
npm run generate-schema --url=https://traction-api-test.apps.silver.devops.gov.bc.ca/tenant/openapi.json
```

Generate schema from the local API

```bash
npm run generate-schema --url=https://localhost:5100/tenant/openapi.json
```
