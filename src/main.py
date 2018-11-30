#!/usr/bin/env python2
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
	description="Ocfs2 Lock Top" \
		"This is a tool used to tell which inode is most busy" \
		"it works like linux top command"
	usage = "%(prog)s -r -o test.log -n 192.168.1.1 -n 192.168.1.2 -m 192.168.1.1:/mnt/ocfs2"
	usage = "%(prog)s -l -o test.log -m /mnt/ocfs2"
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

	parser.add_argument('--remote', metavar='remote', dest='remote',
						action='store_true', help="run in remote mode")

	parser.add_argument('--local', metavar='locl', dest='local',
						action='store_true', help="run in local mode")

	n = parser.parse_args()
	if n.remote is True and n.remote is True:
		parser.print_help()

	return n




def signal_handler(signum, frame):
	if signum == signal.SIGINT:
		print("signal {}".format(signum))
		sys.exit(0)
	else:
		return 0


def block_signal():
	signal.pthread_sigmask(signal.SIG_BLOCK, [signal.SIGINT])

def set_up_signal():
	signal.pthread_sigmask(signal.SIG_UNBLOCK, [signal.SIGINT])
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGALRM, signal_handler)



def main():
	#sys.argv.extend("-r -o test.log -n 10.67.162.62 -n 10.67.162.52 -m 10.67.162.62:/mnt".split())
	sys.argv.extend("-l /mnt".split())
	args = parse_args()
	#nodes, mount_host, mount_point, log = parse_args()

	if args.remote is True:
		nodes = args.host_list
		mount_host, mount_point = args.mount.split(':')
		log = args.log
	else:
		mount_host, mount_point = args.mount
		log = args.log
	lock_space_str = util.get_dlm_lockspace_mp(mount_host, mount_point)

	my_printer = Printer()
	kb = keyboard.Keyboard()
	if args.remote:
		lock_space = dlm.LockSpace(nodes, lock_space_str)
	else:
		lock_space = dlm.LockSpace(None, lock_space_str)


	printer_thread = threading.Thread(target=my_printer.run, args = (log,))
	kb_thread = threading.Thread(target=kb.run, kwargs={"printer":my_printer})
	lock_space_thread = threading.Thread(target=lock_space.run,
									kwargs={"printer":my_printer})

	printer_thread.start()
	kb_thread.start()
	lock_space_thread.start()


	kb_thread.join()

	lock_space.stop()
	lock_space_thread.join()
	print("lock space stopped")

	my_printer.stop()
	printer_thread.join()
	print("printer stopped")

	print("main exit")
	exit(0)
if __name__ == "__main__":
	main()
