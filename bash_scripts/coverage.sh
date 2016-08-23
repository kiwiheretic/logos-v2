#!/bin/bash

shopt -s globstar
# port is whatever port you want uwsgi to listen on.
# If needed, change to suit
port=8001

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
type coverage > /dev/null 2>&1  || { 
  echo "coverage not found - Is it installed in your virtual environment" ; 
  exit 1 
}

coverage_dir=`readlink -f $base_dir/../coverage/`
if [ ! -d $coverage_dir ]; then
    mkdir $coverage_dir
fi
files=$(find $coverage_dir -type f)
if [ -s "$files" ]; then
    rm $files
fi

( cd $base_dir  ; coverage erase ; \
coverage run --source=. manage.py test ; \
coverage html -d $coverage_dir )

