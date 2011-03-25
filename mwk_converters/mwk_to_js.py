#!/usr/bin/env python

import logging, os, sys
import json

#import mwk
import mworks.data as mwk

def mwk_to_js(inFile, outFile, blacklist=[]):
    m = mwk.MWKFile(inFile)
    try:
        m.open()
    except:
        m.reindex()
        m.open()
    # fix codec
    c = m.codec
    c[0], c[1], c[2], c[3] = ('#codec', '#systemEvent', '#components', '#termination')
    
    # open output file
    logging.debug("openning output file: %s" % outFile)
    oFile = open(outFile,"w")
    fileName = os.path.splitext(os.path.basename(inFile))[0]
    codec = m.codec
    revCodec = m.reverse_codec

    # add codec to file
    oFile.write("var codec = {\n")
    for (k,v) in codec.iteritems():
        oFile.write(" %i:'%s'," % (k, v))
    oFile.write("};\n")

    # add reverse codec to file
    oFile.write("var reverseCodec = {\n")
    for (k,v) in revCodec.iteritems():
        oFile.write(" '%s':%i," % (k, v))
    oFile.write("};\n")

    # add events to file
    logging.debug("adding events to file")
    oFile.write("var events = [\n")
    # oFile.write("var %s = [\n" % dataName)
    # cmd = "insert into %s values(?,?,?)" % tableName
    codeBlacklist = [revCodec[e] for e in blacklist]
    events = m.get_events()
    for e in events:
        if e.code in codeBlacklist:
            continue
        oFile.write(" {'code':'%s', 'time':%i, 'value':'%s'},\n" % (e.code, e.time, json.dumps(e.value)))
    oFile.write('];')

    logging.debug("cleaning up")
    # close database connection
    oFile.close()

    # close mworks file
    m.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    # eventsToUse = ['success','failure','ignore']
    eventsBlacklist = ['#announceCurrentState','#codec', '#systemEvent', '#components', '#termination']

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
    mwk_to_js(inFile, outFile, eventsBlacklist)

    # exit nicely
    sys.exit(0)