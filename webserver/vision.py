import preferences as Prefs
import numpy as np
import cv2
import time
from threading import Thread

global camera_capture
current_frame = cv2.cvtColor(cv2.imread("image.jpeg"), cv2.COLOR_BGR2HSV)
current_prefs = Prefs.load("prefs.vpr")

active = False
'''
Gets the current frame from the camera in HSV
'''
def camera_read():
	ret, frame = camera_capture.read()
	return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

'''
Initializes camera source
'''
def setup_camera():
	global camera_capture
	camera_capture = cv2.VideoCapture(0)
	camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 320) 
	camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 240)
	ret, frame = camera_capture.read()

'''
Performs opencv filter on an image
TODO: Contour filtering based on configuration
'''
def filter(img):
	hsv_min = np.array([current_prefs["hue_min"], current_prefs["sat_min"], current_prefs["val_min"]])
	hsv_max = np.array([current_prefs["hue_max"], current_prefs["sat_max"], current_prefs["val_max"]])
	thresholdImage = cv2.inRange(img, hsv_min, hsv_max)
	contoursImg, contours, heirarchy = cv2.findContours(thresholdImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	return thresholdImage


'''
Prepares and returns next jpeg frame
src: HSV frame source
is_binary: if thresholded image (these can't be color space converted)
'''
def encode_jpg(src, is_binary):
	if (not is_binary):
		src = cv2.cvtColor(src, cv2.COLOR_HSV2BGR)
	jpeg = cv2.imencode('.jpg', src)[1].tostring();
	return jpeg


def init():
	global active
	active = True

def start():
	return Thread(target=update).start()

def update():
	global current_frame
	global active
	print("BEHOLD, A THREAD IS BORN")
	setup_camera()
	while active:
		#print("SCREEE")
		current_frame = camera_read()