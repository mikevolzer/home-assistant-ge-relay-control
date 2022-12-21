#!/bin/bash
set -e
cd /home/pi/Development/light-control
. env/bin/activate
pip3 install -r requirements.txt
python main.py