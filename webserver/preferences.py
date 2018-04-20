import json
import re

#defines required elements for a properly formatted
#Preferences file
format = {
	"area_max":int,
	"area_min":float,
	"aspect_max":int,
	"aspect_min":int,
	"blue_balance":int,
	"calibration_type":int,
	"contour_grouping":int,
	"contour_sort_final":int,
	"convexity_max":int,
	"convexity_min":int,
	"cross_a_a":int,
	"cross_a_x":int,
	"cross_a_y":int,
	"cross_b_a":int,
	"cross_b_x":int,
	"cross_b_y":int,
	"desc":unicode,
	"desired_contour_region":int,
	"exposure":int,
	"hue_max":int,
	"hue_min":int,
	"image_flip":int,
	"image_source":int,
	"img_to_show":int,
	"red_balance":int,
	"sat_max":int,
	"sat_min":int,
	"val_max":int,
	"val_min":int
}

'''
Loads Preferences from vpr file and packs into dictionary
'''
def load(file):
	f = open(file, "r")
	prefs = json.load(f)
	f.close()

	if (not check_integrity(prefs, format)):
		raise InvalidPreferencesException("Preferences improperly formatted")

	return prefs


'''
Loads Preferences from non-json legacy vpr files
'''
def load_legacy(file):
	f = open(file, "r")
	parsed = re.split("\r\n|\r|\n|:", f.read())
	f.close()

	#shave extra newlines off the end (number is inconsistent)
	for line in reversed(parsed):
		if (line == ""):
			parsed = parsed[:-1]
		else:
			break

	prefs = {}
	try:
		for index, elem in enumerate(parsed):
			if (index % 2 == 0):
				prefs[elem] = format[elem]( parsed[index+1] )
	except:
		raise InvalidPreferencesException("Legacy Preferences improperly formatted")

	if (not check_integrity(prefs, format)):
		raise InvalidPreferencesException("Legacy Preferences improperly formatted")

	return prefs

'''
Saves Preferences to json-encoded vpr
'''
def save(prefs, file):
	if (not check_integrity(prefs, format)):
		raise InvalidPreferencesException("Preferences improperly formatted")

	f = open(file, "w+")
	f.write( json.dumps(prefs, sort_keys=True, indent=4, separators=(',', ': ')) )
	f.close()

'''
Save Preferences to non-json legacy vpr
'''
def save_legacy(prefs, file):
	if (not check_integrity(prefs, format)):
		raise InvalidPreferencesException("Preferences improperly formatted")

	f = open(file, "w+")
	for key, val in sorted( prefs.iteritems() ):
		f.write(key + ":" + str(val) + "\r\n")

	f.close()

'''
Checks integrity of preferences dict and returns false
if elements are missing or of incorrect type
'''
def check_integrity(data, format):
	correct_format = True
	#https://stackoverflow.com/a/3294899
	for key, value in format.iteritems():
		correct_format &= (key in data)

		if (not correct_format):
			print "KEY ERROR: " + key
			break

		correct_format &= (type(data[key]) == value)

		if (not correct_format):
			print "VALUE ERROR (" + key + "): Expected " + value + ", got " + str(type(data[key])) + "for value " + str(data[key])
			break

	return correct_format


class InvalidPreferencesException(Exception):
	pass