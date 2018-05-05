from __future__ import print_function
import sys
import time
import cv2
from flask import Flask, render_template, request, Response
import preferences as Prefs
import ctypes
from multiprocessing import Pipe
from threading import Thread


STREAM_FRAMERATE = 30

#preferences value
current_prefs = Prefs.load("prefs.vpr") 

#last requested timestamp for mjpg
stream_timestamp = time.time()

global jpeg_pipe
global jpeg_data
jpeg_data = cv2.imencode('.jpg', cv2.imread("image.jpeg"))[1].tostring()

app = Flask(__name__)


'''
start server
'''
def run(c):
	global jpeg_pipe
	jpeg_pipe = c
	buffer_thread = Thread(target=jpeg_buffer_daemon)
	response_thread = Thread(target=response_daemon)
	buffer_thread.daemon = True
	response_thread.daemon = True
	buffer_thread.start()
	response_thread.start()
	app.run(host='127.0.0.1', port=125, threaded=True, debug=True, use_reloader=False)


def jpeg_buffer_daemon():
	global jpeg_data
	while True:
		try:
			jpeg_data = jpeg_pipe.recv() # Read from the output pipe
		except EOFError:
			print("EOF ERROR IN JPEG BUFFER DAEMON")
			continue

def response_daemon():
	while True:
		#construct response object
		response = {}
		response["stream_timestamp"] = stream_timestamp
		response["prefs"] = current_prefs
		try:
			jpeg_pipe.send(response)
		except EOFError:
			print("EOF ERROR IN RESPONSE DAEMON")
			continue

'''
Render main configuration page
'''
@app.route("/")
def main_page():
	return render_template("index.html")

'''
Get mjpg stream
'''
@app.route("/stream.mjpg", methods=["GET"])
def render_stream():
	f_print("Request Received")
	return Response(
		generate_stream(),
		mimetype="multipart/x-mixed-replace; boundary=jpgboundary"
	)


'''
Generates individual jpg buffer to send to client
'''
def generate_stream():
	global jpeg_data
	global stream_timestamp
	header = "--jpgboundary\nContent-Type: image/jpeg\n\n"
	while True:
		stream_timestamp = time.time()
		yield header + jpeg_data
		time.sleep(1 / float(STREAM_FRAMERATE))


'''
Update configuration settings based on request from client
'''
@app.route("/fuck", methods = ["GET"])
def process_data():
	data = request.args
	f_print("Got data " + str(data))

	#sets data values if data properly formatted
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
Prints to flask debug output.
'''
def f_print(str):
	print(str, file=sys.stderr)
