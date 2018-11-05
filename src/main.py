#!/usr/bin/env python3
#-*- coding: utf-8 -*-


from collections import OrderedDict
import util
import pdb


# cat  -----  output of one time execution of "cat locking_stat"
# one cat contains multiple lockres(es)
# OneShot -----  lockinfo for one lockres in one cat
# BigTrain ---- a list of OneShot for a typical lockres
# Line ------- a list of specified index for one lock res
# LockSpace ---- A BigTrain should only belongs to one LockSpace
#

debug_info_v2 = []

class Cat:
	def __init__(self, lock_space):
		self.lock_space = lock_space

	def get(self):
		return util.get_one_cat(self.lock_space)

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

	def __str__(self):
		return self._name

	def __eq__(self, other):
		return other._name == self._name

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

class BigTrain():
	def __init__(self, lock_space):
		self._lock_space = lock_space
		self._train = []

	def get_line(self, data_type, delta=False):
		data_list = [int(getattr(i, data_type)) for i in self._train]
		if delta and len(data_list) >= 2:
			ret = [data_list[i] - data_list[i-1] for i in \
				range(1, len(data_list))]
		else:
			ret = data_list
		return ret

	def get_lock_name_line(self, index_name):
		ret = [i.getattr(index_name) for i in _train]
		return ret

	def append(self, shot):
		if not hasattr(self, "_name"):
			self._name = shot.name
		else:
			assert(self._name == shot.name)
		self._train.append(shot)


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



class LockSpace:
	LOOPS = 5
	INTERVAL = 3
	def __init__(self, lock_space):
		self.lock_space = lock_space
		self._trains = {}
		self.major, self.minor, self.mount_point = \
			util.lockspace_to_device(lock_space)
		self.lsof_cache = {}
		print(self)

	def __str__(self):
		ret = "lock space: {}\n mount point: {}".format(
			self.lock_space, self.mount_point)
		return ret
	def process_one_shot(self, s, time_stamp):
		#pdb.set_trace()
		shot  = OneShot(s, time_stamp)
		if not shot.legal():
			return
		shot_name = shot.name
		if shot_name not in self._trains:
			self._trains[shot_name] = BigTrain(self)
		train = self._trains[shot_name]
		train.append(shot)

	def run_once(self):
		cat = Cat(self.lock_space)
		raw_shot_strs = cat.get()
		time_stamp = util.now()
		for i in raw_shot_strs:
			self.process_one_shot(i, time_stamp)

	def append_new_shot(shot):
		if shot.lock_name not in self._trains:
			_trains[shot.lock_name] = BigTrain(self)
		_trains[shot.lock_name].append(i)

	def run(self, loops = 5, interval = "2s"):
		#pdb.set_trace()
		for i in range(LockSpace.LOOPS):
			self.run_once()
			util.sleep(LockSpace.INTERVAL)

	def __contains__(self, item):
		return item in self._trains

	def get_train(self, lock_name):
		if lock_name not in self:
			return None
		return self._trains[lock_name]

	def get_mount_point(self):
		return self.mount_point


	def get_lock_names(self):
		return self._trains.keys()

def main():
	lock_spaces = util.get_dlm_lockspaces()
	target = lock_spaces[0]
	lock_space = LockSpace(target)
	lock_space.run()
	for i in lock_space.get_lock_names():
		train = lock_space.get_train(i)

		pr_total = train.get_line("lock_total_prmode")
		pr_total_diff = train.get_line("lock_total_prmode", True)
		if pr_total[-1] - pr_total[0] > 5:
			print(train.inode_num, train.lock_type,
				"pr total", pr_total)
			print(train.inode_num, train.lock_type,
				"pr total diff", pr_total_diff)

		ex_total = train.get_line("lock_total_exmode")
		ex_total_diff = train.get_line("lock_total_exmode", True)
		if ex_total[-1] - ex_total[0] > 5:
			print(train.inode_num, train.lock_type,
				"ex total", ex_total)
			print(train.inode_num, train.lock_type,
				"ex total diff", ex_total_diff)

if __name__ == "__main__":
	main()
