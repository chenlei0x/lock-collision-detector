#! /bin/bash

O2TOP="../../bin/o2top"

if [ $1 == '-l' ]
then
	$O2TOP --local -m /mnt
else
	$O2TOP --remote -o test.log -n 10.67.162.128 \
		-n 10.67.162.212 -m 10.67.162.128:/mnt
fi
