#!/bin/bash
APPNAME=evmts
APPDIR=${PWD}

LOGFILE=$APPDIR'/logs/gunicorn.log'
ERRORFILE=$APPDIR'/logs/gunicorn-error.log'

NUM_WORKERS=3

ADDRESS=127.0.0.1:8080

cd $APPDIR


exec gunicorn $APPNAME.wsgi:application \
-w $NUM_WORKERS --bind=$ADDRESS \
--log-level=debug \
--log-file=$LOGFILE 2>>$LOGFILE  1>>$ERRORFILE &