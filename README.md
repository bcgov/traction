# traction [![Lifecycle:Maturing](https://img.shields.io/badge/Lifecycle-Maturing-007EC6)](<Redirect-URL>)
[![Maintainability](https://api.codeclimate.com/v1/badges/e6df50041dd4373c7e15/maintainability)](https://codeclimate.com/github/bcgov/traction/maintainability)

Hyperledger Aries Traction - a digital wallet solution for organizations. The focus of Traction is for line of businesses to easily integrate Aries ([aca-py](https://github.com/hyperledger/aries-cloudagent-python)) into their applications; without having to stand up, maintain and manage and instance of aca-py themselves.

Traction provides a series of Aca-Py plugins to manage Aries agent instances in a multi-tenant aca-py deployment, and provides some value-add services for the tenants and the administrator of Aca-Py.  Future functionality could include machine-readable governance, etc.

See [traction flow chart](docs/assets/traction-flow-chart-1600x900-12162022.pdf) for a simple architecture overview.

## Quick start

To run a local instance of traction, see the documentation in [scripts](./scripts/README.md).


## Deploying Traction

Helm charts for deploying Traction and Endorser to Openshift (BC Gov Traction team specific):

[Charts](./charts/README.md)


## Repository workflow
Currently authorized users can create a branch and run a pull request to merge in changes. Unauthorized can always create a fork.


### Rebasing of a branch
```bash
git fetch --all
git pull

git rebase origin/develop
git push --force
```

## Archive of Showcase
Earlier iterations of Traction had a Showcase application (use Traction API to facilitate Alice/Faber/Acme demo).

This has been removed as the API advances and other applications fill that role. A full working instance of Traction API and Showcase are in [tag v0.1.0](https://github.com/bcgov/traction/releases/tag/v0.1.0)

The v0.1.0 release has instructions and docker compose files for running Showcase.
Review [Scripts](https://github.com/bcgov/traction/blob/66565a3f6c01ddec241dc3b8db2bd99879bd7cf2/scripts/README.md). 

