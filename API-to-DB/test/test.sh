#!/bin/bash

cd  `find /home/ -name twitter_imgs -type d`
cd API-to-DB
. twitter_imgs_vpython/bin/activate

python3 test.py