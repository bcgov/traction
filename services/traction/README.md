```shell
pip install -r requirements.txt
gunicorn -k uvicorn.workers.UvicornWorker -b localhost:5000  api.main:app
```


```shell
pip install tox
tox -e lint
tox -e test
```