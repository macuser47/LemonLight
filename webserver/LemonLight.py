import vision as Vision
import webserver as Server
import preferences as Prefs
import nt as NT
import time
import numpy as np
from threading import Thread
from multiprocessing import Process, Value, Pipe

import ctypes
import cv2
import sys

import random
import pprint

frequency = 100.0
stream_timeout = 5
parent_c, child_c = Pipe()

stream_timestamp = time.time()

app_prefs = Prefs.load_app_prefs("app.prefs")

def init():
	global proc
	proc = Process(target=Server.run, args=(child_c,))
	proc.start()

	Vision.init()
	Vision.start()

	NT.init("127.0.0.1")
	
	start_threads()

def update():
	pass

def push_nt_pipeline():
	pass

'''
TODO: Do client detection for this thread
'''
def receive_webserver_data():
	global parent_c
	global stream_timestamp
	global app_prefs
	while True:
		try:
			mp_buffer = parent_c.recv()
			Vision.current_prefs = mp_buffer["prefs"]
			stream_timestamp = mp_buffer["stream_timestamp"]
			app_prefs = mp_buffer["app_prefs"]
		except EOFError:
			print("Error receiving preferences data from webserver process")


def pass_stream_data():
	while True:
		if (time.time() - stream_timestamp < stream_timeout):
			raw_img = Vision.current_frame
			filtered_img = Vision.filter(raw_img)
			jpeg = Vision.encode_jpg(raw_img, False)
			parent_c.send(jpeg)
			#print("STREAMING")
		else:
			pass
			#print("NOT STREAMING")


def start_threads():
	global thread_map
	for fun in thread_map:
		thread = Thread(target=fun)
		thread.daemon = True
		thread.start()

thread_map = [receive_webserver_data, pass_stream_data, push_nt_pipeline]

if __name__ == "__main__":
	init()
	try:
		while True:
			update()
			#time.sleep(1 / float(frequency))
	except KeyboardInterrupt:
		Vision.active = False
		proc.terminate()
		parent_c.close()
		child_c.close()
		raise KeyboardInterrupt