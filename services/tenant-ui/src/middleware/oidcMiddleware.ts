import { createRemoteJWKSet, jwtVerify, JWTPayload } from "jose";
import config from "config";
import { Request, Response, NextFunction } from "express";

// Extend Express Request to include claims
interface AuthenticatedRequest extends Request {
  claims?: JWTPayload;
}

const jwksUri = new URL(config.get("server.oidc.jwksUri"));
const jwks = createRemoteJWKSet(jwksUri);

const oidcMiddleware = async (
  req: AuthenticatedRequest,
  res: Response,
  next: NextFunction
) => {
  const authHeader = req.headers.authorization;
  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    res.status(401).json({ message: "Unauthorized" });
    return;
  }
  const token = authHeader.split(" ")[1];
  try {
    const { payload } = await jwtVerify(token, jwks);
    req.claims = payload;
    next();
  } catch (error) {
    res.status(401).json({ message: "Invalid token", error });
  }
};

export default oidcMiddleware;
