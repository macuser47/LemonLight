from __future__ import print_function
import sys

from flask import Flask, render_template, request
import numpy as np
import cv2

#initialize flask server
app = Flask(__name__)

#stream simulator
img = cv2.cvtColor(cv2.imread("image.jpeg", cv2.IMREAD_COLOR), cv2.COLOR_BGR2HSV)

#confiugration settings
hsv_min = np.array([13, 157, 158])
hsv_max = np.array([255, 255, 255])

'''
Render main configuration page
'''
@app.route("/")
def main_page():
	return render_template("index.html")

'''
Update configuration settings based on request from client
'''
@app.route("/fuck", methods = ["GET"])
def process_data():
	filter(img)
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
	cv2.imwrite("static/new.png", thresholdImage)
	return thresholdImage


'''
Gets the current frame from the camera in HSV
'''
def current_frame():
	cap = cv2.VideoCapture(0)
	ret, frame = cap.read()
	return cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

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