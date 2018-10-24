#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import datetime
import time
from . import shell

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

def lockspace_to_device(uuid):
	sh = shell.Shell()
	cmd = "cat /sys/kernel/debug/ocfs2/{uuid}/fs_stat | grep Device =>".format(uuid=uuid)
	sh.run(cmd)
	output = sh.output()
	#output should be like
	"""
    Device => Id: 253,16  Uuid: 7635D31F539A483C8E2F4CC606D5D628  Gen: 0x6434F530  Label:
	"""
	dev_major, dev_minor = output.split()[3].split(",")
	cmd = "lsblk"
	output = sh.run("lsblk -o MAJ:MIN,KNAME | grep '{major}:{minor}'".format(
			major=dev_major,minor=dev_minor))
	#output should be like
	"└─vda2 253:2    0 58.6G  0 part / "



def get_dlm_lockspaces():
	cmd = shell.shell("dlm_tool ls | grep ^name")
	output = cmd.output()
	lockspace_list = [i[1] for i in output]
	if len(lockspace_list):
		return lockspace_list
	return None
