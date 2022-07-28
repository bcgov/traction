import bodyParser from "body-parser";
import config from "config";
import cors from "cors";
import express from "express";
import path from "path";

import { router } from "./routes/router";
import { tractionProxy } from "./routes/tractionRouter";

const PORT: number = parseInt(config.get('server.port') as string, 10);
const APIROOT: string = config.get('server.apiPath');

const app = express();
app.use(cors());
app.use(express.json());
// app.use(bodyParser.json());

// Host the static frontend assets
app.use('/favicon.ico', (_req, res) => { res.redirect('/favicon.ico'); });
app.use('/', express.static(path.join(__dirname, '../../frontend/dist')));

// Frontend configuration endpoint, return config section at /config so UI can get it
app.use('/config', (_req, res, next) => {
    try {
        const frontend = config.get('frontend');
        res.status(200).json(frontend);
    } catch (err) {
        next(err);
    }
});

// This service's api endpoints
app.use(APIROOT, router);

// Proxy any api/traction calls over to Traction
app.use(`${APIROOT}/traction`, tractionProxy);

app.listen(PORT, () => {
    console.log(`Listening on port ${PORT}`);
});