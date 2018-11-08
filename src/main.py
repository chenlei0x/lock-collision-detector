#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import OrderedDict
import util
import ipdb as pdb
from multiprocessing.dummy import Pool as ThreadPool

# cat  -----  output of one time execution of "cat locking_stat"
				# one cat contains multiple OneShot(es)
# OneShot -----  lockinfo for one lockres at one time of cat
# Lock   ---- a list of OneShot for a typical lockres
# Node --- LockSpace on one node, which contains multiple Lock(s)
# LockSpace ---- A Lock should only belongs to one LockSpace
#

LOCK_LEVEL_PR = 0
LOCK_LEVEL_EX = 1

class Cat:
	def __init__(self, lock_space, node_name):
		self.lock_space = lock_space
		self._node_name = node_name

	def get(self):
		return util.get_one_cat(self.lock_space, self._node_name)

class LockName:
	"""
	M    000000 0000000000000005        6434f530
	type  PAD   blockno(hex)			generation(hex)
	[0:1][1:1+6][1+6:1+6+16]			[1+6+16:]
	"""

	def __init__(self, lock_name):
		self._name = lock_name

	@property
	def lock_type(self):
		lock_name = self._name
		return lock_name[0]

	@property
	def inode_num(self):
		start, end = 7, 7+16
		lock_name = self._name
		return int(lock_name[start : end], 16)

	@property
	def generation(self):
		return self._name[-8:]

	@property
	def short_name(self):
		return " ".join([self.lock_type, str(self.inode_num), self.generation])

	def __str__(self):
		return self._name

	def __eq__(self, other):
		return self._name == other._name

	def __hash__(self):
		return hash(self._name)

class OneShot:
	debug_format_v3 = OrderedDict([
		("debug_ver", 1),
		("name", 1),
		("l_level", 1),
		("l_flags", 1),
		("l_action", 1),
		("l_unlock_action", 1),
		("l_ro_holders", 1),
		("l_ex_holders", 1),
		("l_requested", 1),
		("l_blocking", 1),
		("lvb_64B", 64),
		("lock_num_prmode", 1),
		("lock_num_exmode", 1),
		("lock_num_prmode_failed", 1),
		("lock_num_exmode_failed", 1),
		("lock_total_prmode", 1),
		("lock_total_exmode", 1),
		("lock_max_prmode", 1),
		("lock_max_exmode", 1),
		("lock_refresh", 1),
	])

	def __init__(self, source_str, time_stamp):
		self.source = source_str.strip()
		self.time_stamp = time_stamp
		strings = source_str.strip().split()
		assert(int(strings[0].lstrip("0x")) == 3)
		i = 0
		for k, v in OneShot.debug_format_v3.items():
			var_name = k
			var_len = v
			value = "".join(strings[i: i + var_len])
			setattr(self, var_name, value)
			i += var_len
		self.name = LockName(self.name)

	def __str__(self):
		ret = []
		for k in OneShot.debug_format_v3.keys():
			v = getattr(self, k)
			ret.append("{} : {}".format(k, v))
		return "\n".join(ret)

	def legal(self):
		if 0 == self.name.inode_num:
			return False
		return True

	@property
	def inode_num(self):
		return self.name.inode_num

	@property
	def inode_type(self):
		return self.name.inode_type

class Lock():
	def __init__(self, lock_space):
		self._lock_space = lock_space
		self._shots= []

	def get_line(self, data_field, delta=False):
		data_list = [int(getattr(i, data_field)) for i in self._shots]
		if delta and len(data_list) >= 2:
			ret = [data_list[i] - data_list[i-1] for i in \
				range(1, len(data_list))]
		else:
			ret = data_list
		return ret

	def get_data_indexed(self, data_field, index = -1):
		try:
			ret =getattr(self._shots[index], data_field)
		except:
			return None
		else:
			return ret

	def get_latest_delta(self, data_field):
		a = self.get_latest_index(data_field, -1)
		b = self.get_latest_index(data_field, -1)
		if a and b:
			return a - b
		return None

	def name(self):
		return getattr(self, "_name", None)

	def append(self, shot):
		if not hasattr(self, "_name"):
			self._name = shot.name
		else:
			assert(self._name == shot.name)
		self._shots.append(shot)

	@property
	def node(self):
		return self._lock_space

	@property
	def lock_space(self):
		return self._lock_space

	@property
	def inode_num(self):
		if not hasattr(self, "_name"):
			return None
		return self._name.inode_num

	@property
	def lock_type(self):
		if not hasattr(self, "_name"):
			return None
		return self._name.lock_type
	"""
	@property
	def file_path(self):
		mps = self._lock_space.get_mount_point()
		if len(mps) == 0:
			return None
		mp = mps[0]
		inode_num = self.inode_num
		return util.get_lsof(mp, inode_num)
	"""

class LockSet():
	def __init__(self, lock_list):
		self._lock_list = lock_list
		if len(lock_list) == 0:
			return
		name = self._lock_list[0].name
		for i in self._lock_list:
			assert(i.name == name)

		self._name = lock_list[0].name

	def get_delta_cluster_scale(self, lock_type):
		lambda _sum x,y: x + y
		sum_list = []


		if lock_type = LOCK_LEVEL_PR:
			total_time_field = "lock_total_prmode"
			total_num_field =  "lock_num_prmode"

		if lock_type = LOCK_LEVEL_EX:
			total_time_field = "lock_total_exmode"
			total_num_field = "lock_num_exmode"

		for i in self._lock_list:
			d = i.get_latest_delta()
			sum_list.append(d)

		return

	def lock_name:
		return self._name



class Node:
	def __init__(self, lock_space, node_name=None):
		self.lock_space = lock_space
		self._locks = {}
		self.major, self.minor, self.mount_point = \
			util.lockspace_to_device(lock_space, node_name)
		self._node_name = node_name

	@property
	def node_name(self):
		return self._node_name

	def __str__(self):
		ret = "lock space: {}\n mount point: {}".format(
			self.lock_space, self.mount_point)
		return ret

	def process_one_shot(self, s, time_stamp):
		shot  = OneShot(s, time_stamp)
		if not shot.legal():
			return
		shot_name = shot.name
		if shot_name not in self._locks:
			self._locks[shot_name] = Lock(self)
		train = self._locks[shot_name]
		train.append(shot)

	def run_once(self, time_stamp=None):
		cat = Cat(self.lock_space, self._node_name)
		raw_shot_strs = cat.get()
		if time_stamp is None:
			time_stamp = util.now()
		for i in raw_shot_strs:
			self.process_one_shot(i, time_stamp)

	def run(self, loops=5, interval=2):
		#pdb.set_trace()
		for i in range(loops):
			print(self.node_name, "running")
			self.run_once()
			util.sleep(interval)

	def __contains__(self, item):
		return item in self._locks

	def __getitem__(self, key):
		return self._locks.get(key, None)

	"""
	def get_lock(self, lock_name):
		if lock_name not in self:
			return None
		return self._locks[lock_name]

	def get_mount_point(self):
		return self.mount_point
	"""

	def get_lock_names(self):
		return self._locks.keys()

class LockSpace:
	"One lock space on multiple node"
	def __init__(self, node_name_list, lock_space):
		#pdb.set_trace()
		self.lock_space = lock_space
		self._nodes = {} #node_list[i] : Node
		for node in node_name_list:
			self._nodes[node] = Node(lock_space, node)

	def run(self):
		#pdb.set_trace()
		pool = ThreadPool(10)
		for node_name, node in self._nodes.items():
			#lon.run()
			pool.apply_async(node.run)
		pool.close()
		pool.join()

	@property
	def node_name_list(self):
		return self._nodes.keys()

	@property
	def node_list(self):
		return self._nodes.values()

	def __getitem__(self, key):
		return self._nodes.get(key, None)

	def name_to_locks(self, lock_name):
		lock_on_cluster = []
		for node in self.node_list:
			lock = node[lock_name]
			if lock is not None:
				lock_on_cluster.append(lock)
		return lock_on_cluster

	def get_all_lock_names(self):
		ret = set()
		for node in self.node_list:
			for name in node.get_lock_names():
				ret.add(name)
		ret = list(ret)
		return ret

	def report_once(self):
		lock_names = self.get_all_lock_names()
		sort_list = []
		for lock_name in lock_names:
			locks = lock_space.name_to_locks(lock_name)
			for l in locks:
				lock_space_on_node = l.lock_space
				node_name = lock_space_on_node.node_name
				pr_total = l.get_line("lock_total_prmode")
				pr_total_diff = l.get_line("lock_total_prmode", True)

				title_printed = 0
				if pr_total[-1] - pr_total[0] > 5:
					print("[{}] [{}]".format(node_name, lock_name.short_name))
					title_printed = 1
					print("pr total ", pr_total)
					print("pr total diff", pr_total_diff)

				ex_total = l.get_line("lock_total_exmode")
				ex_total_diff = l.get_line("lock_total_exmode", True)

				if ex_total[-1] - ex_total[0] > 5:
					if title_printed:
						print("[{}] [{}]".format(node_name, lock_name.short_name))
					print("ex total", ex_total)
					print("ex total diff", ex_total_diff)
			title_printed = 1
			print("============")

nodes = ["10.67.162.62", "10.67.162.52"]
import threading
def main():
	lock_spaces = util.get_dlm_lockspaces(nodes[0])
	target = lock_spaces[0]

	lock_space = LockSpace(nodes, target)
	lock_space.run()


if __name__ == "__main__":
	main()
