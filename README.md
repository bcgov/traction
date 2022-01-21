# traction
Hyperledger Aries Traction - a digital wallet solution for organizations. This project space will be a rewrite of the Business Partner Agent with multitenancy, cloud native architecture and Open APIs.

### Charts
The charts in this repository are for deployments of pull requests. The charts for Continuous Deployment are located elsewhere but need to be updated if a PR makes changes (adds infrastructure, changes settings etc.).

Developers should lint the charts before committing and running.

#### Chart Linting
On your local machine run

```
docker run -it --rm --name ct --volume $(pwd):/data quay.io/helmpack/chart-testing sh -c "cd /data; ct lint --config ct.yaml"
```

To run changes to the charts without a PR, you can login to Openshift, edit values-pr.yaml if needed and run:

```
helm upgrade -f ./charts/traction/values.yaml -f ./charts/traction/values-pr.yaml pr-00-traction ./charts/traction --install --wait
```