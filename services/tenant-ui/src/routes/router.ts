// The default router for the Tenant UI backend
// Expand on this (or add other router files) if the TenantUI backend should do much more business actions
// other than serving the static files and proxying to Traction

import express, { Request, Response } from "express";
import * as helloComponent from "../components/hello";
import * as innkeeperComponent from "../components/innkeeper";
const { secure } = require("express-oauth-jwt");
import { createRemoteJWKSet } from "jose";

const jwksService = createRemoteJWKSet(
  new URL(
    "https://dev.loginproxy.gov.bc.ca/auth/realms/digitaltrust-nrm/protocol/openid-connect/certs"
  )
);

export const router = express.Router();
router.use(secure(jwksService, { realm: "digitaltrust-nrm" }));

router.get("/hello", async (req: Request, res: Response) => {
  const result = helloComponent.getHello();
  res.status(200).send(result);
});

router.get(
  "/innkeeperLogin",
  secure(jwksService),
  async (req: any, res: Response) => {
    // Validate JWT from OIDC login before moving on
    // The realm access check below is pretty Keycloak specific
    // It's a TODO later to see how this could be a more generic OIDC claim
    console.log(req.claims);
    if (
      req.claims.realm_access &&
      req.claims.realm_access.roles &&
      req.claims.realm_access.roles.includes("innkeeper")
    ) {
      const result = await innkeeperComponent.login();
      res.status(200).send(result);
    } else {
      res.status(403).send();
    }
  }
);
