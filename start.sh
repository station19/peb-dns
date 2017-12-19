#!/bin/sh

export FLASK_APP=${PWD}/app.py
export FLASK_DEBUG=0
PORT=$1

if [ ! -d migrations ];then
    flask db init
    flask db migrate
    flask db upgrade
fi

gunicorn -w 4 app:app -b 0.0.0.0:${PORT} \
        --log-level=debug \
        --access-logfile logs/peb_dns_access.log \
        --error-logfile logs/peb_dns_error.log \
        --log-file logs/peb_dns.log
