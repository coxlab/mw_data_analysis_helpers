#!/usr/bin/env python

import logging, os, sys
import sqlite3
import json

#import mwk
import mworks.data as mwk


logging.basicConfig(level=logging.DEBUG)

#eventsBlacklist = ['#announceCurrentState','#codec', '#systemEvent', '#components', '#termination'] # not implemented

# parse command line arguments
logging.debug("Parsing command line arguments")
if len(sys.argv) == 3:
    inFile = sys.argv[1]
    outFile = sys.argv[2]
elif len(sys.argv) == 2:
    inFile = sys.argv[1]
    outFile = '%s.sqlite3' % os.path.splitext(os.path.basename(inFile))[0]
else:
    print "Usage: %s input_mwk_file (output_sqlite3_file)" % __file__
    sys.exit(1)

# open up and read mwks file
logging.debug("opening and reading mwks file: %s" % inFile)
m = mwk.MWKFile(inFile)
m.open()
# fix codec
c = m.codec
c[0], c[1], c[2], c[3] = ('#codec', '#systemEvent', '#components', '#termination')
evs = m.get_events()

# open sqlite3 database
logging.debug("opening sqlite3 database: %s" % outFile)
conn = sqlite3.connect(outFile)
c = conn.cursor()

# # make table to add to data files table
# logging.debug("adding information to db")
# c.execute('''create table datafiles
#     (animal text, day text)''')

# make table for new data
# tableName = os.path.splitext(os.path.basename(inFile))[0]
# cmd = "create table %s (code int, time int, value text)" % tableName
# c.execute(cmd)
c.execute('''create table events
    (code int, time int, value text)''')

# make table for codec
# codecTableName = "%s_codec" % tableName
# cmd = "create table %s (code int, name text)" % codecTableName
# c.execute(cmd)
c.execute('''create table codec
    (code int, name text)''')

# # add information to datafiles table
# animal = tableName.split('_')[0].lower()
# day = tableName.split('_')[1]
# c.execute('''insert into datafiles
#     values(?,?)''', (animal, day))

# add codec to database
codec = m.codec
# cmd = "insert into %s values(?,?)" % codecTableName
for (k,v) in codec.iteritems():
    # c.execute(cmd,(k,v))
    c.execute('''insert into codec values (?,?)''',(k,v))

# add events to database
logging.debug("adding events to db")
# cmd = "insert into %s values(?,?,?)" % tableName
for e in evs:
    # c.execute(cmd, (e.code, e.time, json.dumps(e.value)))
    c.execute('''insert into events
        values(?,?,?)''', (e.code, e.time, json.dumps(e.value)))

logging.debug("cleaning up")
# close database connection
conn.commit()
c.close()

# close mworks file
m.close()

# exit nicely
sys.exit(0)