interface StartupBannerVals {
  port: number;
  apiRoot: string;
  staticPath: string;
}

export function logStartupBanner(vals: StartupBannerVals): void {
  // Print a startup banner with server details
  const env = process.env.NODE_ENV || "development";
  console.log("");
  console.log("🔷 Server Startup");
  console.log(`- Mode:               ${env}`);
  console.log(`- API Root:           ${vals.apiRoot}`);
  console.log(`- Port:               ${vals.port}`);
  console.log(`- Tenant UI FE dist:  ${vals.staticPath}`);
  console.log("🚀 Tenant UI Backend is up 🚀");
  console.log("");
}
