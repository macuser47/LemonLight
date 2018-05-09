import preferences as Prefs
import numpy as np
import cv2
import time
from threading import Thread

global camera_capture
current_frame = cv2.cvtColor(cv2.imread("image.jpeg"), cv2.COLOR_BGR2HSV)
current_prefs = Prefs.load("vprs/prefs0.vpr")

resolution = (320, 240)

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
	x, y = resolution
	camera_capture = cv2.VideoCapture(0)
	camera_capture.set(cv2.CAP_PROP_FRAME_WIDTH, x) 
	camera_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, y)
	ret, frame = camera_capture.read() #capture from camera immediately to force hardware contrast adjustment

'''
Performs opencv filter on an image
TODO: Contour filtering based on configuration
'''
def filter(img):
	#do HSV filtering and get contours
	hsv_min = np.array([current_prefs["hue_min"], current_prefs["sat_min"], current_prefs["val_min"]])
	hsv_max = np.array([current_prefs["hue_max"], current_prefs["sat_max"], current_prefs["val_max"]])
	thresholdImage = cv2.inRange(img, hsv_min, hsv_max)
	contoursImg, contours, heirarchy = cv2.findContours(thresholdImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

	#do contour filtering
	filteredContours = []
	for contour in contours:
		contour_valid = True
		#filter by area
		screen_area = resolution[0] * resolution[1]
		contour_valid &= (current_prefs["area_min"] <= (cv2.contourArea(contour) / screen_area) <= current_prefs["area_max"])
		#filter by aspect ratio
		rect = cv2.minAreaRect(contour)
		if (not (rect[1][1] == 0)):
			aspect_ratio = float(rect[1][0]) / rect[1][1]
			contour_valid &= (current_prefs["aspect_min"] <= aspect_ratio <= current_prefs["aspect_max"])

		if (contour_valid):
			filteredContours.append(
				(contour, rect)
			)
	#sort contours
	#TODO: use contour_sort_final to sort by different modes
	filteredContours = sorted(filteredContours, reverse=True, key=lambda c: cv2.contourArea(c[0]))

	contours_found = len(filteredContours) > 0

	return thresholdImage, contours, filteredContours, contours_found

def draw_contours(base_image, contours):
	new_img = np.copy(base_image)
	aa_rect_color = (0, 0, 255)
	rot_rect_color = (255, 0, 0)
	line_thickness = 2
	for contour in contours:
		cont = contour[0] #TODO: get rid of this crappy hack
		aa_x, aa_y, aa_w, aa_h  = cv2.boundingRect(cont)
		rot_rect = cv2.minAreaRect(cont)
		rot_box = np.int32( cv2.boxPoints(rot_rect) )

		cv2.rectangle(
			new_img, 
			(aa_x, aa_y),
			(aa_x + aa_w, aa_y + aa_h),
			aa_rect_color,
			line_thickness
		)
		cv2.drawContours(
			new_img,
			[rot_box],
			0,
			rot_rect_color,
			line_thickness
		)

	return new_img
		

'''
Prepares and returns next jpeg frame
src: HSV frame source
is_binary: if thresholded image (these can't be color space converted)
'''
def encode_jpg(src, is_binary):
	if (not is_binary):
		src = cv2.cvtColor(src, cv2.COLOR_HSV2BGR)
	return cv2.imencode('.jpg', src)[1].tostring()


def init():
	global active
	active = True

def start():
	camera_thread = Thread(target=camera_update)
	camera_thread.daemon = True
	camera_thread.start()



def camera_update():
	global current_frame
	global active
	print("BEHOLD, A THREAD IS BORN")
	setup_camera()
	while active:
		#print("SCREEE")
		current_frame = camera_read()