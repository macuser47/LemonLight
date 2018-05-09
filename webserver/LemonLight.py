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

#globals
stream_timestamp = time.time()
app_prefs = Prefs.load_app_prefs("app.prefs")
stream_active = False
current_threshold_image = None
current_contours = []

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

def compute_contour_data():
	global current_threshold_image
	global current_contours
	while True:
		current_threshold_image, _, current_contours, contours_found = Vision.filter( Vision.current_frame )

		if (not contours_found):
			print("[" + str(time.time())[:10] + "] WARNING: NO CONTOURS FOUND")
			NT.push({
				"tv": 0,
				"tx": 0,
				"ty": 0,
				"ta": 0,
				"ts": 0,
				"tl": 0.0
			})
			continue

		#construct main NT response
		main_contour, main_box = current_contours[0]
		nt_data = {
			"tv": 1,
			"tx": int( main_box[0][0] ), #TODO: scale to angles
			"ty": int( main_box[0][1] ),
			"ta": int( cv2.contourArea(main_contour) ),
			"ts": int( main_box[2] ),
			"tl": 0.0 #TODO:latency calculation
		}

		pprint.pprint(nt_data)

		#construction secondary contour responses
		contours = []
		for contour, box in current_contours[1:]:
			contour_data = {
				"tx": int( box[0][0] ),
				"ty": int( box[0][1] ),
				"ta": int( cv2.contourArea(contour) ),
				"ts": int( box[2] ),
				"cx": int( box[0][0] ),
				"cy": int( box[0][1] )
			}
			contours.append(contour_data)

		NT.push(nt_data)
		NT.push_contours_raw(contours)



def receive_webserver_data():
	global parent_c
	global stream_timestamp
	global app_prefs
	while True:
		try:
			mp_buffer = parent_c.recv() #note that recv() will wait until data is available before proceeding
			Vision.current_prefs = mp_buffer["prefs"]
			stream_timestamp = mp_buffer["stream_timestamp"]
			app_prefs = mp_buffer["app_prefs"]
		except EOFError:
			print("Error receiving preferences data from webserver process")


def pass_stream_data():
	global stream_active
	global current_threshold_image
	global current_contours
	while True:
		stream_active = (time.time() - stream_timestamp < stream_timeout)
		if (stream_active):
			#output based on prefs
			if ((app_prefs["view_mode"] == 1) & (not (current_threshold_image is None))): #TODO: break thresholding into independent function - it's lightweight
				jpeg = Vision.encode_jpg(current_threshold_image, True) #Should these be encoded in a parallel thread? Perhaps.
			else:
				new_img = Vision.draw_contours(Vision.current_frame, current_contours)
				jpeg = Vision.encode_jpg(new_img, False)

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

thread_map = [receive_webserver_data, pass_stream_data, compute_contour_data]

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