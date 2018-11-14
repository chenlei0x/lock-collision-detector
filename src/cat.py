#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import util


def gen_cat(which, lock_space, *args):
	if which == 'local':
		return LocalCat(lock_space)
	elif which == 'ssh':
		return SshCat(lock_space, *args)


class Cat:
	def __init__(self, lock_space):
		self._lock_space = lock_space

	def get():
		pass

class LocalCat(Cat):
	def  __init__(self, lock_space):
		super().__init__(lock_space)

	def get(self):
		return util.get_one_cat(self.lock_space, None)

class SshCat(Cat):
	def __init__(self, lock_space, node_name):
		self._node_name = node_name
		super().__init__(lock_space)

	def get(self):
		return util.get_one_cat(self._lock_space, self._node_name)
