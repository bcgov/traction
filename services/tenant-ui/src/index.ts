import config from "config";
import cors from "cors";
import express from "express";
import { Request, Response, NextFunction } from "express";
import path, { dirname } from "path";
import { fileURLToPath } from "url";

import { router } from "./routes/router.js";
import { logStartupBanner } from "./helpers/startbanner.js";
import { configureLogStream } from "./services/log-stream.js";

const API_ROOT: string = config.get("server.apiPath");
const LOKI_URL: string = config.get("server.lokiUrl");
const PORT: number = parseInt(config.get("server.port") as string, 10);
const STATIC_FILES_PATH: string = config.get("server.staticFiles");

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

import history from "connect-history-api-fallback";

const app = express();

app.use(history());
app.use(cors());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

// Host the static frontend assets
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
app.use(API_ROOT, router);

// Catch-all error handler (Express 5 style)
app.use((err: any, _req: Request, res: Response, _next: NextFunction) => {
  console.error(err);

  res.status(err.status || 500).json({
    error: {
      message: err.message || "Internal Server Error",
    },
  });
});

// Start the server
const server = app.listen(PORT, () => {
  logStartupBanner({
    port: PORT,
    apiRoot: API_ROOT,
    staticPath: STATIC_FILES_PATH,
    lokiUrl: LOKI_URL,
  });
});

// If logging is enabled, wire the log stream
if (LOKI_URL) {
  configureLogStream(server);
}
