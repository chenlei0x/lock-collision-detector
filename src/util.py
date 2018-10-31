#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import datetime
import time
import shell
import pdb

def now():
	"""
	:type nums: List[int]
	:type k: int
	:rtype: datetime
	"""
	return datetime.datetime.now()

def sleep(interval):
	"""
	:rtype: None
	"""
	return time.sleep(interval)

def get_one_shot(lockspace):
	"""
	:type lockspace: str
	:rtype: str
	"""
	sh = shell.Shell()
	cmd = "cat /sys/kernel/debug/ocfs2/{lockspace}/locking_state"
	sh = shell.run(cmd.format(lockspace=lockspace))
	ret = sh.output()
	return ret


# fs_stat
"""
    Device => Id: 253,16  Uuid: 7635D31F539A483C8E2F4CC606D5D628  Gen: 0x6434F530  Label:
    Volume => State: 2  Flags: 0x0
     Sizes => Block: 4096  Cluster: 4096
  Features => Compat: 0x3  Incompat: 0xB7D0  ROcompat: 0x1
     Mount => Opts: 0x104  AtimeQuanta: 60
   Cluster => Stack: pcmk  Name: 7635D31F539A483C8E2F4CC606D5D628  Version: 1.0
  DownCnvt => Pid: 3802  Count: 0  WakeSeq: 707  WorkSeq: 707
  Recovery => Pid: -1  Nodes: None
    Commit => Pid: 3810  Interval: 0
   Journal => State: 1  TxnId: 2  NumTxns: 0
     Stats => GlobalAllocs: 0  LocalAllocs: 0  SubAllocs: 0  LAWinMoves: 0  SAExtends: 0
LocalAlloc => State: 1  Descriptor: 0  Size: 27136 bits  Default: 27136 bits
     Steal => InodeSlot: -1  StolenInodes: 0, MetaSlot: -1  StolenMeta: 0
OrphanScan => Local: 117  Global: 248  Last Scan: 5 seconds ago
     Slots => Num     RecoGen
            *   0           1
                1           0
                2           0
                3           0
                4           0
                5           0
                6           0
                7           0
"""
import os
def major_minor_to_device_path(major, minor):
	sh = shell.Shell()
	sh.run("lsblk -o MAJ:MIN,KNAME,MOUNTPOINT -l | grep '{major}:{minor}'".format(
			major=major,minor=minor))
	output = sh.output()
	#output should be like
	"""
	MAJ:MIN KNAME
	253:0   vda
	253:1   vda1
	253:2   vda2
	253:16  vdb
	"""
	assert(len(output) > 0)
	device_name = output[0].split()[1]
	return device_name

def lockspace_to_device(uuid):
	pdb.set_trace()
	sh = shell.Shell()
	cmd = "cat /sys/kernel/debug/ocfs2/{uuid}/fs_state | grep 'Device =>'".format(uuid=uuid)
	sh.run(cmd)
	output = sh.output()
	#output should be like
	"""
    Device => Id: 253,16  Uuid: 7635D31F539A483C8E2F4CC606D5D628  Gen: 0x6434F530  Label:
	"""
	dev_major, dev_minor = output[0].split()[3].split(",")

	sh.run("lsblk -o MAJ:MIN,KNAME,MOUNTPOINT -l | grep '{major}:{minor}'".format(
			major=major,minor=minor))
	output = sh.output()
	#before grep output should be like
	"""
	MAJ:MIN KNAME MOUNTPOINT
	253:0   vda
	253:1   vda1  [SWAP]
	253:2   vda2  /
	253:16  vdb   /mnt/ocfs2-1
	"""
	#after grep
	"""
	253:16  vdb   /mnt/ocfs2-1
	"""
	assert(len(output) > 0)
	device_name, mount_point = *output[0].split()
	return dev_major, dev_minor, mount_point
	#device_name = major_minor_to_device_path(dev_major, dev_minor)
	#return device_name

def get_dlm_lockspaces():
	cmd = shell.shell("dlm_tool ls | grep ^name")
	output = cmd.output()
	lockspace_list = [i.split()[1] for i in output]
	if len(lockspace_list):
		return lockspace_list
	return None


"""
lchen-vanilla-node1:~/code # mount | grep "type ocfs2" | cut -f1
/dev/vdb on /mnt/ocfs2 type ocfs2 (rw,relatime,heartbeat=none,nointr,data=ordered,errors=remount-ro,atime_quantum=60,cluster_stack=pcmk,coherency=full,user_xattr,acl)
/dev/vdb on /mnt/ocfs2-1 type ocfs2 (rw,relatime,heartbeat=none,nointr,data=ordered,errors=remount-ro,atime_quantum=60,cluster_stack=pcmk,coherency=full,user_xattr,acl)
"""
def device_to_mount_points(device):
	cmd = shell.shell("mount | grep 'type ocfs2'")
	output = cmd.output()
	dev_stat = os.stat(device)
	dev_num = dev_stat.st_rdev

	ret = []
	for i in output:
		i = i.split()
		_dev = i[0]
		if os.stat(_dev).st_rdev == dev_num:
			ret.append(i[2])
	return list(set(ret))



"""
lchen-vanilla-node1:~/code # lsof +D /mnt/ocfs2/
COMMAND   PID USER   FD   TYPE DEVICE SIZE/OFF   NODE NAME
vim     26463 root    4u   REG 253,16    12288 697713 /mnt/ocfs2/.1.swp
"""
def get_lsof(mount_point, inode_num):
	cmd = shell.shell("lsof +D {directory}".format(directory=mount_point))
	output = cmd.output()
	for i in output:
		str_list = i.split()
		if str_list[-2] == inode_num:
			return str_list[-1]
	return None
