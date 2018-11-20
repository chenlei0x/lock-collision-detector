#!/usr/bin/env python3
#-*- coding: utf-8 -*-


class Printer():
	def __init__(self):
		self.content = []
		self.mutex = threading.Lock()

		self.sem = threading.Semaphore(value=0)
		self.just_print = None
		super().__init__()

	def activate(self, content):
		self.sem.release()

		self.mutex.acquire()
		self.content.append(content)
		self.mutex.release()

	def refresh(self):
		util.clear_screen()
		if self.just_print:
			print(self.just_print)

	def run():
		while True:
			self.sem.acquire()
			self.mutex.acquire()
			if len(self.content) > 0:
				c = self.content.pop(0)
				print(c)
				self.just_print = c
			self.mutex.release()
