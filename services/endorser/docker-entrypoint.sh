#!/bin/bash
# python3 -m alembic upgrade head
# if [ $? == 0 ]; then
    exec uvicorn api.main:app --host 0.0.0.0 --port $ENDORSER_API_PORT --log-level error
# fi
# echo 'Alembic db upgrade failed...'
# exit 1
