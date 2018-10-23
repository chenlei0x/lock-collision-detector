#!/usr/bin/env python3
#-*- coding: utf-8 -*-


from collections import OrderedDict



debug_info_v2 = [

]

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

	def __init__(self, debug_info):
		self.source = debug_info.strip()
		strings = debug_info.strip().split()
		assert(int(strings[0].lstrip("0x")) == 3)

		i = 0
		for k, v in OneShot.debug_info_v3.iterms():
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


class LockResCollection:
	shots_box = {
		name: [OneShot, OneShot]
	}
	def __init__(self):
		self.name = name
		self.lock_infos = []

	def proceses_one_shot(raw_string):
		# raw_string: str 
		raw_string.

		for i in self.debug_infos.splitlines():
			l = OneShot(i)
			if l.var_name not in shots_box:
				shots_box[l.var_name] = []
			lock_info_list = shots_box[l.var_name]
			# lock_info_list: list
			lock_info_list.append(l)

	def rt_biebb():
		for lock_name, shot_list in LockResCollection.shots_box.items():
			lock_num_prmode = [x.lock_num_prmode for x in shot_list]
			lock_num_exmode = [x.lock_num_exmode for x in shot_list]
			lock_total_prmode = [x.lock_total_prmode for x in shot_list]
			lock_total_exmode = [x.lock_total_exmode for x in shot_list]
			lock_max_prmode = [x.lock_max_prmode for x in shot_list]
			lock_max_exmode = [x.lock_max_exmode for x in shot_list]

	def biebb():
		for lock_name, shot_list in LockResCollection.shots_box.items():
			lock_num_prmode = [x.lock_num_prmode for x in shot_list]
			lock_num_exmode = [x.lock_num_exmode for x in shot_list]
			lock_total_prmode = [x.lock_total_prmode for x in shot_list]
			lock_total_exmode = [x.lock_total_exmode for x in shot_list]
			lock_max_prmode = [x.lock_max_prmode for x in shot_list]
			lock_max_exmode = [x.lock_max_exmode for x in shot_list]



lock_stat_string = " 0x3	M00000000000000000000056434f530	3	0x41	0x0	0x0	0	0	3	-1	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	0x0	18	0	0	0	374376	0	370	0	1	"


