import json
import re

#defines required elements for a properly formatted
#Preferences file
prefs_format = {
	"area_max":float,
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

application_prefs_format = {
	"target_ip":unicode,
	"default_pipeline":int,
	"current_pipeline":int,
	"view_mode":int
}

'''
Loads Application Prefernces from pref file and packs into dictionary
'''
def load_app_prefs(file):
	return load_format(file, application_prefs_format)

'''
Loads Preferences from vpr file and packs into dictionary
'''
def load(file):
	return load_format(file, prefs_format)

'''
Generalized method to load json file based on preferences schema
'''
def load_format(file, schema):
	f = open(file, "r")
	prefs = json.load(f)
	f.close()

	if (not schema_match(prefs, schema)):
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
				prefs[elem] = prefs_format[elem]( parsed[index+1] )
	except:
		raise InvalidPreferencesException("Legacy Preferences improperly formatted")

	if (not schema_match(prefs, prefs_format)):
		raise InvalidPreferencesException("Legacy Preferences improperly formatted")

	return prefs

'''
Save Appliction preferences to prefs
'''
def save_app_prefs(prefs, file):
	save_format(prefs, file, application_prefs_format)

'''
Saves Preferences to json-encoded vpr
'''
def save(prefs, file):
	save_format(prefs, file, prefs_format)

'''
Generalized method to save file based on schema
'''
def save_format(prefs, file, schema):
	if (not schema_match(prefs, schema)):
		raise InvalidPreferencesException("Preferences improperly formatted")

	f = open(file, "w+")
	f.write( json.dumps(prefs, sort_keys=True, indent=4, separators=(',', ': ')) )
	f.close()

'''
Save Preferences to non-json legacy vpr
'''
def save_legacy(prefs, file):
	if (not schema_match(prefs, prefs_format)):
		raise InvalidPreferencesException("Preferences improperly formatted")

	f = open(file, "w+")
	for key, val in sorted( prefs.iteritems() ):
		f.write(key + ":" + str(val) + "\r\n")

	f.close()


'''
Checks if dict implements all elements in a schema
Additional elements are allowed
Allows None values
https://stackoverflow.com/a/45812573
'''
def schema_match(dictionary, schema):
    if isinstance(schema, dict) and isinstance (dictionary, dict):
        # schema is a dict of types or other dicts
        return all(k in dictionary and schema_match(dictionary[k], schema[k]) for k in schema)
    if isinstance(schema, list) and isinstance (dictionary, list):
        # schema is list in the form [type or dict]
        return all(schema_match(c, schema[0]) for c in dictionary)
    elif isinstance(schema, type):
        # schema is the type of dictionary
        return isinstance (dictionary, schema) or (dictionary is None)
    else:
        # schema is neither a dict, nor list, not type
        return False

'''
Checks if dictionary is strictly a subset of a schema
No additional elements are allowed
'''
def schema_subset(dictionary, schema):
    if isinstance(schema, dict) and isinstance (dictionary, dict):
        # schema is a dict of types or other dicts
		return all(k in schema and schema_match(dictionary[k], schema[k]) for k in dictionary)
    if isinstance(schema, list) and isinstance (dictionary, list):
        # schema is list in the form [type or dict]
        return all(schema_match(c, schema[0]) for c in dictionary)
    elif isinstance(schema, type):
        # schema is the type of dictionary
		print(isinstance (dictionary, schema) or (dictionary is None))
		return isinstance (dictionary, schema) or (dictionary is None)
    else:
        # schema is neither a dict, nor list, not type
        return False

'''
Checks if dict implements all elements in a schema
No additional elements are allowed
Allows None values
'''
def schema_match_strict(dictionary, schema):
	return schema_subset(dictionary, schema) and schema_match(dictionary, schema)

class InvalidPreferencesException(Exception):
	pass