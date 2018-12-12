#!/usr/bin/env python
#-*- coding: utf-8 -*-

import util
import dlm
from printer import Printer
import keyboard
import threading
import sys
import signal
import argparse


def parse_args():
	description=""
	usage = \
"""
o2top is a tool used to tell which inode is most busy it works like linux top command
This tool supports both local and remote monitoring your filesystem

Running in remote mode allows users run out of or inside of your cluster.
Use -n to specify the remote ip or hostname used for ssh

1. copy ssh pub key to remote host

	(1). ssh-copy-id root@192.168.1.1

	(2). ssh-copy-id root@192.168.1.2

2. run o2top and use -m to tell me the mount point and the host it resides on, use '/'
   as a delimeter

	%(prog)s --remote -o /path/to/test.log -n 192.168.1.1 -n 192.168.1.2 -m 192.168.1.1:/mnt/ocfs2

o2top also supports local mode, use -m to specify the local mount point.

	%(prog)s --local -o /path/to/test.log -m /mnt/ocfs2

When running, press '1' to see what is happening on each node :)
press 'q' to exit gracefully

Now, o2top can only shows the inode number of the busy files, you should help yourself to
find the path corresponding to the inode number.
"""
	parser = argparse.ArgumentParser(description=description, usage=usage)
	parser.add_argument('-n', metavar='host',
						dest='host_list', action='append',
						help="node address used for ssh")

	parser.add_argument('-m', metavar='mount',
						dest="mount",
						help='mount point and the address it resides on," \
							 "like 192.168.1.1:/mnt')
	parser.add_argument('-o', metavar='log', dest='log',
						action='store', help="log path")

	parser.add_argument('--remote', dest='remote',
						action='store_true', help="run in remote mode")

	parser.add_argument('--local', dest='local',
						action='store_true', help="run in local mode")


	args = parser.parse_args()

	if args.remote is True and args.local is True:
		print("Error, remote and local mode can not coexist")
		exit(0)

	if args.remote is True:
		if args.host_list is None:
			print("Use -n to specify which node to be monitored")
		if args.mount is None:
			print("Use -n to specify mount point like -m 192.168.1.1:/mnt")
		mount_info = args.mount.split(':')
		if len(mount_info) != 2:
			print("Mount point format error, -m 192.168.1.1:/mnt")
	elif args.local is True:
		mount_point = args.mount
	else:
		print("Use --local or --remote to specify mode")
		exit(0)

	return args

def main():
	args = parse_args()

	if args.remote is True:
		nodes = args.host_list
		mount_host, mount_point = args.mount.split(':')
		log = args.log
		lock_space_str = util.get_dlm_lockspace_mp(mount_host, mount_point)

	elif args.local is True:
		mount_point = args.mount
		log = args.log
		lock_space_str = util.get_dlm_lockspace_mp(None, mount_point)

	if lock_space_str is None:
		print("Error while getting lockspace")
		exit(0)

	my_printer = Printer()
	kb = keyboard.Keyboard()
	if args.remote:
		lock_space = dlm.LockSpace(nodes, lock_space_str)
	else:
		lock_space = dlm.LockSpace(None, lock_space_str)


	printer_thread = threading.Thread(target=my_printer.run, args = (log,))
	kb_thread = threading.Thread(target=kb.run, kwargs={"printer":my_printer})

	lock_space_thread = threading.Thread(target=lock_space.run,
								kwargs={"printer":my_printer, "sync":False})

	printer_thread.start()
	kb_thread.start()
	lock_space_thread.start()

	kb_thread.join()
	util.kill()

	lock_space.stop()
	lock_space_thread.join()

	my_printer.stop()
	printer_thread.join()

	exit(0)
if __name__ == "__main__":
	main()
