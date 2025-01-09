// The default router for the Tenant UI backend
// Expand on this (or add other router files) if the TenantUI backend should do much more business actions
// other than serving the static files and proxying to Traction

import express, { Request, Response } from "express";
import config from "config";
import * as emailComponent from "../components/email";
import * as innkeeperComponent from "../components/innkeeper";
import { body, validationResult } from "express-validator";
import { NextFunction } from "express";
import oidcMiddleware from "../middleware/oidcMiddleware";

export const router = express.Router();

router.use(express.json());

// For the secured innkeepr OIDC login request to verify the token and get a token from Traction
router.get(
  "/innkeeperLogin",
  oidcMiddleware,
  async (req: any, res: Response, next: NextFunction) => {
    try {
      // Validate JWT from OIDC login before moving on
      // The realm access check below is pretty Keycloak specific
      // It's a TODO later to see how this could be a more generic OIDC claim
      console.log(req.claims);
      if (
        req.claims.realm_access &&
        req.claims.realm_access.roles &&
        req.claims.realm_access.roles.includes(
          config.get("server.oidc.roleName")
        )
      ) {
        const result = await innkeeperComponent.login();
        res.status(200).send(result);
      } else {
        res.status(403).send();
      }
    } catch (error) {
      console.error(`Error logging in: ${error}`);
      next(error);
    }
  }
);

// Protected reservation endpoint
router.post(
  "/innkeeperReservation",
  async (req: any, res: Response, next: NextFunction) => {
    try {
      // Get innkeeper token from login method
      const { token } = await innkeeperComponent.login();

      const result = await innkeeperComponent.createReservation(req, token);
      res.status(201).send(result);
    } catch (error) {
      next(error);
    }
  }
);

// Email endpoint
router.post(
  "/email/reservationConfirmation",
  body("contactEmail").isEmail(),
  body("reservationId").not().isEmpty(),
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        res.status(422).json({ errors: errors.array() });
        return;
      }

      const result = await emailComponent.sendConfirmationEmail(req);
      res.send(result);
    } catch (error) {
      next(error);
    }
  }
);

router.post(
  "/email/reservationStatus",
  body("contactEmail").isEmail(),
  body("reservationId").not().isEmpty(),
  body("state").not().isEmpty(),
  async (req: Request, res: Response, next: NextFunction) => {
    try {
      const errors = validationResult(req);
      if (!errors.isEmpty()) {
        res.status(422).json({ errors: errors.array() });
        return
      }

      const result = await emailComponent.sendStatusEmail(req);
      res.send(result);
    } catch (error) {
      next(error);
    }
  }
);
