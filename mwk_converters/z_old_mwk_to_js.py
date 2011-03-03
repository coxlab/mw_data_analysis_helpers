#!/usr/bin/env python

import logging, os, sys
import sqlite3
import json

import mwk


logging.basicConfig(level=logging.DEBUG)

eventsToUse = ['success','failure','ignore']
#eventsBlacklist = ['#annouceCurrentState']

# parse command line arguments
logging.debug("Parsing command line arguments")
if len(sys.argv) == 3:
    inFile = sys.argv[1]
    outFile = sys.argv[2]
elif len(sys.argv) == 2:
    inFile = sys.argv[1]
    outFile = '%s.js' % os.path.splitext(os.path.basename(inFile))[0]
else:
    print "Usage: %s input_mwk_file (output_js_file)" % __file__
    sys.exit(1)

# open up and read mwks file
logging.debug("opening and reading mwks file: %s" % inFile)
m = mwk.MWKFile(inFile)
m.open()

# open output file
logging.debug("openning output file: %s" % outFile)
oFile = open(outFile,"w")
dataName = os.path.splitext(os.path.basename(inFile))[0]
oFile.write("var %s = [\n" % dataName)
codec = m.codec

# add events to file
logging.debug("adding events to file")
# cmd = "insert into %s values(?,?,?)" % tableName
for eventName in eventsToUse:
    if eventName not in codec.values():
        logging.warning("Event %s not in codec" % eventName)
        continue
    events = m.get_events(codes=[eventName])
    if len(events) == 0:
        logging.warning("No %s events found" % eventName)
        continue
    oFile.write('{name:"%s", times:\n[' % eventName)
    for event in events:
        oFile.write('%i,' % event.time)
    oFile.write('], values:\n[')
    for event in events:
        oFile.write('%s,' % event.value)
    oFile.write(']},\n')

# write footer
oFile.write("];")

logging.debug("cleaning up")
# close database connection
oFile.close()

# close mworks file
m.close()

# exit nicely
sys.exit(0)