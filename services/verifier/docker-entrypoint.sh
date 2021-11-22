#!/bin/bash
python3 -m flask db upgrade
if [ $? == 0 ]; then
    python3 -m flask run --host=0.0.0.0
fi
echo 'Alembic db upgrade failed...'
exit 1