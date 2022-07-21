### to generate the base json file

see [client readme](../acapy_wrapper_074/README.md)


### edit the base json file

see [client readme](../acapy_wrapper_074/README.md)

### install and run the generator
This example is on a Mac with homebrew installed:

```shell
brew install openapi-generator
openapi-generator openapi-generator generate -i <path to edited swagger.json>  -g python-fastapi -o <path to output folder> --skip-validate-spec
```

### edit the output code until it works in traction

see [0.7.3 README](../acapy_wrapper/README.md) for more information about required changes to the generated code. You may want to look at the git history of that directory and this to see alterations done over time.
