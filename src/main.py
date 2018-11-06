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
# LockSpaceOneNode --- LockSpace on one node, which contains multiple Lock(s)
# LockSpace ---- A Lock should only belongs to one LockSpace
#

debug_info_v2 = []

class Cat:
	def __init__(self, lock_space, node_ip):
		self.lock_space = lock_space
		self._node_ip = node_ip

	def get(self):
		return util.get_one_cat(self.lock_space, self._node_ip)

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

	def __str__(self):
		return self._name

	def __eq__(self, other):
		return other._name == self._name and other.generation == self.generation

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

	def get_line(self, data_type, delta=False):
		data_list = [int(getattr(i, data_type)) for i in self._shots]
		if delta and len(data_list) >= 2:
			ret = [data_list[i] - data_list[i-1] for i in \
				range(1, len(data_list))]
		else:
			ret = data_list
		return ret

	def get_lock_name_line(self, index_name):
		ret = [i.getattr(index_name) for i in _shots]
		return ret

	def append(self, shot):
		if not hasattr(self, "_name"):
			self._name = shot.name
		else:
			assert(self._name == shot.name)
		self._shots.append(shot)


	@property
	def lock_space(self):
		return self._lock_space

	@property
	def file_path(self):
		mps = self._lock_space.get_mount_point()
		if len(mps) == 0:
			return None
		mp = mps[0]
		inode_num = self.inode_num
		return util.get_lsof(mp, inode_num)

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



class LockSpaceOneNode:
	def __init__(self, lock_space, node_ip=None):
		self.lock_space = lock_space
		self._locks = {}
		self.major, self.minor, self.mount_point = \
			util.lockspace_to_device(lock_space, node_ip)
		self._node_ip = node_ip

	@property
	def node_ip(self):
		return self._node_ip

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
		cat = Cat(self.lock_space, self._node_ip)
		raw_shot_strs = cat.get()
		if time_stamp is None:
			time_stamp = util.now()
		for i in raw_shot_strs:
			self.process_one_shot(i, time_stamp)

	def run(self, loops=5, interval=3):
		#pdb.set_trace()
		for i in range(loops):
			self.run_once()
			util.sleep(interval)

	def __contains__(self, item):
		return item in self._locks

	def get_lock(self, lock_name):
		if lock_name not in self:
			return None
		return self._lockss[lock_name]

	def get_mount_point(self):
		return self.mount_point


	def get_lock_names(self):
		return self._locks.keys()

class LockSpace:
	"One lock space on multiple node"
	def __init__(self, node_ip_list, lock_space):
		#pdb.set_trace()
		self.node_ip_list = node_ip_list
		self.lock_space = lock_space
		self._nodes = {} #node_list[i] : LockSpaceOneNode
		for node in self.node_ip_list:
			self._nodes[node] = LockSpaceOneNode(lock_space, node)

	def run(self):
		pdb.set_trace()
		pool = ThreadPool(10)
		for node, lon in self._nodes.items():
			lon.run()
			#pool.apply_async(lon.run)

	@property
	def node_name_list(self):
		return self._nodes.keys()

	@property
	def node_list(self):
		return self._nodes.values()

	def __getitem__(self, key):
		return self._nodes.get(key, None)

nodes = ["10.67.162.62"] #, "10.67.162.52"]
import threading
def main():
	lock_spaces = util.get_dlm_lockspaces(nodes[0])
	target = lock_spaces[0]

	lock_space = LockSpace(nodes, target)
	lock_space.run()
	for node_name in lock_space.node_name_list:
		lock_space_node = lock_space[node_name]

		for lock_name in lock_space_node.get_lock_names():
			train = lock_space_node.get_lock(lock_name)

			pr_total = train.get_line("lock_total_prmode")
			pr_total_diff = train.get_line("lock_total_prmode", True)
			if pr_total[-1] - pr_total[0] > 5:
				print("[{}]".format(node_name), train.inode_num, train.lock_type,
					"pr total", pr_total)
				print("[{}]".format(node_name), train.inode_num, train.lock_type,
					"pr total diff", pr_total_diff)

			ex_total = train.get_line("lock_total_exmode")
			ex_total_diff = train.get_line("lock_total_exmode", True)
			if ex_total[-1] - ex_total[0] > 5:
				print("[{}]".format(node_name), train.inode_num, train.lock_type,
					"ex total", ex_total)
				print("[{}]".format(node_name), train.inode_num, train.lock_type,
					"ex total diff", ex_total_diff)

if __name__ == "__main__":
	main()
