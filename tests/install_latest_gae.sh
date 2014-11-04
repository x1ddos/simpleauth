#!/bin/bash
set -e

DOWNLOAD_URL=https://storage.googleapis.com/appengine-sdks/featured
VERSION_CHECK_URL=https://appengine.google.com/api/updatecheck
VERSION=$(echo $(curl -s ${VERSION_CHECK_URL}) | sed -E 's/release: \"(.+)\"(.*)/\1/g')

wget -c --no-verbose -O /tmp/appengine.zip $DOWNLOAD_URL/google_appengine_$VERSION.zip
unzip -q -o /tmp/appengine.zip -d /tmp

