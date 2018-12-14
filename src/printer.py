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
		self.log = log

	def stop(self):
		self.should_stop = True

	def _refresh(self):
		if self.content:
			util.clear_screen()
			print(self.content[self.display_mode])

	def refresh(self):
		self._refresh()


	def toggle_display_mode(self):
		if self.display_mode == SIMPLE_DISPLAY:
			self.set_display_mode(DETAILED_DISPLAY)
		else:
			self.set_display_mode(SIMPLE_DISPLAY)

	def set_display_mode(self, mode):
		assert(mode in [SIMPLE_DISPLAY, DETAILED_DISPLAY])
		self.display_mode = mode
		self.refresh()

	def activate(self, simple_content, detailed_content):
		self.content = (simple_content, detailed_content)


	def run(self, printer_queue):
		output = self.log
		if output:
			log = open(output, "w")
		while not self.should_stop:
			obj = printer_queue.get()
			msg_type = obj['msg_type']
			if msg_type == 'kb_hit':
				self.toggle_display_mode()
				self._refresh()
			elif msg_type == 'new_content':
				self.activate(obj['simple'], obj["detailed"])
				self._refresh()
				if output:
					log.write(self.content[self.display_mode])
		if output:
			log.close()

def worker(printer_queue, log):
	printer = Printer(log)
	printer.run(printer_queue)
