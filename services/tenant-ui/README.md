# Traction Tenant UI

## Overview

The Tenant UI is a frontend web dashboard that will authenticate a wallet key/secret and allow a user to make calls for that wallet to the Traction API.

The architechture consists of

- A Node app that serves the frontend, handles environment configuration, and can provide any minimal Tenant-UI-specific business functionality (like sending an email or something)
- A Vue3 frontend app providing the UI

![Arch Diagram](/docs/assets/tenant-ui-flow-chart-svg.svg)

## Set up your configuration

In tenant-ui/config add a `local.json` file to add any specific config you'd like for your local instance (otherwise see `default.json` for defaults). At this point the only thing you'll probably want to override is the Traction URL. So your local.json can just look like this for example:

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

### Running Tests

To Run tests simply execute

```bash
  npm run test
```

In addition to running tests this will also produce code coverage statistics.

To test your changes in the same environment you would see in production use

```bash
    npm run build
    npm run start
```

## Using docker

Build and run a docker image (example shows using environment variable to point at a specific Traction Instance)

```bash
docker build . -t local/traction-ui
docker run --env SERVER_TRACTION_URL=https://traction-api-test.apps.silver.devops.gov.bc.ca/ FRONTEND_TENANT_PROXY_URL=https://traction-tenant-proxy-test.apps.silver.devops.gov.bc.ca/ -p 8080:8080 -d local/traction-ui
```

## Internationalization

The Tenant UI uses [Vue I18n](https://vue-i18n.intlify.dev/) to handle internationalization for the Vue app.

When developing, review the [documentation](https://vue-i18n.intlify.dev/guide/essentials/syntax.html) for the basic syntax for that library quickly to understand the localization features used. Internatonalization settings are handled in the `i18n` folder and translations are kept in `json` files for each language there.

When developing the Tenant UI, adhere to localization best practices including

- Do not handle any localization logic or translations in the components themselves. The frontend code should only deal with message string names, and all localizations should be handled exclusively in the language `json` files.
- Use proper responsive design principles, and do not space UI components based on english language text lengths. Translated UI elements might end up shorter or much longer, so overflows of text should always work accordingly.

Currently localization is handled at the Tenant UI frontend level, but data that returns to the frontend from the Traction and AcaPy APIs may not include localization of text and status codes, etc. As such, full localization is a work in progress and will require some future work in integrating with Traction and AcaPy.


To ensure that the language files are consistent with each other additional helper scripts have been added

- `fill-keys` takes everything in en.json and fills the other lang files with the entries suffixed by the locale code.
- `common-keys` looks at which keys point to the same values so they can be refactored into a common key.
- `sort-keys` does exactly what it says

To execute any of these scripts navigate to `services/tenant-ui/frontend` and execute

```
npm run i18n:fill-keys
```

Replacing `fill-keys` with which ever script your would like to run

## OIDC Login for Innkeeper

The Tenant UI Inkeeper functionality can be configured to log in with either (or both)
- the Innkeeper secret
- a configured OIDC provider

To set up the OIDC provider of your choice, add configuration values in your deployment to match the `frontend.innkeeperOidc` fields for a auth code grant client,a nd configure the `server.oidc` fields appropriately to veify the JWKS for tokens from that client. 

As well, the Innkeeper secret must be available to the Tenant UI server, this is set in `server.innkeeper` configuration...

## Email Mocking

Email is used in multiple components of `tenent-ui` for development
purposes we have included [maildev](https://maildev.github.io/maildev/) to assist with monitoring and
mocking these emails in place of a proper SMTP server.

To enable this set the following environment variables before starting the `tenant-ui`
- `SERVER_SMTP_SERVER=maildev`
- `SERVER_SMTP_PORT=1025`

To view the emails being sent open http://localhost:1080/ in your web browser

By default this is already configured in the docker-compose file. For
local use you will need to start `maildev` manually.

## Configuring Matomo

If you would like to use Matomo for tracking you can set the FRONTEND_MATOMO_URL environment variable as exposed in [custom-environment-variables.json](../config/custom-environment-variables.json)

If no value is set using either of these methods MATOMO tracker code will never be loaded.

For more information on configuration settings see
[Set up your configuration](https://github.com/bcgov/traction/tree/main/services/tenant-ui#set-up-your-configuration)

## Log Streaming

The Tenant UI can display streamed logs from a Loki aggregator. For details on setup, see ["Optional Local Log Streaming Setup" in the scripts README](../../scripts/README.md)