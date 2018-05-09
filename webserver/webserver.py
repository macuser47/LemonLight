from __future__ import print_function
import sys
import time
import cv2
from flask import Flask, render_template, request, Response
import preferences as Prefs
import ctypes
from multiprocessing import Pipe
from threading import Thread
import json
import os

STREAM_FRAMERATE = 30

#preferences values
app_prefs = Prefs.load_app_prefs("app.prefs")
current_prefs = Prefs.load("vprs/prefs" + str(app_prefs["default_pipeline"])  + ".vpr2")

#last requested timestamp for mjpg
stream_timestamp = time.time()

global jpeg_pipe
global jpeg_data
jpeg_data = cv2.imencode('.jpg', cv2.imread("image.jpeg"))[1].tostring()

app = Flask(__name__)
app.config["VPR2_UPLOAD_FOLDER"] = "/vprs"
app.config["VPR_UPLOAD_FOLDER"] = "/vprs/legacy"


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
		response["app_prefs"] = app_prefs
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
General immediate event handler for the webserver
'''
@app.route("/the_actual_fuck", methods = ["GET", "POST"])
def handle_events():
	#handle vpr uploads
	if (request.method == "POST"):
		if ("file" in request.files):
			file = request.files["file"]
			extension, extension_valid = validate_extension(file.filename, ["vpr", "vpr2"])
			if (extension_valid):
				if (extension == "vpr2"):
					filename = "prefs" + str(app_prefs["current_pipeline"]) + ".vpr2"
					file.save(os.path.join(app.config['VPR2_UPLOAD_FOLDER'], filename))
				elif (extension == "vpr"): #legacy handling
					filename = "prefs.vpr"
					final_filename = "prefs" + str(app_prefs["current_pipeline"]) + ".vpr2"
					file.save(os.path.join(app.config['VPR_UPLOAD_FOLDER'], filename))
					try:
						Prefs.save( Prefs.load_legacy("/vprs/legacy/prefs.vpr"), final_filename )
					except Prefs.InvalidPreferencesException:
						f_print("Err: Newly uploaded vpr improperly formatted")
						return "File format incomplete or damaged"
	else:
		pass


def validate_extension(filename, extensions):
	extension = filename.rsplit(".", 1)[1].lower()
	return extension, extension in extensions

'''
Update application config settins based on request from client
TODO: Generalize with /fuck implementation: merge onto same url and format?
TODO: Move to POST requests with body instead of GET
Returns application prefs
'''
@app.route("/app_prefs", methods = ["GET"])
def process_app_data():
	global current_prefs
	data = request.args
	if (options_data_valid(data, Prefs.application_prefs_format)):
		f_print("App prefs: Request formatted properly!")
		for key, value in data.iteritems():
			app_prefs[key] = Prefs.application_prefs_format[key](value)

		#Update local file every time a change is made
		Prefs.save_app_prefs(app_prefs, "app.prefs")

		#Do server-specific event handling for prefs data
		if ("current_pipeline" in data):
			#load new pipeline
			current_prefs = Prefs.load("vprs/prefs" + str(app_prefs["current_pipeline"])  + ".vpr2")

	else:
		f_print("App prefs: Malformed request, ignoring...")

	return json.dumps( app_prefs )
	#return "Welcome to <strong>the internet</strong><br>Just kidding, you're on LAN.<br><strong>B A M B O O Z L E D</strong>"


'''
Update configuration settings based on request from client
Returns vpr prefs
'''
@app.route("/fuck", methods = ["GET"])
def process_data():
	data = request.args
	f_print("Got data " + str(data))

	#sets data values if data properly formatted
	if (options_data_valid(data, Prefs.prefs_format)):	 
		f_print("Request formatted properly!")
		for key, value in data.iteritems():
			current_prefs[key] = Prefs.prefs_format[key](value)
		#Update local file every time a change is made
		Prefs.save(current_prefs, "vprs/prefs" + str(app_prefs["current_pipeline"]) + ".vpr2")
	else:
		f_print("Malformed request, ignoring...")

	return json.dumps( current_prefs )
	#return "You shouldn't be here....<br>Get the <b><i>fuck</i></b> out."

'''
Checks if incoming GET preference changes are valid
Separate from Prefs.schema_subset because casts from string are required.
'''
def options_data_valid(data, schema): 
	correct_format = True
	for key, value in data.iteritems():
		correct_format &= (key in schema)

		if (not correct_format):
			break

		try:
			n = schema[key](value)
		except ValueError:
			correct_format = False

	return correct_format


'''
Prints to flask debug output.
'''
def f_print(str):
	print(str, file=sys.stderr)