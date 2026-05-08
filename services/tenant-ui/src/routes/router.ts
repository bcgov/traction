// The default router for the Tenant UI backend
// Expand on this (or add other router files) if the TenantUI backend should do much more business actions
// other than serving the static files and proxying to Traction

import express, { Request, Response } from "express";
import config from "config";
import { body, validationResult, CustomValidator } from "express-validator";

// Allow https for any host, or http only for local development origins.
const isAllowedStatusRouteUrl: CustomValidator = (value: string) => {
  let url: URL;
  try {
    url = new URL(value);
  } catch {
    throw new Error("Invalid URL");
  }
  const isLocalhost = url.hostname === "localhost" || url.hostname === "127.0.0.1";
  if (url.protocol === "https:") return true;
  if (url.protocol === "http:" && isLocalhost) return true;
  throw new Error("URL must use https, or http for localhost only");
};

import * as emailComponent from "../components/email.js";
import * as innkeeperComponent from "../components/innkeeper.js";
import oidcMiddleware from "../middleware/oidcMiddleware.js";

export const router = express.Router();

router.use(express.json());

// For the secured innkeepr OIDC login request to verify the token and get a token from Traction
router.get(
  "/innkeeperLogin",
  oidcMiddleware,
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
      res.status(200).json(result);
    } else {
      res.status(403).json({ error: "Forbidden" });
    }
  }
);

// Protected reservation endpoint
router.post("/innkeeperReservation", async (req: any, res: Response) => {
  // Get innkeeper token from login method
  const { token } = await innkeeperComponent.login();

  const result = await innkeeperComponent.createReservation(req, token);
  res.status(201).json(result);
});

// Email endpoint
router.post(
  "/email/reservationConfirmation",
  body("contactEmail").isEmail(),
  body("contactName").notEmpty().trim().escape(),
  body("reservationId").not().isEmpty(),
  body("serverUrlStatusRoute").custom(isAllowedStatusRouteUrl),
  async (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      res.status(422).json({ errors: errors.array() });
      return;
    }

    await emailComponent.sendConfirmationEmail(req);
    res.status(204).send();
  }
);

router.post(
  "/email/reservationStatus",
  body("contactEmail").isEmail(),
  body("contactName").notEmpty().trim().escape(),
  body("reservationId").not().isEmpty(),
  body("state").not().isEmpty(),
  body("serverUrlStatusRoute").optional().custom(isAllowedStatusRouteUrl),
  async (req: Request, res: Response) => {
    const errors = validationResult(req);
    if (!errors.isEmpty()) {
      res.status(422).json({ errors: errors.array() });
      return;
    }

    await emailComponent.sendStatusEmail(req);
    res.status(204).send();
  }
);
