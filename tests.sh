#!bin/bash

error="\e[1;31m[ERROR]\e[0m"
execution="\e[0;36m[INFO]\e[0m"


echo -e "$execution Installing googleclient"
pip3 install .

echo -e "$execution Starting tests"
python -m unittest discover -v googleclient/tests
