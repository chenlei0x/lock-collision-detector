#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys, os
import termios, fcntl
import select
import signal
import threading
import printer as _printer

class Keyboard():
	def __init__(self):
		self.key_1_cnt = 0

	def run(self, printer):
		fd = sys.stdin.fileno()

		oldterm = termios.tcgetattr(fd)
		oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)

		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON
		newattr[3] = newattr[3] & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

		while True:
			inp, outp, err = select.select([sys.stdin], [], [])
			c = sys.stdin.read()
			if c == 'q':
				#printer.stop()
				break

			if c == '1':
				self.key_1_cnt += 1
				mode_list = [_printer.SIMPLE_DISPLAY, _printer.DETAILED_DISPLAY]
				mode = mode_list[self.key_1_cnt%2]
				printer.set_display_mode(mode)


		# Reset the terminal:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

