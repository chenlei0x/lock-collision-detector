#!/usr/bin/env python
#-*- coding: utf-8 -*-

import multiprocessing
import signal
import time
import os
import pdb
import shell

def my_sleep(interval):
	"""
	:rtype: None
	"""
	return time.sleep(interval)

def read_first_page(file):
	ret = file.read(4096)
	assert(ret >= 0)
	file.seek(0)

def write_first_page(file):
	file.seek(0)
	length = 4096
	buf = "0" * length
	ret = file.write(buf.encode())
	file.seek(0)

def read_loops(file, loops):
	for i in range(loops):
		for f in file:
			print("read_loops")
			f.seek(0)
			ret = f.read(4096)

def write_loops(file, loop):
	length = 4096
	buf = bytes("0" * length)
	file.seek(0)
	for i in range(loops):
		for f in file:
			f.seek(0)
		ret = f.write(buf)
		f.seek(0)


def touch(file_name, directory=None):
	path = os.path.join(directory, file_name)
	cmd = "touch {0}".format(path)
	shell.shell(cmd)

def cat(file_name, directory=None):
	path = os.path.join(directory, file_name)
	cmd = "cat {0} > /dev/null 2>&1".format(path)
	shell.shell(cmd)

def dd(file_name, size, directory=None):
	path = os.path.join(directory, file_name)
	cmd = "dd if=/dev/zero of={0} bs=4K count=1".format(path)
	shell.shell(cmd)

def echo_append(file_name, directory=None):
	path = os.path.join(directory, file_name)
	cmd = "echo aaaaaaa >> {0}".format(path)
	shell.shell(cmd)

def test(mp, loops=1000):
	file_access_high = "high"
	file_access_mid = "mid"
	file_access_low = "low"

	dd(file_access_high, "4k", mp)
	dd(file_access_low, "4k", mp)
	dd(file_access_mid, "4k", mp)

	for i in range(loops):
		factor = i % 10
		if factor >= 4:
			target = file_access_high
		elif factor >= 1:
			target = file_access_mid
		else:
			target = file_access_low

		if factor % 2 == 0:
			print("[{0}]: cat".format(target))
			cat(target, mp)
		else:
			print("[{0}]: dd".format(target))
			dd(target, "4k", mp)
		my_sleep(1)


if __name__ == '__main__':
	test("/mnt")
