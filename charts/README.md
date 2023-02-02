## Important

These charts are for the traction development team to build and promote instances within their Openshift namespaces. If you are forking the repo, or following along, you can use these as a guide but these are not expected to work for everyone nor in every Kubernetes infrastructure.

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

#### Values.yaml

For each set of charts (tenant-ui, traction), there is a base values.yaml file with default production configuration. 

There are instance/deployment overrides for:
- Pull Requests (-pr). This goes to our dev namespace and is pre-merge to the develop branch.
- Development (-development). This goes to our dev namespace and is post-merge to the develop branch, pre-promotion to test.
- Test (-test). This goes to our test namespace and is pre-integration.
- Integration (-int). This goes to our test namespace and is pre-production.
- Production (-production). This goes to our production namespace. Production for us is not intended for client use; it is to prove out production scenarios before we deliver code to other interested business units to run their own instances.

In each of the above cases, we use the file overrides to make additional configuration required for each namespace and / or instance.


##### Tenant-UI

Tenant UI is a separate deliverable and has it's own CI/CD pipeline, however, the instances we stand up will point at matching traction deployments. Some of the configuration will require being in the same namespace to make "private" connections between the Tenant UI and Traction.

