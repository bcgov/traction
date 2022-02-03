#!/bin/bash
exec gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:5000 --log-level INFO api.main:app
