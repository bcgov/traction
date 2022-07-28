# Traction Tenant UI

## Overview

The Tenant UI is a frontend web dashboard that will authenticate a wallet key/secret and allow a user to make calls for that wallet to the Traction API.

The architechture consists of
- A Node app that serves the frontend, handles environment configuration, and can provide any minimal Tenant-UI-specific business functionality (like sending an email or something)
- A Vue3 frontend app providing the UI

## Set up your configuration
In tenant-ui/src/config add a `local.json` file to add any specific config you'd like for your local instance (otheriwse see `default.json` for defaults). At this point the only thing you'll probably want to override is the Traction URL. So your local.json can just look like this for example:

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
