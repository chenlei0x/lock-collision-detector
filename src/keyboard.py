#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import sys, os
import termios, fcntl
import select
import signal
import threading

class Keyboard():
	def __init__(self):
		pass

	def run(self, printer_queue):
		fd = sys.stdin.fileno()

		oldterm = termios.tcgetattr(fd)
		oldflags = fcntl.fcntl(fd, fcntl.F_GETFL)

		newattr = termios.tcgetattr(fd)
		newattr[3] = newattr[3] & ~termios.ICANON
		newattr[3] = newattr[3] & ~termios.ECHO
		termios.tcsetattr(fd, termios.TCSANOW, newattr)

		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags | os.O_NONBLOCK)

		while True:
			try:
				inp, outp, err = select.select([sys.stdin], [], [])
				c = sys.stdin.read()
			except:
				printer_queue.put({'msg_type':'quit',
									'what':'1'})
				break

			if c == 'q':
				printer_queue.put({'msg_type':'quit',
									'what':'1'})
				break

			if c == '1':
				printer_queue.put({'msg_type':'kb_hit',
									'what':'1'})

		# Reset the terminal:
		termios.tcsetattr(fd, termios.TCSAFLUSH, oldterm)
		fcntl.fcntl(fd, fcntl.F_SETFL, oldflags)

def worker(printer_queue):
	kb = Keyboard()
	kb.run(printer_queue)


if __name__ == '__main__':
	worker(None)
