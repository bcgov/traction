### Charts
Developers should lint the charts before committing and running.

#### Chart Linting
On your local machine run (at root of the repository)

```
docker run -it --rm --name ct --volume $(pwd):/data quay.io/helmpack/chart-testing sh -c "cd /data; ct lint --config ct.yaml"
```

To run changes to the charts without a PR, you can login to Openshift, edit values-pr.yaml if needed and run (add a `--dry-run` flag for testing compilation of charts):

```
helm upgrade -f ./charts/traction/values.yaml -f ./charts/traction/values-pr.yaml pr-00-traction ./charts/traction --install --wait
```

### Openshift Resources
We have 3 Openshift namespaces (dev, test, prod), each with a limit on resources. We have a 4th namespace (tools) with smaller limits (cpu: 4 cores -> 4000m).

limits.cpu = 8 cores -> 8000m
limits.mem = 32Gi -> 32609Mi

requests.cpu = 4 cores -> 4000m
requests.cpu = 16Gi -> 16304Mi

Note: tools namespace has reduced limits on cpu:

limits.cpu = 4 cores -> 4000m

requests.cpu = 2 cores -> 2000m

Currently, each instance has 3 containers (traction api & traction acapy & traction db). We are using the dev namespace for a DEV instance plus our Pull Request Instances (4 developers, so hopefully only 4 PRs open at a time). This puts cosiderable limitations on the resources we can request and our limits. We are leaving extra space for standing up tenant-ui on demand.

For test and prod namespaces, we can assume that we will need 2 instances (test + uat), (prod + hotfix).  

For now, just keeping it simple by giving all containers similar requests and limits, this must be adjusted as we determine actual load and run requirements for each container.  

#### PR instances limits and requests

Take the dev namespace limits divide by 6, then use a fudge factor of around 75% of max. The DEV instance (pre-test) will get double the resources than PRs that is why 6 instead of 5 (1 dev + 4 prs).  

limits.cpu = 200m
limits.mem = 820Mi

requests.cpu = 120m
requests.cpu = 400Mi

#### DEV instance limits and requests

See above, basically use double what a PR gets  

limits.cpu = 400m
limits.mem = 1600Mi

requests.cpu = 200m
requests.cpu = 820Mi


#### TEST/PROD instance limits and requests

TEST and PROD, expect 2 full instances then use a fudge factor of around 75% of max; give a little breathing room.

limits.cpu = 600m
limits.mem = 2600Mi

requests.cpu = 300m
requests.cpu = 1300Mi