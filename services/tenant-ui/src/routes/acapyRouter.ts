// Not really a router, but the configuration to proxy calls to THIS backend over to Traction
import config from "config";
import { createProxyMiddleware, fixRequestBody } from "http-proxy-middleware";
import * as http from "http";

// Send calls to api/traction/acapy to the configured Acapy environment
// If we need to alter any request bodies or anything when coming from the tenant UI
// can do that in these options (like with onProxyReq)
// https://www.npmjs.com/package/http-proxy-middleware#intercept-and-manipulate-requests
const ACAPYURL: string = config.get("server.acapyAdminUrl");
const PROXYACAPYROOT: string = config.get("server.proxyAcapyPath");
const XAPIKEY: string = config.get("server.acapyAdminApiKey");

const options = {
  target: ACAPYURL,
  changeOrigin: true,
  // So we go to the root of proxied traction (lose the api/traction/acapy part)
  pathRewrite: { [`^${PROXYACAPYROOT}`]: "" },
  followRedirects: true,
  // So that express body-parser can be used as well
  onProxyReq(proxyReq: http.ClientRequest, req: any) {
    // add the x-api-key from the secret for calls to the acapy admin api
    // this is only allowed on permitted routes where the wallet's token is also supplied
    proxyReq.setHeader("X-API-KEY", XAPIKEY);

    // Set the token to the ACAPY key (see acapy.ts middleware comments)
    proxyReq.setHeader("authorization", `Bearer ${req.parsedToken.key}`);

    return fixRequestBody(proxyReq, req);
  },
};

export const acapyProxy = createProxyMiddleware(options);
