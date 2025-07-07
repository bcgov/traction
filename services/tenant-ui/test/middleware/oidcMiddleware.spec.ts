import { Request, Response, NextFunction } from "express";
import oidcMiddleware from "../../src/middleware/oidcMiddleware.js";
import { jwtVerify } from "jose";
import { Mock } from "vitest";

vi.mock(import("config"), async (importOriginal) => {
  const actual = await importOriginal()
  return {
    ...actual,
    get: vi.fn().mockReturnValue("http://example.com/.well-known/jwks.json")
  }
})
vi.mock("jose", () => ({
  createRemoteJWKSet: vi.fn(),
  jwtVerify: vi.fn(),
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
      status: vi.fn().mockReturnThis(),
      json: vi.fn(),
    };
    next = vi.fn();
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
    (jwtVerify as Mock).mockRejectedValue(new Error("Invalid token"));

    await oidcMiddleware(req as Request, res as Response, next);

    expect(res.status).toHaveBeenCalledWith(401);
    expect(res.json).toHaveBeenCalledWith({ message: "Invalid token", error: expect.any(Error) });
  });

  it("should call next if token is valid", async () => {
    req.headers!.authorization = "Bearer validtoken";
    (jwtVerify as Mock).mockResolvedValue({ payload: { sub: "123" } });

    await oidcMiddleware(req as AuthenticatedRequest, res as Response, next);

    expect(req.claims).toEqual({ sub: "123" });
    expect(next).toHaveBeenCalled();
  });
});