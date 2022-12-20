// The default router for the Tenant UI backend
// Expand on this (or add other router files) if the TenantUI backend should do much more business actions
// other than serving the static files and proxying to Traction

import express, { Request, Response } from "express";
import config from "config";
import * as emailComponent from "../components/email";
import * as innkeeperComponent from "../components/innkeeper";
import { secure } from "express-oauth-jwt";
import { body, validationResult } from "express-validator";
import { createRemoteJWKSet } from "jose";
import { NextFunction } from "express";

const jwksService = createRemoteJWKSet(
  new URL(config.get("server.oidc.jwksUri"))
);

export const router = express.Router();

router.use(express.json());

// For the secured innkeepr OIDC login request to verify the token and get a token from Traction
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
      req.claims.realm_access.roles.includes(config.get("server.oidc.roleName"))
    ) {
      const result = await innkeeperComponent.login();
      res.status(200).send(result);
    } else {
      res.status(403).send();
    }
  }
);

// Email endpoint
router.post(
  "/email/reservationConfirmation",
  body("contact_email").isEmail(),
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        return res.status(422).json({ errors: errors.array() });
      }

      const result = await emailComponent.sendEmail(req);
      res.send(result);
    } catch (error) {
      next(error);
    }
  }
);
router.post("/email/reservationStatus", async (req: Request, res: Response) => {
  const result = await emailComponent.sendEmail(req);
  res.send(result);
});
