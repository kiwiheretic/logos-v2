#!/bin/bash

if [ -z $1 ]
then
    port=8001
else
    port=$1
fi

if [ -e "/tmp/logos_$port.pid" ]
then
    pid=`cat "/tmp/logos_$port.pid"`
    echo "Killing process $pid"
    kill -s sigint $pid
fi
