#!/usr/bin/env python
"""
Convert a mworks data file to hdf5 with structure:

root ->
  <session> ->
    codec [code, name]
    events [code, time, index]
    values [vlstring]

where events.index defines the corresponding value item for a given event
so... events[0].value == values[events[0].index]
"""


import json, logging, os, sys

import tables

import mworks.data as mwk

codecNameLen = 32

class Event(tables.IsDescription):
    code = tables.UInt32Col()
    time = tables.UInt64Col()
    index = tables.UInt64Col()
    # value = tables.StringCol(512)
    #value = tables.Col.from_atom(, tables.VLStringAtom())

class CodecEntry(tables.IsDescription):
    code = tables.UInt32Col()
    name = tables.StringCol(codecNameLen)
    #value = tables.VLStringAtom()

# =================================

logging.basicConfig(level=logging.DEBUG)

eventsBlacklist = []#'#announceCurrentState','#codec', '#systemEvent', '#components', '#termination']

# parse command line arguments
logging.debug("Parsing command line arguments")
if len(sys.argv) == 3:
    inFile = sys.argv[1]
    outFile = sys.argv[2]
elif len(sys.argv) == 2:
    inFile = sys.argv[1]
    outFile = '%s.h5' % os.path.splitext(os.path.basename(inFile))[0]
else:
    print "Usage: %s input_mwk_file (output_h5_file)" % __file__
    sys.exit(1)

# open up and read mwks file
logging.debug("opening and reading mwks file: %s" % inFile)
m = mwk.MWKFile(inFile)
m.open()
# fix codec
codec = m.codec
codec[0], codec[1], codec[2], codec[3] = ('#codec', '#systemEvent', '#components', '#termination')
revCodec = {}
for k,v in codec.iteritems():
    revCodec[v] = k

# open file for writing
h5file = tables.openFile(outFile, mode = "w", title = "Test file")

# create new group based on the name of the input file
group = h5file.createGroup("/", os.path.splitext(os.path.basename(inFile))[0], 'Data for a session')

# create new table
eventsTable = h5file.createTable(group, 'events', Event, "Events")
codecTable = h5file.createTable(group, 'codec', CodecEntry, "Codec")
valueTable = h5file.createVLArray(group, 'values', tables.VLStringAtom(), "Values", expectedsizeinMB=0.0001)

# add codec to file
logging.debug("Adding codec to file")
codecEntry = codecTable.row
maxLen = 0
maxStr = ""
for (code,name) in codec.iteritems():
    codecEntry['name'] = name
    codecEntry['code'] = code
    if len(name) > maxLen:
        maxLen = len(name)
        maxStr = name
    codecEntry.append()
logging.debug("len(longest_codec_name) = %i : %s" % (maxLen, maxStr))
if maxLen > codecNameLen:
    logging.error("Codec name %s was too long %i > %i" % (maxStr, maxLen, codecNameLen))

# add reverse codec to file # no need for this here

# add events to file
logging.debug("Adding events to file")
codeBlacklist = [revCodec[e] for e in eventsBlacklist]
events = m.get_events()
event = eventsTable.row
maxLen = 0
maxStr = ""
for e in events:
    # logging.debug("\tEvent: %s" % codec[e['code']])
    if e.code in codeBlacklist:
        continue
    event['code'] = e.code
    event['time'] = e.time
    vs = json.dumps(e.value)
    if len(vs) > maxLen:
        maxLen = len(vs)
        maxStr = vs
    event['index'] = len(valueTable)
    valueTable.append(vs)
    # event['value'] = vs
    event.append()

logging.debug("Max value string[%i]: %s" % (maxLen, maxStr))

# Close (and flush) the file
h5file.close()

# close mworks file
m.close()

# exit nicely
sys.exit(0)