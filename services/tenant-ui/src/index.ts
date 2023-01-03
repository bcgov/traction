import config from "config";
import cors from "cors";
import express from "express";
import path from "path";

import { router } from "./routes/router";

const PORT: number = parseInt(config.get("server.port") as string, 10);
const APIROOT: string = config.get("server.apiPath");
const STATIC_FILES_PATH: string = config.get("server.staticFiles");

import history from "connect-history-api-fallback";

const app = express();
app.use(history());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));


// Host the static frontend assets
app.use("/favicon.ico", (_, res) => {
  res.redirect("/favicon.ico");
});
app.use("/", express.static(path.join(__dirname, STATIC_FILES_PATH)));

// Since the server config can have important secret values in, you must opt-in
// for server values (or other non FE config) that should return from /config
function _setupConfig() {
  return {
    frontend: config.get("frontend"),
    image: config.get("image"),
    server: {
      tractionUrl: config.get("server.tractionUrl"),
    },
  };
}

// Frontend configuration endpoint, return config section at /config so UI can get it
app.use("/config", (_, res, next) => {
  try {
    res.status(200).json(_setupConfig());
  } catch (err) {
    next(err);
  }
});

// This service's api endpoints
app.use(APIROOT, router);

app.listen(PORT, () => {
  console.log(`Listening on port ${PORT}`);
});
