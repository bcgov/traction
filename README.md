# Traction 

![Traction Logo](./docs/assets/readme-logo.png)

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE) [![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Maturing-007EC6)](<Redirect-URL>) [![Maintainability](https://api.codeclimate.com/v1/badges/e6df50041dd4373c7e15/maintainability)](https://codeclimate.com/github/bcgov/traction/maintainability) 


## Table of Contents 

- [What is Traction?](#what-is-traction)
- [Start using Traction](#start-using-traction)
- [What are the benefits of using Traction?](#what-are-the-benefits-of-using-traction)
- [What is Traction comprised of?](#what-is-traction-comprised-of)
- [Start contributing to Traction](#start-contributing-to-traction)
- [Who is maintaining Tracion?](#who-is-maintaining-traction)
- [How is Traction licenced?](#how-is-traction-licensed)
- [Engage with the community](#engage-with-the-community)



## What is Traction? 

Traction is a digital wallet solution comprised of plugins layered on top of Hyperledger Aries Cloud Agent Python (ACA-Py) and streamlines the process of sending and receiving digital credentials for governments and organizations.  

Its open-source foundation makes it easy to integrate digital trust technology into existing lines of business applications, without having to stand up, maintain and manage an instance of ACA-Py themselves. Future functionality could include machine-readable governance and more. 

![Arch Diagram](./docs/assets/traction-flow-chart-1600x900-12162022-01.jpg)

## Start using Traction 

**Running Traction**: to run a local instance of traction, see the documentation in [scripts](./scripts/README.md). 

**Deploying Traction**: Helm charts for deploying Traction and Endorser to Openshift (BC Gov Traction team specific): [charts](./charts/README.md). 


## What are the benefits of using Traction? 

Traction makes it easier to integrate digital trust technology into existing line of business applications. 

- **API-first Architecture**: Traction is designed with an API-first architecture, this RESTful API allows for integration into existing line-of-business applications already being used by organizations, the Tenant user interface is built on this API to enable adoption prior to integration and for low-use functions. 
- **Enhanced Interoperability**: Hyperledger Aries makes Traction more broadly compatible with existing technologies used by governments and organizations around the world. 
- **Multi-tenancy**: Rather than having multiple digital tools to integrate with organizations, one scalable instance of Traction can be used to participate in the digital trust ecosystem, control all connections, and more easily share data. 
- **Higher Scalability**: Traction is open-source technology, encouraging collaborative refinement, faster release, and higher scalability. 


## What is Traction comprised of? 

- [ACA-Py + plugins](./plugins/README.md) 
- [Tenant UI](./services/tenant-ui/README.md) 
- [Endorser Services](./services/endorser/README.md) 


## Start contributing to Traction 

Traction is an open-source technology project that welcomes collaboration.  

If you would like to contribute to Traction, please review the following: 

- [Contributing](./CONTRIBUTING.md)  
- [Code of Conduct](./CODE_OF_CONDUCT.md) 
- [Compliance](./COMPLIANCE.yaml) 

### Repository workflow
Currently authorized users can create a branch and run a pull request to merge in changes. Unauthorized can always create a fork.


#### Rebasing of a branch
```bash
git fetch --all
git pull

git rebase origin/develop
git push --force
```

## Who is maintaining Traction? 
[The Province of British Columbia](https://github.com/bcgov/) is maintaining Traction as an open-source project.

Maintainer(s): 
- Jason Sherman
- Jason Syrotuck
- Lucas O'Neil
- Jamie Popkin

## How is Traction licensed? 

Traction is licensed under Apache License 2.0 which can be reviewed [here](./LICENSE). 


## Engage with the community 

Connect with others
- on Discord: [EMDT Public Discord Channel](https://discord.com/channels/766403442599657522/854432442382680104) 
- for Aries discussion see the Hyperlerger Aries Github [participation section](https://github.com/hyperledger/aries#project-participation)
