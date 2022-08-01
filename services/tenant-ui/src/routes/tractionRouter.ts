// Not really a router, but the configuration to proxy calls to THIS backend over to Traction
import config from 'config';
import { createProxyMiddleware, fixRequestBody } from 'http-proxy-middleware';

// Send calls to api/traction to the configured Traction environment
// If we need to alter any request bodies or anything when coming from the tenant UI
// can do that in these options (like with onProxyReq)
// https://www.npmjs.com/package/http-proxy-middleware#intercept-and-manipulate-requests
const TRACURL: string = config.get('server.tractionUrl');
const options = {
    target: TRACURL,
    changeOrigin: true,
    // So we go to the root of proxied traction (lose the api/traction part)
    pathRewrite: { '^/api/traction': '' },
    followRedirects: true,
    // So that express body-parser can be used as well
    onProxyReq(proxyReq: any, req: any, res: any) {
        // TODO This is kind of a hack and can't figure out why we need it. THe fixRequestBody shim is needed
        // to allow application/json posts to work through the proxy, but then the token fetch in traction is
        // x-www-urlformencoded, and the shim then seems to break that. I think there's got to be another way to 
        // handle this but for now just don't adjust bodies for the 1 token endpoint
        if (!req.originalUrl.includes('tenant/token')) {
            return fixRequestBody(proxyReq, req);
        }
    }
};

export const tractionProxy = createProxyMiddleware(options);