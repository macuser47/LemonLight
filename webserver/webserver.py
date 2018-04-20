from __future__ import print_function
import sys

from flask import Flask, render_template, request, Response
import numpy as np
import cv2

import time
import preferences as Prefs

#initialize flask server
app = Flask(__name__)

#stream simulator
img = cv2.cvtColor(cv2.imread("image.jpeg", cv2.IMREAD_COLOR), cv2.COLOR_BGR2HSV)

global cap

#preferences value
current_prefs = Prefs.load("prefs.vpr")

'''
Render main configuration page
'''
@app.route("/")
def main_page():
	return render_template("index.html")

'''
Get mjpg stream
'''
@app.route("/stream.mjpg")
def render_stream():
	setup_camera()
	return Response( #TODO: make this stop gracefully when session ends instead of the thread violently crashing
		generate_stream(),
		mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
	)


'''
Generates individual jpg buffer to send to client
'''
def generate_stream():
	header = "--jpgboundary\nContent-Type: image/jpeg\n\n"
	while True:
		yield header + next_mjpg_frame(filter(current_frame()), True)
		time.sleep(0.03)


'''
Prepares and returns next stream frame
src: HSV frame source
is_binary: if thresholded image (these can't be color space converted)
'''
def next_mjpg_frame(src, is_binary):
	if (not is_binary):
		src = cv2.cvtColor(src, cv2.COLOR_HSV2BGR)
	return cv2.imencode('.jpg', src)[1].tostring();


'''
Update configuration settings based on request from client
'''
@app.route("/fuck", methods = ["GET"])
def process_data():
	data = request.args;
	f_print("Got data " + str(data))

	#sets data values if data properly formatted
	#open to any better way to do this -- dicts maybe?
	if (options_data_valid(data)):	 
		f_print("Request formatted properly!")
		for key, value in data.iteritems():
			current_prefs[key] = Prefs.format[key](value)
	else:
		f_print("Malformed request, ignoring...")

	return "You shouldn't be here....<br>Get the <b><i>fuck</i></b> out."

'''
Checks if incoming GET preference changes are valid
Inverse of Prefs.check_integrity: checks if all elements of data are in format,
rather than all elements of format are in data
'''
def options_data_valid(data): 
	correct_format = True
	for key, value in data.iteritems():
		correct_format &= (key in Prefs.format)

		if (not correct_format):
			break

		try:
			n = Prefs.format[key](value)
		except ValueError:
			correct_format = False

	return correct_format


'''
Performs opencv filter on an image
TODO: Contour filtering based on configuration
'''
def filter(img):
	#TODO: make this look less dumb. map() w/lambda?
	hsv_min = np.array([current_prefs["hue_min"], current_prefs["sat_min"], current_prefs["val_min"]])
	hsv_max = np.array([current_prefs["hue_max"], current_prefs["sat_max"], current_prefs["val_max"]])
	thresholdImage = cv2.inRange(img, hsv_min, hsv_max)
	contoursImg, contours, heirarchy = cv2.findContours(thresholdImage, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
	return thresholdImage


'''
Gets the current frame from the camera in HSV
'''
def current_frame():
	ret, frame = cap.read()
	return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

def setup_camera():
	global cap
	cap = cv2.VideoCapture(0)
	cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320); 
	cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 240);
	cap.set(cv2.CAP_PROP_SATURATION,0.2);
	ret, frame = cap.read()

'''
Prints to flask debug output.
'''
def f_print(str):
	print(str, file=sys.stderr)

'''
start server
'''
if __name__ == "__main__":
	app.run(host='127.0.0.1', port=125, threaded=True, debug=True)