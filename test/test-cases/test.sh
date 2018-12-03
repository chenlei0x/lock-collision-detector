#! /bin/bash

./main.py --remote -o test.log -n 10.67.162.128 \
	-n 10.67.162.212 -m 10.67.162.128:/mnt

./main.py --local -m /mnt
