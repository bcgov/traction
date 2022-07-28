// The default router for the Tenant UI backend
// Expand on this (or add other router files) if the TenantUI backend should do much more business actions
// other than serving the static files and proxying to Traction

import express, { Request, Response } from "express";
import * as helloComponent from "../components/hello";

export const router = express.Router();

router.get("/hello", async (req: Request, res: Response) => {
    const result = helloComponent.getHello();
    res.status(200).send(result);
});