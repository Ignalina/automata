#!/bin/bash


if [ ! -d "venv" ]; then
  python3 -m venv venv
  source venv/bin/activate
  pip install redfish
fi

  source venv/bin/activate

