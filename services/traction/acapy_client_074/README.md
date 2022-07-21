### to generate the base json file

1. deploy an agent running version of acapy code you want to generate
2. go to the acapy admin url api docs (ex. https://traction-acapy-admin-dev.apps.silver.devops.gov.bc.ca/api/doc)
3. download the swagger json (ex. https://traction-acapy-admin-dev.apps.silver.devops.gov.bc.ca/api/docs/swagger.json)


### edit the base json file

There are some regex fields that will not pass the generator, simply remove them.

For example, these were removed from 0.7.4:
1. "pattern": "[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-4[a-fA-F0-9]{3}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}",
2. "pattern": "^{.*}$",
3. "pattern": "^{\\s*\".*?\"\\s*:\\s*{.*?}\\s*(,\\s*\".*?\"\\s*:\\s*{.*?}\\s*)*\\s*}$",

### install and run the generator
This example is on a Mac with homebrew installed:

```shell
brew install openapi-generator
openapi-generator generate -i <path to edited swagger.json>  -g python -o <path to output folder> --skip-validate-spec
```

### edit the output code until it works in traction

see [0.7.3 README](../acapy_client/README.md) for more information about required changes to the generated code. You may want to look at the git history of that directory and this to see alterations done over time.
