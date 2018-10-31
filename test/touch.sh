#/bin/bash

for i in `seq 1 100000`
do
	touch /mnt/$i
	cat /mnt/$i > /dev/null
done
