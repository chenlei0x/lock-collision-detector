#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import threading
import util

class _Getch:
	"""Gets a single character from standard input.  Does not echo to the
	screen."""
	def __init__(self):
		#try:
		#	self.impl = _GetchWindows()
		#except ImportError:
		self.impl = _GetchUnix()

	def __call__(self): return self.impl()


class _GetchUnix:
	def __init__(self):
		import tty, sys

	def __call__(self):
		import sys, tty, termios
		fd = sys.stdin.fileno()
		old_settings = termios.tcgetattr(fd)
		try:
			tty.setraw(sys.stdin.fileno())
			ch = sys.stdin.read(1)
		finally:
			termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
		return ch


class _GetchWindows:
	def __init__(self):
		import msvcrt

	def __call__(self):
		import msvcrt
		return msvcrt.getch()


getch = _Getch()


import sys, os
import termios, fcntl
import select
import signal

class Keyboard(threading.Thread):
	def __init__(self):
		self.key = '0'
		super().__init__()

	def run(self):
		fd = sys.stdin.fileno()
		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON
		newattr[3] = newattr[3] & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		oldterm = termios.tcgetattr(fd)
		oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

		while True:
			inp, outp, err = select.select([sys.stdin], [], [])
			c = sys.stdin.read()
			if c == 'q':
				self.key = c
				os.kill(os.getpid(), signal.SIGINT)
				break

			if c == '1':
				if self.key == c:
					self.key = '0'
					print("Short display!!!")
				else:
					self.key = '1'
					print("Detailed display!!!")


		# Reset the terminal:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)
