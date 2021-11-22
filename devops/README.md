Basing initial tekton pr pipeline on https://www.arthurkoziel.com/tutorial-tekton-triggers-with-github-integration

install tekton and oc clients

## install pipeline
Assume access and privileges to the openshift4 namespace... (f6b17d-tools).
This PR pipeline is in tools and sets up the deployment in tools.  
This needs to change to dev/test/prod when we get namespaces.

```
kubectl apply -f devops/tekton/
```

Need to set up the webhook for the traction-gh-listener (listens for pull requests!)  

This will use the route and service created by the event listener and the secret we created in 02-secret.yaml.

Webooks go to http://traction-gh-listener-tools.apps.silver.devops.gov.bc.ca/hooks.


## clean up commands - tekton

deleting task runs and pipeline runs will free up some pods that are created to run deployments.

### list all task runs

```
tkn tr ls
```

### delete all task runs

```
kubectl delete tr --all
```

### get last task run logs

```
tkn tr logs -f -a $(tkn tr ls | awk 'NR==2{print $1}')
```

### list all pipeline runs

```
tkn pr ls
```

### delete all pipeline runs

```
kubectl delete pr --all
```

## remove deployment
some commands if you want to remove a deployment and start fresh...

```
kubectl delete pr --all

cd devops/helm/charts
helm uninstall traction

oc delete secret traction-acapy
oc delete pvc data-traction-postgresql-0

