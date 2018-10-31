#!/usr/bin/env python3
#-*- coding: utf-8 -*-

def read_first_page(file):
	ret = file.read(4096)
	assert(ret >= 0)
	file.seek(0)

def write_first_page(file):
	buf = bytes("0" * length)
	ret = file.write(buf)
	file.seek(0)

def read_loops(file, loop):
	for i in range(loops):
		ret = file.read(4096)
		assert(ret >= 0)
		file.seek(0)

def write_loops(file, loop):
	length = 4096
	buf = bytes("0" * length)
	for i in range(loops):
		ret = file.write(buf)
		file.seek(0)


def create_file(file_name):
	file = open(file_name, "w+b")
	return file


def read_loops_sleep(interval, file_list):
	while True:
		for f in file_list:
			read(f)
			sleep(interval)

def write_loops_sleep(interval, file_list):
	while True:
		for f in file_list:
			write_first_page

def test(file_name):
	a_list = []
	b_list = []
	c_list = []
	for i in range(100):
		ret = create_file("a_{}".format(i))
		a_list.append(ret)

		ret = create_file("b_{}".format(i))
		b_list.append(ret)

		ret = create_file("c_{}".format(i))
		c_list.append(ret)

	while True:

