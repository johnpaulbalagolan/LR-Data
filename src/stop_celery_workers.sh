#!/bin/sh

WORKERS=3

if [ -f .celery_workers ]; then
    WORKERS=`cat .celery_workers`
fi

celeryd-multi stop $WORKERS

rm -f .celery_workers

