#!/bin/bash

pushd ./doc/
export PYTHONPATH=$PYTHONPATH:..
export DJANGO_SETTINGS_MODULE=spaciblo.settings
epydoc -v --config epydoc.config
export RD=`pwd`
echo "file://$RD/apidocs/spaciblo-module.html"
popd 