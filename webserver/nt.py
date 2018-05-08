from networktables import NetworkTables

nt_response_format = {
    "tv":int,
    "tx":int,
    "ty":int,
    "ta":int,
    "ts":int,
    "tl":float
}

nt_input = {
    "ledMode":  int, #as of now unsupported, but still requred for backwards compatibility
    "camMode":  int,
    "pipeline": int,
    "stream":   int, #alternate streaming modes currently unsupported, but compatibility may come later?
    "snapshot": int
}

nt_raw_contour_format = {
    "tx":int,
    "ty":int,
    "ta":int,
    "ts":int,
    "cx":int,
    "cy":int
}

'''
Initializes networktables client with target
Sets the refresh rate to 100hz
'''
def init(host_ip):
    global table
    NetworkTables.initialize(server=host_ip)
    NetworkTables.setUpdateRate(0.010) #set output rate at 100hz
    table = NetworkTables.getTable("lemonlight")

'''
Verifies response dict and puts to networktables
'''
def push(response):
    if (check_schema(response, nt_response_format)):
        for key, value in response.iteritems():
            table.putValue(key, value)
    else:
        print("ERR: Invalid nt push")


'''
Verifies raw contours and puts to networktables
'''
def push_contours_raw(contours):
    schema_valid = True
    for contour in contours:
        schema_valid &= check_schema(contour, nt_raw_contour_format)
    if (schema_valid):
        for index, contour in enumerate(contours):
            for key, value in contour.iteritems():
                table.putValue(key + str(index), value)
    else:
        print("ERR: Invalid nt contours")


'''
Polls networktables for current table data
Formats response as dict
'''
def poll():
    state = {}
    for key, _ in nt_input.iteritems():
        state[key] = table.getValue(key, None)
    return state

'''
Does schema check of dict vs format dict
https://stackoverflow.com/a/45812573
'''
def check_schema(dictionary, format):
    if isinstance(format, dict) and isinstance (dictionary, dict):
        # format is a dict of types or other dicts
        return all(k in dictionary and check_schema(dictionary[k], format[k]) for k in format)
    if isinstance(format, list) and isinstance (dictionary, list):
        # format is list in the form [type or dict]
        return all(check_schema(c, format[0]) for c in dictionary)
    elif isinstance(format, type):
        # format is the type of dictionary
        return isinstance (dictionary, format)
    else:
        # format is neither a dict, nor list, not type
        return False