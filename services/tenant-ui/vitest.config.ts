import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    globals: true,
    environment: "node",
    include: ["test/**/*.{test,spec}.{js,ts}"],
    coverage: {
      provider: "v8",
      include: ["src/**/*.{js,ts}"],
      exclude: [
        "src/**/*.d.ts",
        "src/**/*.config.{js,ts}",
      ],
      reporter: ["text", "lcov", "html"],
      reportsDirectory: "./coverage",
    },
  },
});
