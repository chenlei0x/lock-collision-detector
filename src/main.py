#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import OrderedDict
import util
import ipdb as pdb
from multiprocessing.dummy import Pool as ThreadPool
import Cat

# cat  -----  output of one time execution of "cat locking_stat"
				# one cat contains multiple Shot(es)
# Shot -----  lockinfo for one lockres at one time of cat
# Lock   ---- a list of Shot for a typical lockres
# Node --- LockSpace on one node, which contains multiple Lock(s)
# LockSpace ---- A Lock should only belongs to one LockSpace
#

LOCK_LEVEL_PR = 0
LOCK_LEVEL_EX = 1


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

class Shot:
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
		for k, v in Shot.debug_format_v3.items():
			var_name = k
			var_len = v
			value = "".join(strings[i: i + var_len])
			setattr(self, var_name, value)
			i += var_len
		self.name = LockName(self.name)

	def __str__(self):
		ret = []
		for k in Shot.debug_format_v3.keys():
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
	def __init__(self, node):
		self._node = node
		self._shots= []

	@property
	def shot_count(self):
		return len(self._shots)

	@property
	def name(self):
		return getattr(self, "_name", None)

	@property
	def node(self):
		return self._node

	@property
	def lock_space(self):
		return self._node.lock_space

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

	def get_lock_level_info(self, lock_level):
		#pdb.set_trace()
		if not self.has_delta():
			return 0, 0, 0

		total_time_field, total_num_field = self._lock_level_2_field(lock_level)
		delta_time = self._get_latest_data_field_delta(total_time_field)
		delta_num = self._get_latest_data_field_delta(total_num_field)
		#(total_time, total_num, key_indexn)
		if delta_time and delta_num:
			return delta_time, delta_num, delta_time/delta_num
		return 0, 0, 0

	def has_delta(self):
		return len(self._shots) >= 2

	def append(self, shot):
		if not hasattr(self, "_name"):
			self._name = shot.name
		else:
			assert(self._name == shot.name)
		self._shots.append(shot)

	def get_line(self, data_field, delta=False):
		data_list = [int(getattr(i, data_field)) for i in self._shots]
		if not delta:
			return data_list

		if self.has_delta():
			ret = [data_list[i] - data_list[i-1] for i in \
				range(1, len(data_list))]
			return ret

		return None

	def get_key_index(self, begin=-2, end=-1):
		if self.shot_count < 2:
			return 0
		avg_key_index = 0
		for level in [LOCK_LEVEL_PR, LOCK_LEVEL_EX]:
			*_, key_index= self.get_lock_level_info(level)
			avg_key_index += key_index
		return avg_key_index/2


	def _get_data_field_indexed(self, data_field, index = -1):
		try:
			ret =getattr(self._shots[index], data_field)
			return ret
		except:
			return None

	def _get_latest_data_field_delta(self, data_field):
		if not self.has_delta():
			return 0
		latter = self._get_data_field_indexed(data_field, -1)
		former = self._get_data_field_indexed(data_field, -2)
		return int(latter) - int(former)

	def _lock_level_2_field(self, lock_level):
		if lock_level == LOCK_LEVEL_PR:
			total_time_field = "lock_total_prmode"
			total_num_field =  "lock_num_prmode"
		elif lock_level == LOCK_LEVEL_EX:
			total_time_field = "lock_total_exmode"
			total_num_field = "lock_num_exmode"
		else:
			return None, None
		return total_time_field, total_num_field


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
	# locks which has the same name but on different node
	def __init__(self, lock_list=None):


		self.node_to_lock_dict = {}

		if lock_list is None:
			self._lock_list = []
			self._nodes_count = 0
			self._name = None
			return

		name = lock_list[0].name
		for i in lock_list:
			assert(i.name == name)

		self._lock_list = lock_list
		self._nodes_count = len(lock_list)
		self._name = self._lock_list[0].name
		for i in self._lock_list:
			self.append(i)


	@property
	def name(self):
		if hasattr(self, "_name"):
			return self._name
		return None

	def append(self, lock):
		if self._name is None:
			self._name = lock.name

		self._lock_list.append(lock)
		self._nodes_count += 1
		assert lock.node not in self.node_to_lock_dict
		self.node_to_lock_dict[lock.node] = lock

	def report_once(self):
		if len(self.node_to_lock_dict) == 0:
			return

		ret = ""
		res_ex = {"total_time":0,"total_num":0, "key_index":0}
		res_pr = {"total_time":0,"total_num":0, "key_index":0}
		body = ""

		#pdb.set_trace()
		for _node, _lock in self.node_to_lock_dict.items():

			total_time, total_num, key_index = _lock.get_lock_level_info(LOCK_LEVEL_EX)
			res_ex["total_time"] += total_time
			res_ex["total_num"] += total_num

			ex_report_str = "\t{} PR [{}, {}, {}]".format(
					_node.name, total_num, total_time, key_index)


			total_time, total_num, key_index = _lock.get_lock_level_info(LOCK_LEVEL_PR)
			res_pr["total_time"] += total_time
			res_pr["total_num"] += total_num

			pr_report_str = "EX [{}, {}, {}]".format(total_num, total_time, key_index)

			body += ex_report_str + pr_report_str

		if res_ex["total_num"] != 0:
			res_ex["key_index"] = res_ex["total_time"]/res_ex["total_num"]
		if res_pr["total_num"] != 0:
			res_pr["key_index"] = res_pr["total_time"]/res_pr["total_num"]
		title = "[inode {}] EX [{}, {}, {}] PR [{}, {}, {}]".format(self.name, \
				res_ex["total_num"], res_ex["total_time"], res_ex["key_index"], \
				res_pr["total_num"], res_pr["total_time"], res_pr["key_index"])

	@property
	def name(self):
		return self._name

	def get_key_index(self):
		if len(self._lock_list) == 0:
			return 0

		key_index = 0
		for i in self._lock_list:
			key_index += i.get_key_index()

		return key_index/len(self._lock_list)

class LockSetGroup():
	def __init__(self):
		self.lock_set_list = []
		self.lock_name_to_lock_set = {}

	def append(self, lock_set):
		self.lock_name_to_lock_set[lock_set.name] = lock_set
		self.lock_set_list.append(lock_set)

	def get_top_n_key_index(self, n):
		self.lock_set_list.sort(key=lambda x:x.get_key_index())
		return self.lock_set_list[:n]

	def report_once(self, top_n):
		top_n_lock_set = self.get_top_n_key_index(top_n)
		for lock_set in top_n_lock_set:
			lock_set.report_once()


class Node:
	def __init__(self, lock_space, node_name=None):
		self._lock_space = lock_space
		self._locks = {}
		self.major, self.minor, self.mount_point = \
			util.lockspace_to_device(self._lock_space.name, node_name)
		self._node_name = node_name

	@property
	def name(self):
		return self._node_name

	def __str__(self):
		ret = "lock space: {}\n mount point: {}".format(
			self._lock_space.name, self.mount_point)
		return ret

	@property
	def lock_space(self):
		return self._lock_space

	def process_one_shot(self, raw_string, time_stamp):
		shot  = Shot(raw_string, time_stamp)
		if not shot.legal():
			return
		shot_name = shot.name
		if shot_name not in self._locks:
			self._locks[shot_name] = Lock(self)
		lock = self._locks[shot_name]
		lock.append(shot)
		self.lock_space.lock_names.append(shot_name)

	def run_once(self, time_stamp=None):
		cat = Cat.gen_cat('ssh', self.lock_space.name, self.name)
		#pdb.set_trace()
		raw_shot_strs = cat.get()
		print("[%s]"%self.name, "running", raw_shot_strs.__len__())
		if time_stamp is None:
			time_stamp = util.now()
		for i in raw_shot_strs:
			self.process_one_shot(i, time_stamp)

	def run(self, loops=5, interval=2):
		for i in range(loops):
			print(self.name, "running")
			self.run_once()
			util.sleep(interval)

	def __contains__(self, item):
		return item in self._locks

	def __getitem__(self, key):
		return self._locks.get(key, None)

	def get_lock_names(self):
		return self._locks.keys()

class LockSpace:
	"One lock space on multiple node"
	LOOP = 5
	INTERVAL = 2

	def __init__(self, node_name_list, lock_space):
		#pdb.set_trace()
		self._name = lock_space
		self._nodes = {} #node_list[i] : Node
		self.lock_names = []
		for node in node_name_list:
			self._nodes[node] = Node(self, node)


	def run(self):
		loops = LockSpace.LOOP
		interval = LockSpace.INTERVAL
		for i in range(loops):
			pool = ThreadPool(10)
			for node_name, node in self._nodes.items():
				node.run_once()
			#for node_name, node in self._nodes.items():
			#	pool.apply_async(node.run_once)
			#pool.close()
			#pool.join()
			self.report_once()


	@property
	def name(self):
		return self._name

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

	def lock_name_to_lock_set(self, lock_name):
		lock_set = LockSet()
		for node in self.node_list:
			lock = node[lock_name]
			if lock is not None:
				lock_set.append(lock)
		return lock_set

	def get_all_lock_names(self):
		return self.lock_names

	def report_once(self, node_detail=False, where_to_output=""):
		lock_names = self.lock_names
		lsg = LockSetGroup()
		for lock_name in lock_names:
			lock_set = self.lock_name_to_lock_set(lock_name)
			lsg.append(lock_set)
		lsg.report_once(10)



nodes = ["10.67.162.62", "10.67.162.52"]
import threading
def main():
	lock_spaces = util.get_dlm_lockspaces(nodes[0])
	target = lock_spaces[0]

	lock_space = LockSpace(nodes, target)
	lock_space.run()


if __name__ == "__main__":
	main()
