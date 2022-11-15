// Not really a router, but the configuration to proxy calls to THIS backend over to Traction
import config from "config";
import { createProxyMiddleware, fixRequestBody } from "http-proxy-middleware";
import * as express from "express";
import * as http from "http";

// Send calls to api/traction/acapy to the configured Acapy environment
// If we need to alter any request bodies or anything when coming from the tenant UI
// can do that in these options (like with onProxyReq)
// https://www.npmjs.com/package/http-proxy-middleware#intercept-and-manipulate-requests
const ACAPYURL: string = config.get("server.acapyAdminUrl");
const PROXYACAPYROOT: string = config.get("server.proxyAcapyPath");

const options = {
  target: ACAPYURL,
  changeOrigin: true,
  // So we go to the root of proxied traction (lose the api/traction/acapy part)
  pathRewrite: { [`^${PROXYACAPYROOT}`]: "" },
  followRedirects: true,
  // So that express body-parser can be used as well
  onProxyReq(proxyReq: http.ClientRequest, req: express.Request) {
    return fixRequestBody(proxyReq, req);
  },
};

export const acapyProxy = createProxyMiddleware(options);
