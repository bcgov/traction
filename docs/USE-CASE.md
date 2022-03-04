# Running the tractino demo

## Running traction using swagger

Start up the traction services as follows - open up a bash shell and run the following:

```bash
git clone https://github.com/bcgov.traction.git
cd traction/scripts
cp .env-example .env
docker-compose build
docker-compose up
```

### As innkeeper, authenticate with the swagger interface

### As innkeeper, create a new tenant

### As innkeeper, make the tenant an issuer

### As tenant, authenticate with the swagger interface

### As tenant, complete the issuer update

### As tenant, create a schema and credential definition

### As innkeeper, create a second tenant

### As the second tenant, authenticate with the swagger interface

### As first tenant, create a connection invitation

### As second tenant, accept the connection invitation

### As first tenant, issue a credential (create an offer)

### As second tenant, accept the credential offer

### As second tenant, view the received credential

### TBD proof exchange flow


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
