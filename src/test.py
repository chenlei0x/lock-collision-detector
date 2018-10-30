#!/usr/bin/env python3
#-*- coding: utf-8 -*-


from collections import OrderedDict
import util


# cat  -----  output of one time execution of "cat locking_stat"
# one cat contains multiple lockres(es)
# OneShot -----  lockinfo for one lockres in one cat
# BigTrain ---- a list of OneShot for a typical lockres
# Line ------- a list of specified index for one lock res
# LockSpace ---- A BigTrain should only belongs to one LockSpace
#

debug_info_v2 = []

class Cat:
	def __init__():
		pass
	def get_lines():
		pass

class OneShot:
	debug_info_v3 = OrderedDict([
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
		for k, v in OneShot.source_str_v3.iterms():
			var_name = k
			var_len = v
			value = "".join(strings[i: i + var_len])
			setattr(self, var_name, value)
			i += var_len

	def __str__(self):
		ret = []
		for k in OneShot.debug_info_v3.keys():
			v = getattr(self, k)
			ret.append("{} : {}".format(k, v))
		return "\n".join(ret)

class BigTrain():
	def __init__(self, lock_space):
		self._lock_space = lock_space
		self._train = []
		self._name = None

	def get_line(self, data_type, delta=False):
		data_list = [i.getattr(data_type) for i in self._train]
		if delta and len(data_list) >= 2:
			ret = [data_list[i] - data_list[i-1] for i in range(1, len(data_list))]
		else:
			ret = [data_list]
		return ret

	def get_lock_name_line(self, index_name):
		ret = [i.getattr(index_name) for i in _train]
		return ret

	def append(self, item):
		assert(self._name is None or self.lock_name==item.name)
		if self._name is None:
			self.name = item.name
		self._train.append(item)
	"""
	M    000000 0000000000000005        6434f530
	type  PAD   blockno(hex)			generation(hex)
	[0:1][1:1+6][1+6:1+6+16]			[1+6+16:]
	"""

	@property
	def lock_type(self):
		lock_name = self._name
		if lock_name is None:
			return None
		return lock_name[0]

	@property
	def inode_num(self):
		start, end = 1, 1+6
		lock_name = self._name
		if lock_name is None:
			return None
		return int(lock_name[start : end], 16)

	@property
	def lock_space(self):
		return self._lock_space

	@property
	def file_path(self):
		mps == self._lock_space.get_mount_points()
		if len(mps) == 0:
			return None
		mp = mps[0]
		inode_num = self.inode_num()
		return util.get_lsof(mp, inode_num)


class LockSpace:
	LOOPS = 100
	INTERVAL = "100s"
	def __init__(self, lock_space):
		self.lock_space = lock_space
		self._trains = {}
		self.device = util.lockspace_to_device(lockspace)
		self.mount_points = device_to_mount_points(device)

	def process_one_shot(string):
		time_stamp = util.now()
		l = OneShot(i, time_stamp)
		if l.var_name not in _trains:
			_trains[l.var_name] = LockResLine
		lock_info_list = _trains[l.var_name]
		lock_info_list.append(l)

	def proceses_one_cat(raw_string):
		time_stamp = util.now()
		for i in self.raw_string.splitlines():
			l = OneShot(i, time_stamp)
			if l.var_name not in _trains:
				_trains[l.var_name] = BigTrain()
			train = _trains[l.var_name]
			train.append(l)

	def run_once(self):
		cat = Cat(self.lock_space)
		raw_shot_strs = cat.run()
		for i in raw_shot_strs:
			one_shot = OneShot(i)
			self.append_new_shot(i)

	def append_new_shot(shot):
		if shot.lock_name not in self._trains:
			_trains[shot.lock_name] = BigTrain(self)
		_trains[shot.lock_name].append(i)

	def run(self, loops = 100, interval = "2s"):
		for i in range(Main.loops):
			run_once()
			util.sleep(Main.INTERVAL)

	def __contains__(self, item):
		return i in self._trains

	def get_train(self, lock_name):
		if lock_name not in self:
			return None
		return self._trains[lock_name]


	def get_lock_names(self):
		return self._trains.keys()


lock_stat_string = " 0x3	M00000000000000000000056434f530	3	0x41	0x0	0x0	0	0	3	-1	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	18	0	0	0	374376	0	370	0	1	"


def main():
	lock_spaces = util.get_dlm_lockspaces()
	target = lock_spaces[0]
	lock_space = LockSpace(target)
	lock_space.run()
	for i in lockspace.get_lock_names():
		train = lock_space.get_train(i)
		print(train.get_line("lock_total_prmode"))
		print(train.get_line("lock_total_exmode"))
