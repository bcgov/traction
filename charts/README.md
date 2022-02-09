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