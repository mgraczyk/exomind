#!/bin/bash
python_version="$(python3 -V 2>&1)"
required_python_version='Python 3.(6|7|8|9).\d'

if ! (echo $python_version | egrep "$required_python_version" >/dev/null); then
  echo "Incorrect python version: You have $python_version, you need $required_python_version"
else
  test -d .venv/ || python3 -m venv .venv
  source .venv/bin/activate

  python -m pip install --upgrade pip
  PYCURL_SSL_LIBRARY=openssl python -m pip install -r requirements.txt
  export PYTHONPATH=$(pwd)
  test -f .env && source .env
fi
