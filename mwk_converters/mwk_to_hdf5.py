#!/usr/bin/env python

import logging, os, sys

import tables

import mworks.data as mwk


class Event(tables.IsDescription):
    code = tables.UInt32Col()
    time = tables.UInt64Col()
    value = tables.StringCol()
    #value = tables.Col.from_atom(, tables.VLStringAtom())

class CodecEntry(tables.IsDescription):
    code = tables.UInt32Col()
    name = tables.StringCol()
    #value = tables.VLStringAtom()

# =================================

logging.basicConfig(level=logging.DEBUG)

eventsBlacklist = ['#announceCurrentState','#codec', '#systemEvent', '#components', '#termination']

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

# create new group
group = h5file.createGroup("/", 'session', 'Data for a session')

# create new table
eventsTable = h5file.createTable(group, 'events', Event, "Events")
codecTable = h5file.createTable(group, 'codec', CodecEntry, "Codec")

# add codec to file
codecEntry = codecTable.row
for (code,name) in codec.iteritems():
    codecEntry['name'] = name
    codecEntry['code'] = code
    codecEntry.append()

# add reverse codec to file # no need for this here

# add events to file
codeBlacklist = [revCodec[e] for e in eventsBlacklist]
events = m.get_events()
event = eventsTable.row
for e in events:
    if e.code in codeBlacklist:
        continue
    event['code'] = e.code
    event['time'] = e.time
    event['value'] = json.dumps(e.value)
    event.append()

# Close (and flush) the file
h5file.close()

# close mworks file
m.close()

# exit nicely
sys.exit(0)