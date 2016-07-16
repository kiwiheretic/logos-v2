#!/bin/bash
# $1 = path to virtual environment
# $2- = parameters to manage.py script

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

# ${@:2} - all parameters expanded from the second one (excluding the first)
# http://stackoverflow.com/questions/9057387/process-all-arguments-except-the-first-one
# see also http://wiki.bash-hackers.org/scripting/posparams#range_of_positional_parameters
python $base_dir/manage.py ${@:2}
