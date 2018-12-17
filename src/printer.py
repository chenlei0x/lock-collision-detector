#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import threading
import util
import multiprocessing

SIMPLE_DISPLAY=0
DETAILED_DISPLAY=1

class Printer():
	def __init__(self, log):
		self.content = None
		self.display_mode = SIMPLE_DISPLAY
		self.should_stop = False
		self.log = None
		if log is not None:
			self.log = open(log, 'w')
		self.prelude = None

	def _refresh(self):
		if self.content:
			util.clear_screen()
			if self.prelude:
				print(self.prelude)
			print(self.content[self.display_mode])

	def activate(self, simple_content, detailed_content):
		self.content = (simple_content, detailed_content)
	def toggle_display_mode(self):
		if self.display_mode == SIMPLE_DISPLAY:
			self.set_display_mode(DETAILED_DISPLAY)
		else:
			self.set_display_mode(SIMPLE_DISPLAY)

	def set_display_mode(self, mode):
		assert(mode in [SIMPLE_DISPLAY, DETAILED_DISPLAY])
		self.display_mode = mode

	def run(self, printer_queue, **kargs):
		self.prelude = kargs['mount_info']

		if self.log:
			self.log.write(self.prelude)
		while not self.should_stop:
			obj = printer_queue.get()
			msg_type = obj['msg_type']
			if msg_type == 'kb_hit':
				self.toggle_display_mode()
				self._refresh()
			elif msg_type == 'new_content':
				self.activate(obj['simple'], obj["detailed"])
				self._refresh()
				if self.log:
					self.log.write(self.content[self.display_mode])
					self.log.write('\n')
					self.log.flush()
			elif msg_type == 'quit':
				break

def worker(printer_queue, log, **kargs):
	printer = Printer(log)
	try:
		printer.run(printer_queue, **kargs)
	except:
		if log is not None:
			printer.log.close()
