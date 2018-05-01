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

def update():
	global stream_timestamp
	#do vision processing
	raw_img = Vision.current_frame
	filtered_img = Vision.filter(raw_img)

	#output to NT (todo)
	#cv2.imshow("", raw_img)
	#cv2.waitKey(0)

	#check server
	if (time.time() - stream_timestamp < stream_timeout):
		jpeg = Vision.encode_jpg(filtered_img, True)
		parent_c.send(jpeg)
		print("STREAMING")
	else:
		print("NOT STREAMING")

	#create custom string with length param to allow for 0x00 in cstring



	try:
		a = parent_c.recv()
		#print("Stamp: " + str(a["stream_timestamp"]))
		Vision.current_prefs = a["prefs"]
		stream_timestamp = a["stream_timestamp"]
		pass
	except EOFError:
		print("Error receiving preferences data from webserver process")

	#print("passed")
	#print(v.value.decode("hex"))
	#print(ctypes.string_at(ctypes.create_string_buffer(jpeg), length).encode("hex"))

	#raise KeyboardInterrupt

	#print(Vision.encode_jpg(raw_img, False).encode("hex"))

	#print Server.jpeg_data




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