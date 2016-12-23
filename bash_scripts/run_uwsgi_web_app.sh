#!/bin/bash

# port is whatever port you want uwsgi to listen on.
# possibly changed by -p option
port=8001

while getopts "p:" opt; do
  case $opt in
    p)
      echo "port set to $OPTARG" >&2
      port=$OPTARG
      ;;
    \?)
      echo "Invalid option: -$opt" >&2
      ;;
  esac
done

# shift the command line arguments so positional arguments start at $1
shift $((OPTIND-1))


# following function based on
# http://stackoverflow.com/questions/13767252/ubuntu-bash-script-how-to-split-path-by-last-slash
function get_dir_part {
    p=$1
    [[ "$p" == */* ]] || p="./$p"
    echo "${p%/*}"
}

if [ "$1" ]
then
    if [ -e "$1/bin/activate" ]
    then
        source "$1/bin/activate"
    else
        echo "This is not a valid virtualenv - could not locate <path>/bin/activate"
        exit 1
    fi
else
    echo "path to virtual enviroment should be first parameter to script"
    exit 1
fi

# get base directory of real path of this script
# real path uses readlink
# see http://stackoverflow.com/questions/284662/how-do-you-normalize-a-file-path-in-bash
base_dir=$(get_dir_part $(get_dir_part $(readlink -m $0)))
type uwsgi > /dev/null 2>&1  || { 
  echo "uwsgi not found - Is it installed in your virtual environment" ; 
  exit 1 
}

if [ ! -e "$base_dir/logs" ]
then
    mkdir "$base_dir/logs"
fi

if [ -e "/tmp/logos_$port.pid" ]
then
    rm "/tmp/logos_$port.pid"
fi

uwsgi --chdir=$base_dir \
    --module=logos.wsgi:application \
    --env DJANGO_SETTINGS_MODULE=logos.settings \
    --master --pidfile="/tmp/logos_$port.pid" \
    --socket=127.0.0.1:$port \
    --processes=1 \
    --static-map /static="$base_dir/assets" \
    --chmod-socket=666 \
    --harakiri=20 \
    --max-requests=5000 \
    --vacuum \
    --daemonize="$base_dir/logs/logos.$$.log" # background the process

