import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { logStartupBanner } from "../../src/helpers/startbanner.js";

describe("startbanner", () => {
  let consoleSpy: ReturnType<typeof vi.spyOn>;
  let originalNodeEnv: string | undefined;

  beforeEach(() => {
    consoleSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    originalNodeEnv = process.env.NODE_ENV;
  });

  afterEach(() => {
    consoleSpy.mockRestore();
    process.env.NODE_ENV = originalNodeEnv;
  });

  it("should log the startup banner with default development env", () => {
    // Test the "development" default branch
    delete process.env.NODE_ENV;

    logStartupBanner({
      port: 3000,
      apiRoot: "/api",
      staticPath: "/static",
    });

    expect(consoleSpy).toHaveBeenCalledWith(
      "- Mode:               development"
    );
  });

  it("should log the startup banner with custom NODE_ENV", () => {
    // Test when NODE_ENV is explicitly set
    process.env.NODE_ENV = "production";

    logStartupBanner({
      port: 3000,
      apiRoot: "/api",
      staticPath: "/static",
    });

    expect(consoleSpy).toHaveBeenCalledWith("- Mode:               production");
  });
});
