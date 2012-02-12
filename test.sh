#!/bin/bash
#
# to run continuous tests, run this file with:
#   test.sh auto
# - it'll start nosy if app/tests/nosy.cfg is present, otherwise tdaemon.
#
# You'll need either nosy or tdaemon. See more on required packages 
# for automatic testing at
# http://alex.cloudware.it/2012/02/gae-automated-python-testing-with-nose.html

# Base directory
DIR=`dirname $0`

pushd .
cd $DIR

# run all the tests or watch for file system changes.

if [ "$1" == "auto" ]; then
  if [ -f tests/nosy.cfg ]; then
    nosy -c tests/nosy.cfg
  else
    # tdaemon --custom-args="--with-snort --with-gae --without-sandbox --logging-filter=-root"
    tdaemon --custom-args="--with-snort --without-sandbox --logging-filter=-root"
  fi
else
  # nosetests --with-gae --without-sandbox --logging-filter=-root $@
  nosetests --without-sandbox --logging-filter=-root $@
fi

popd
