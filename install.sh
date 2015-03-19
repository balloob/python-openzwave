#!/bin/bash -e

if [ "$1" == "--python3" ]; then
  PYEX=python3
else
  PYEX=python
fi

echo "-----------------------------------------------------------------"
echo "|   Uninstall python-openzwave                                  |"
echo "-----------------------------------------------------------------"
set +e
./uninstall.sh
set -e

echo "-----------------------------------------------------------------"
echo "|   Install python-openzwave  lib                               |"
echo "-----------------------------------------------------------------"
$PYEX setup-lib.py install --record install.files

echo "-----------------------------------------------------------------"
echo "|   Install python-openzwave  api                               |"
echo "-----------------------------------------------------------------"
$PYEX setup-api.py install --record install.tmp
cat install.tmp >>install.files
rm install.tmp
rm -Rf python_openzwave_lib.egg-info >/dev/null 2>&1
rm -Rf python_openzwave_api.egg-info >/dev/null 2>&1

echo "-----------------------------------------------------------------"
echo "|   Installation done                                           |"
echo "|   You can unistall python-openzwave using :                   |"
echo "|   sudo ./uninstall.sh                                         |"
echo "-----------------------------------------------------------------"
