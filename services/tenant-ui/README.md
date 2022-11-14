# Traction Tenant UI

## Overview

The Tenant UI is a frontend web dashboard that will authenticate a wallet key/secret and allow a user to make calls for that wallet to the Traction API.

The architechture consists of

- A Node app that serves the frontend, handles environment configuration, and can provide any minimal Tenant-UI-specific business functionality (like sending an email or something)
- A Vue3 frontend app providing the UI

## Set up your configuration

In tenant-ui/config add a `local.json` file to add any specific config you'd like for your local instance (otheriwse see `default.json` for defaults). At this point the only thing you'll probably want to override is the Traction URL. So your local.json can just look like this for example:

```
{
  "server": {
    "tractionUrl": "https://traction-api-test.apps.silver.devops.gov.bc.ca/"
  }
}
```

## Running the App

To just start up the app on your local navigate a terminal to `services/tenant-ui/` and install the libraries

```bash
npm ci
cd frontend
npm ci
```

start the API from `services/tenant-ui/`

```bash
npm run start
```

This starts up the API and builds the FE and serves the frontend from [here](localhost:8080)

## Developing

To develop the backend and frontend you'll want hot-reloading and the 2 things run as separate processes so from `services/tenant-ui/` run

```bash
npm ci
npm run dev
```

and then in a separate terminal in `services/tenant-ui/frontend`

```bash
npm ci
npm run dev
```

The Vite hot-module-reload app will serve from [here](http://127.0.0.1:5173/).

## Using docker

Build and run a docker image (example shows using environment variable to point at a specific Traction Instance)

```bash
docker build . -t local/traction-ui
docker run --env SERVER_TRACTION_URL=https://traction-api-test.apps.silver.devops.gov.bc.ca/ -p 8080:8080 -d local/traction-ui
```

## Internationalization

The Tenant UI uses [Vue I18n](https://vue-i18n.intlify.dev/) to handle internationalization for the Vue app.

When developing, review the [documentation](https://vue-i18n.intlify.dev/guide/essentials/syntax.html) for the basic syntax for that library quickly to understand the localization features used. Internatonalization settings are handled in the `i18n` folder and translations are kept in `json` files for each language there.

When developing the Tenant UI, adhere to localization best practices including

- Do not handle any localization logic or translations in the components themselves. The frontend code should only deal with message string names, and all localizations should be handled exclusively in the language `json` files.
- Use proper responsive design principles, and do not space UI components based on english language text lengths. Translated UI elements might end up shorter or much longer, so overflows of text should always work accordingly.

Currently localization is handled at the Tenant UI frontend level, but data that returns to the frontend from the Traction and AcaPy APIs may not include localization of text and status codes, etc. As such, full localization is a work in progress and will require some future work in integrating with Traction and AcaPy.

## Generating Typescript Schema for the API

```bash
npm run generate-schema
```

Or

```bash
npx openapi-typescript https://traction-api-test.apps.silver.devops.gov.bc.ca/tenant/openapi.json --output schema.ts
```
