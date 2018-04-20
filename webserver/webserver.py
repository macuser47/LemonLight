from __future__ import print_function
import sys

from flask import Flask, render_template, request, Response
import numpy as np
import cv2

import time

#initialize flask server
app = Flask(__name__)

#stream simulator
img = cv2.cvtColor(cv2.imread("image.jpeg", cv2.IMREAD_COLOR), cv2.COLOR_BGR2HSV)

#confiugration settings
hsv_min = np.array([3, 59, 47])
hsv_max = np.array([33, 151, 131])

global cap

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
	return Response(
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
	format = {"parameter":str, "value":int}

	#sets data values if data properly formatted
	#open to any better way to do this -- dicts maybe?
	if (dict_valid(data, format)):	
		f_print("Request formatted properly!")
		p = data["parameter"]
		d = data["value"]
		if (p == "H_MIN"):
			hsv_min[0] = int(d)
		if (p == "H_MAX"):
			hsv_max[0] = int(d)
		if (p == "S_MIN"):
			hsv_min[1] = int(d)
		if (p == "S_MAX"):
			hsv_max[1] = int(d)
		if (p == "V_MIN"):
			hsv_min[2] = int(d)
		if (p == "V_MAX"):
			hsv_max[2] = int(d)
	else:
		f_print("Malformed request, ignoring...")

	return "You shouldn't be here....<br>Get the <b><i>fuck</i></b> out."

'''
Checks validity of dictionary based on format dictionary
'''
def dict_valid(data, format):
	correct_format = True
	#https://stackoverflow.com/a/3294899
	for key, value in format.iteritems():
		correct_format &= (key in data)

		if (not correct_format):
			break

		try:
			n = value(data[key])
		except ValueError:
			correct_format = False

	return correct_format

'''
Performs opencv filter on an image
TODO: Contour filtering based on configuration
'''
def filter(img):
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
	app.run(host='127.0.0.1', port=125, debug=True)