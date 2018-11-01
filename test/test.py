#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import multiprocessing
import signal
import time
import os

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
	buf = bytes("0" * length)
	ret = file.write(buf)
	file.seek(0)

def read_loops(file, loop):
	file.seek(0)
	for i in range(loops):
		ret = file.read(4096)
		assert(ret >= 0)
		file.seek(0)

def write_loops(file, loop):
	length = 4096
	buf = bytes("0" * length)
	file.seek(0)
	for i in range(loops):
		ret = file.write(buf)
		file.seek(0)


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


def test(path):
	os.path.join(path, )
	a_list = []
	b_list = []
	c_list = []
	for i in range(10):
		path = os.path.join(path, "a_{}".format(i))
		ret = create_file(path)
		a_list.append(ret)

		path = os.path.join(path, "b_{}".format(i))
		ret = create_file(path)
		b_list.append(ret)

		path = os.path.join(path, "c_{}".format(i))
		ret = create_file(path)
		c_list.append(ret)


	pool = multiprocessing.Pool(4)
	pool.apply_async(read_loops, [a_list, 5000, 1])
	pool.apply_async(read_loops, [b_list, 2000, 1])
	pool.apply_async(read_loops, [c_list, 1000, 1])


if __name__ == '__main__':
	test(path)
