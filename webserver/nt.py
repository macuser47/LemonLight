from networktables import NetworkTables
import preferences as Prefs

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
    if (Prefs.schema_subset(response, nt_response_format)):
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
        schema_valid &= Prefs.schema_subset(contour, nt_raw_contour_format)
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
