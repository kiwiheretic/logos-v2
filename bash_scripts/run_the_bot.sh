#!/bin/bash

# params
# $1 - the path to the virtual enviroment top directory
# $2 - the name of the server to connect to

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

screen -d -m python $base_dir/manage.py run_bot -s $2/nick:logos/control:\#logos
