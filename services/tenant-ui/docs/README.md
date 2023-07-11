# Documents for the Tenant-UI Service

## Configuring Matomo

If you would like to use Matomo for tracking you can set `frontend.matomoUrl` in
[custom-environment-variables.json](../config/custom-environment-variables.json)
alternatively you can set the `FRONTEND_MATOMO_URL` environment variable.

If no value is set the MATOMO tracker code will never be loaded.
