import vision as Vision
import webserver as Server
import preferences as Prefs
import time
import numpy as np
from threading import Thread
from multiprocessing import Process, Value, Pipe

import ctypes
import cv2
import sys

frequency = 100.0
stream_timeout = 3
#v = Value(ctypes.c_char_p, "S T R I G G")
parent_c, child_c = Pipe()

stream_timestamp = time.time()

def init():
	global proc
	#print(type(v))
	proc = Process(target=Server.run, args=(child_c,))

	proc.start()
	Vision.init()
	Vision.start()
	start_threads()

def update():
	pass


def receive_webserver_data():
	global parent_c
	global stream_timestamp
	while True:
		try:
			a = parent_c.recv()
			Vision.current_prefs = a["prefs"]
			stream_timestamp = a["stream_timestamp"]
			pass
		except EOFError:
			print("Error receiving preferences data from webserver process")

def pass_stream_data():
	while True:
		if (time.time() - stream_timestamp < stream_timeout):
			raw_img = Vision.current_frame
			filtered_img = Vision.filter(raw_img)
			jpeg = Vision.encode_jpg(filtered_img, True)
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

thread_map = [receive_webserver_data, pass_stream_data]

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