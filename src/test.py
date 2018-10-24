#!/usr/bin/env python3
#-*- coding: utf-8 -*-


from collections import OrderedDict
import util


# cat  -----  output of one time execution of "cat locking_stat"
# one cat contains multiple lockres(es)
# OneShot -----  lockinfo for one lockres
# line	---- a list of OneShot for a typical lockres




debug_info_v2 = []

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

class LockResLine(list):
	def __init__(self, line):
		self.line = line

	def get_ex_list(data_type, delta=False):
		data_list = []
		if data_type = "num":
			data_list = [i.lock_num_exmode for i in self.line]
		elif data_type == "total wait":
			data_list = [i.lock_total_exmode for i in self.line]
		elif data_type == "max wait"
			data_list = [i.lock_man_exmode for i in self.line]
		else:
			return None
		if delta and len(data_list) >= 2:
			ret = [data_list[i] - data_list[i-1] for i in range(1, len(data_list))]
		else:
			ret = [data_list]
		return ret

	def get_pr_list(data_type, delta=False):
		data_list = []
		if data_type = "num":
			data_list = [i.lock_num_prmode for i in self.line]
		elif data_type == "total wait":
			data_list = [i.lock_total_prmode for i in self.line]
		elif data_type == "max wait"
			data_list = [i.lock_man_prmode for i in self.line]
		else:
			return None
		if delta and len(data_list) >= 2:
			ret = [data_list[i] - data_list[i-1] for i in range(1, len(data_list))]
		else:
			ret = [data_list]
		return ret

class LockResLines:
	lines_box = {
#		name: LockResLine
	}
	def __init__(self):
		self.name = name
		self.lock_infos = []

	def proceses_one_cat(raw_string):
		time_stamp = util.now()
		for i in self.debug_infos.splitlines():
			l = OneShot(i, time_stamp)
			if l.var_name not in lines_box:
				lines_box[l.var_name] = LockResLine
			lock_info_list = lines_box[l.var_name]
			lock_info_list.append(l)

	def get_line(self, name):
		shot_list = LockResLines.lines_box.get(name)
		return LockResLine(shot_list)

	def get_lock_names(self):
		return LockResLines.lines_box.keys()


lock_stat_string = " 0x3	M00000000000000000000056434f530	3	0x41	0x0	0x0	0	0	3	-1	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	18	0	0	0	374376	0	370	0	1	"

class LockSpace:
	LOOPS = 100
	INTERVAL = "100s"
	def __init__(self, lockspace):
		self.lockspace = lockspace
		self.lines = LockResLines()

	def run(self):
		for i in range(Main.loops):
			one_shot = self.get_one_cat()
			lines.proceses_one_shot(one_shot)
			util.sleep(Main.INTERVAL)

		for i in lines.get_lock_names():
			line = get_line(i)
			line.get_ex_list("num")
			line.get_pr_list("num")

def main():
	lockspaces = util.get_dlm_lockspaces()
	target = lockspaces[0]
	lock_space = LockSpace(target)
	lock_space.run()
