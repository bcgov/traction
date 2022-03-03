# traction

Hyperledger Aries Traction - a digital wallet solution for organizations. This project space will be a rewrite of the Business Partner Agent with multitenancy, cloud native architecture and Open APIs.

Traction provides a service layer to manage Aries agent instances in a multi-tenant aca-py deployment, and provides some value-add services for using aca-py functions such as setting up issuer agents, and issuing and verifying credentials.  Future functionality could include machine-readable governance, etc.

## Running traction

[Scripts](./scripts/README.md)  

Docker Compose files for spinning up local instances of Traction and the Showcase application.  	

## Deploying Traction

[Charts](./charts/README.md) 
    
Helm charts for deploying Traction, Showcase and Endorser to Openshift.  

## Developing traction

[Architecture](./docs/ARCHITECTURE.md)

Overview of the traction architecture.

[Traction](./services/traction/README.md)  

Source code for Traction API.  

[Traction Showcase/Demo](./services/showcase/README.md)  

Source code for Endorser controller application.

[Endorser](./services/endorser/README.md)
