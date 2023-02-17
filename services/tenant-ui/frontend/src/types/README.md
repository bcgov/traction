# Typescript structure

- Work in progress while we go through setting up types

## ACA-Py API Types

Types for request/response objects from the ACA-Py API (and deployed plugins) will be generated from the Swagger doc.

A couple things about the Swagger docs though, it's old 2.0 Swagger spec (rather than OpenAPI 3+), and has many strucural errors that fail validation at this point, so lots of generators are seeming to have trouble with it.

For example, on a local Docker deployment, can see the Swagger page at:

`http://localhost:8031/api/doc`

and the swagger JSON file used to generate this interface can be downloaded from there (`http://localhost:8031/api/docs/swagger.json`).

For this workflow, the swagger file will just be used as a manual generation to auto-create types for the TenantUI. It will not:

1. Be used in any CI/CD or build processes, just as a standalone for development
1. Be installed as a npm dependency in the app itself

**Do not make any changes to the generated acapyInterface.ts generated file.** Treat it as generator code, if changes are needing to be made, then this approach needs to be re-evaluated as it would mean there's enough issues with the swagger spec as to not be reliable.

For frontend (non request/response) specific types, which are needed in places, create a interface extending the generated one, or a new interface entirely. See "Other interfaces/types/enums" below.

### Regenerating types

The `swagger-typescript-api` package works with the older spec and validation issues, so that can be used locally if a regeneration of the api types file is needed when new endpoints or changes are adapted to.

1. Get the swagger JSON locally from any **Traction ACA-Py deployment**. It is important to have all required Traction Plugins be there for this.
2. On your local machine anywhere, navigate to the location of the downloaded JSON and use `npx` to run the `swagger-typescript-api` library. Version `12.0.3` was used at this time of writing. We don't want to generate a http client class (since we have our own) so use `no-client` just to get types.

   `npx swagger-typescript-api -p swagger.json -n acapyInterface.ts --no-client`
3. Add the resultant file to frontend/src/types/acapyApi

## Other interfaces/types/enums

For now add any other custom types just to the index.ts in this folder, as it expands we can consider if that should be structured differently.
