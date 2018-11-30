#!/usr/bin/env python3
#-*- coding: utf-8 -*-

import threading
import util

SIMPLE_DISPLAY=0
DETAILED_DISPLAY=1

class Printer():
	def __init__(self):
		self.content = None
		self.mutex = threading.Lock()
		self.sem = threading.Semaphore(value=0)
		self.display_mode = SIMPLE_DISPLAY
		self.should_stop = False

	def stop(self):
		self.should_stop = True
		self.sem.release()

	def _refresh(self):
		if self.content:
			util.clear_screen()
			print(self.content[self.display_mode])

	def refresh(self):
		self.mutex.acquire()
		self._refresh()
		self.mutex.release()

	def set_display_mode(self, mode):
		if mode != SIMPLE_DISPLAY and mode != DETAILED_DISPLAY:
			return
		self.display_mode = mode
		self.refresh()

	def activate(self, simple_content, detailed_content):
		self.sem.release()
		self.mutex.acquire()
		self.content = (simple_content, detailed_content)
		self.mutex.release()


	def run(self, output=None):
		if output:
			log = open(output, "w")
		while not self.should_stop:
			self.sem.acquire()
			self.mutex.acquire()
			if self.content is None:
				self.mutex.release()
				continue
			self._refresh()
			if output:
				log.write(self.content[self.display_mode])
			self.mutex.release()
		if output:
			log.close()
