# Running the traction demo

## Running traction using swagger

Start up the traction services as follows - open up a bash shell and run the following:

```bash
git clone https://github.com/bcgov.traction.git
cd traction/scripts
cp .env-example .env
docker-compose build
docker-compose up
```

### Setting up a new Issuer tenant

- As innkeeper, authenticate with the swagger interface
- As innkeeper, create a new tenant
- As innkeeper, make the tenant an issuer
- As tenant, authenticate with the swagger interface
- As tenant, complete the issuer update

[Watch it here!](./assets/traction-new-tenant-issuer.mp4)

### Adding a new Schema/Credential Definition for an Issuer

- As tenant, create a schema and credential definition

[Watch it here!](./assets/traction-issuer-create-schema.mp4)

### Connect two tenants

- As innkeeper, create a second tenant
- As the second tenant, authenticate with the swagger interface
- As first tenant, create a connection invitation
- As second tenant, accept the connection invitation

[Watch it here!](./assets/traction-connect-two-tenants.mp4)

### Issue (and Accept) a Credential

- As first tenant, issue a credential (create an offer)
- As second tenant, accept the credential offer
- As second tenant, view the received credential

[Watch it here!](./assets/traction-issue-credential.mp4)

### Request (and Provide) a Credential Presentation

- As first tenant, create and send a presentation request
- As second tenant, determine which credentials to present
- As second tenant, present the selected credentials
- As first tenant, cerify the provided presentation

[Watch it here!](./assets/traction-presentation-request.mp4)


## Running the "showcase" demo

Run the traction services as described above, and then in a new bash shell run the following:

```bash
cd traction/scripts
docker-compose -f docker-compose.showcase.yml build
docker-compose -f docker-compose.showcase.yml up
```

### Create a "sandbox" (set of traction tenants)

### As faber, issue invitation to alice

### As alice, accept connection

### As faber, issue a credential to alice

### As alice, accept the issued credential

### As alice, request to connect to acme

### As acme, accept connection from alice

### As acme, request proof of education from alice

### As alice, provide proof of education to acme

### As acme, verify proof of education from alice
