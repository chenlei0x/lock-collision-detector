#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import util
import dlm
import printer
import keyboard
import threading
import sys
import signal
import argparse
import multiprocessing


def parse_args():
	description=""
	usage = \
"""
o2top is a tool used to tell which inode is most busy it works like linux top command
This tool supports both local and remote monitoring your filesystem

REMOTE MODE:
  o2top [-o LOG_FILE_PATH] -n <NODE_IP>:<MOUNT_POINT> -n <NODE_IP>

LOCAL MODE:
  o2top [-o LOG_FILE_PATH] <MOUNT_POINT>

Running in remote mode allows users run out of or inside of your cluster.
Use -n to specify the remote ip or hostname used for ssh

  1. copy ssh pub key to remote host

    (1). ssh-copy-id root@192.168.1.1

    (2). ssh-copy-id root@192.168.1.2

  2. run o2top and use ":" to specify a combination of a node and a mount point on it

    o2top  -o /path/to/test.log -n 192.168.1.1 -n 192.168.1.2:/mnt/ocfs2

o2top also supports local mode, use -m to specify the local mount point.

    o2top -o /path/to/test.log /mnt/ocfs2

NOTICE:

1. When running, press '1' to see what is happening on each node :)

2. When running, Press 'q' to exit gracefully

MORE:

Now, o2top can only shows the inode number of the busy files, you should help yourself to
find the path corresponding to the inode number.
"""
	parser = argparse.ArgumentParser(description=description, usage=usage)
	parser.add_argument('-n', metavar='host',
						dest='host_list', action='append',
						help="node address used for ssh")

	parser.add_argument('-o', metavar='log', dest='log',
						action='store', help="log path")

	parser.add_argument('local_mount', nargs='?',
						help='local mount point like 192.168.1.1:/mnt')


	args = parser.parse_args()
	mount_node, mount_point = None, None

	node_list = []
	met_colon = False
	if args.host_list:
		for i in args.host_list:

			if ":" in i:
				if met_colon:
					util.eprint("Respecify mount point: " + i)
					exit(0)
				try:
					mount_node, mount_point = i.split(':')
					node_list.append(mount_node)
				except:
					util.eprint("Error parameter: " + i)
					exit(0)
			else:
				node_list.append(i)
		if args.local_mount:
			util.eprint("Local mount point is not needed")
			exit(0)

		return {
				"mode":"remote",
				"mount_node" : mount_node,
				"mount_point" : mount_point,
				"node_list" : node_list,
				"log" : args.log
				}
	elif args.local_mount:
		mount_point = args.local_mount
		return {
				"mode":"local",
				"mount_point" : args.local_mount,
				"log" : args.log
				}

	parser.print_help()
	exit(0)

def main():
	args = parse_args()

	if args['mode'] == "remote":
		nodes = args["node_list"]
		mount_host, mount_point = args["mount_node"], args["mount_point"]
		log = args["log"]
		lock_space_str = util.get_dlm_lockspace_mp(mount_host, mount_point)
		mount_info = ':'.join([mount_host, mount_point])
	elif args['mode'] == "local":
		mount_point = args["mount_point"]
		log = args["log"]
		lock_space_str = util.get_dlm_lockspace_mp(None, mount_point)
		mount_info = mount_point

	if lock_space_str is None:
		print("Error while getting lockspace")
		exit(0)

	if args["mode"] == "local":
		nodes = None

	printer_queue = multiprocessing.Queue()
	printer_process = multiprocessing.Process(target=printer.worker,
										args=(printer_queue, log),
										kwargs={"mount_info":mount_info}
									)
	lock_space_process = multiprocessing.Process(target=dlm.worker,
										args=(lock_space_str, nodes, printer_queue)
										)


	printer_process.start()
	lock_space_process.start()

	keyboard.worker(printer_queue)

	lock_space_process.terminate()
	lock_space_process.join()

	#printer_process will exit on quit message
	#printer_process.terminate()
	printer_process.join()

	exit(0)

if __name__ == "__main__":
	main()
