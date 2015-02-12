#!/bin/sh
#
# Copy this script to ../.git/hooks/ and rename to just
# 'pre-commit' (no extension)

echo "*** pre commit***"
string="$(uname -s)"
if [ "${string#*'MINGW32_NT'}" != "$string" ]
then
  echo "Windows!";
  /c/python27/python.exe `pwd`/git-hooks/pre-commit.py 
fi
#
#exit 0