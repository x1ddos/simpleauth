#!/bin/bash

# the app will be accessible at http://$BIND_IP:$BIND_PORT
BIND_IP="0.0.0.0"

# TCP/IP port on which the app will be accessible
BIND_PORT="8080"

# Directory where the whole thing resides.
# $DIR will point to the application root. 
DIR=`dirname $0`

# create tmp dir if didn't exist
mkdir -p $DIR/tmp/blobs

python2.7 `which dev_appserver.py` \
  --address=$BIND_IP \
  --port=$BIND_PORT \
  --high_replication \
  --use_sqlite \
  --require_indexes \
  --datastore_path=$DIR/tmp/dev.sqlite3 \
  --blobstore_path=$DIR/tmp/blobs \
  $@ $DIR
