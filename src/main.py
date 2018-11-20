#!/usr/bin/env python3
#-*- coding: utf-8 -*-

from collections import OrderedDict
import util
import ipdb as pdb
import dlm
import printer

class BaseThread(threading.Thread):
	def __init__(self, obj):
		self.obj = obj
		super().__init__()

	def set_run_args(self, *args, **kargs):
		self.args = args
		self.kargs = kargs

	def run(self):
		if hasattr(self, "args") and hasattr(self, "kargs"):
			self.obj.run(*self.args, **self.kargs)
		else:
			self.lock_space.run()


def parse_args():
	import argparse
	description=
	"""Ocfs2 Lock Top
This is a tool used to tell which inode is most busy
it works like linux top command"""
	usage = "%(prog)s -o test.log -n 192.168.1.1 -n 192.168.1.2 -m 192.168.1.1:/mnt/ocfs2"
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
	n = parser.parse_args()
	print(n)
	nodes = n.host_list
	mount_host, mount_point = n.mount.split(':')
	log = n.log
	return nodes, mount_host, mount_point, log


def signal_handler(signum, frame):
	if signum == signal.SIGINT:
		print("signal {}".format(signum))
		sys.exit(0)
	else:
		return 0


def block_signal():
	signal.pthread_sigmask(signal.SIGINT)

def set_up_signal():
	signal.pthread_sigmask(signal.SIGUNBLOCK, signal.SIGINT)
	signal.signal(signal.SIGINT, signal_handler)
	signal.signal(signal.SIGALRM, signal_handler)

def main():
	global lock_space
	sys.argv.extend("-o test.log -n 10.67.162.62 -n 10.67.162.52 -m 10.67.162.62:/mnt".split())
	nodes, mount_host, mount_point, log = parse_args()
	#print(nodes, mount_host, mount_point)

	lock_space_str = util.get_dlm_lockspace_mp(mount_host, mount_point)

	block_signal()

	lock_space = dlm.LockSpace(nodes, lock_space_str)
	lock_space_thread = BaseThread(LockS)
	lock_space_thread.set_run_args(output=log)
	lock_space_thread.start()

	printer = printer.Printer()
	printer_thread = BaseThread(printer)
	printer.start()

	kb_thraed = getch.Keyboard()
	kb_thread.start()

	set_up_signal()

	kb_thraed.join()
	exit(0)
if __name__ == "__main__":
	main()
