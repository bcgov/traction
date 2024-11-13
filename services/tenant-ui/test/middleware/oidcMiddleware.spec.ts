import { Request, Response, NextFunction } from "express";
import oidcMiddleware from "../../src/middleware/oidcMiddleware";
import { jwtVerify } from "jose";

jest.mock("config", () => ({
    get: jest.fn().mockReturnValue("http://example.com/.well-known/jwks.json"),
  }));
jest.mock("jose", () => ({
  createRemoteJWKSet: jest.fn(),
  jwtVerify: jest.fn(),
}));

interface AuthenticatedRequest extends Request {
  claims?: Record<string, any>;
}

describe("oidcMiddleware", () => {
  let req: Partial<AuthenticatedRequest>;
  let res: Partial<Response>;
  let next: NextFunction;

  beforeEach(() => {
    req = {
      headers: {},
    };
    res = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };
    next = jest.fn();
  });

  it("should return 401 if no authorization header is present", async () => {
    await oidcMiddleware(req as Request, res as Response, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: "Unauthorized" });
  });

  it("should return 401 if authorization header does not start with 'Bearer '", async () => {
    req.headers!.authorization = "Basic abcdef";

    await oidcMiddleware(req as Request, res as Response, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: "Unauthorized" });
  });

  it("should return 401 if token is invalid", async () => {
    req.headers!.authorization = "Bearer invalidtoken";
    (jwtVerify as jest.Mock).mockRejectedValue(new Error("Invalid token"));

    await oidcMiddleware(req as Request, res as Response, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: "Invalid token", error: expect.any(Error) });
  });

  it("should call next if token is valid", async () => {
    req.headers!.authorization = "Bearer validtoken";
    (jwtVerify as jest.Mock).mockResolvedValue({ payload: { sub: "123" } });

    await oidcMiddleware(req as AuthenticatedRequest, res as Response, next);

    expect(req.claims).toEqual({ sub: "123" });
    expect(next).toHaveBeenCalled();
  });
});