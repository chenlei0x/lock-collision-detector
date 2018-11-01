#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import multiprocessing
import signal
import time
import os
import pdb

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


def create_file(file_name):
	file = open(file_name, "w+b")
	return file


def read_loops_sleep(file_list, loops, interval):
	for i in range(loops):
		for f in file_list:
			read_first_page(f)
			my_sleep(interval)

def write_loops_sleep(interval, loops, file_list):
	for i in range(loops):
		for f in file_list:
			write_first_page(f)
			my_sleep(interval)


def test(target):
	a_list = []
	b_list = []
	c_list = []
	for i in range(10):
		path = os.path.join(target, "a_{}".format(i))
		ret = create_file(path)
		write_first_page(ret)
		a_list.append(ret)

		path = os.path.join(target, "b_{}".format(i))
		ret = create_file(path)
		write_first_page(ret)
		b_list.append(ret)

		path = os.path.join(target, "c_{}".format(i))
		ret = create_file(path)
		write_first_page(ret)
		c_list.append(ret)

	read_loops(a_list, 500)
	return

	with multiprocessing.Pool(4) as pool:
		res_a = pool.apply_async(read_loops, [a_list, 5000])
		#res_c = pool.apply_async(read_loops, [c_list, 1000, 1])

		#res_a.get()
		res_a.get()
		print("will sleep")
		my_sleep(10)
target = '/mnt/ocfs2'
if __name__ == '__main__':
	test(target)
