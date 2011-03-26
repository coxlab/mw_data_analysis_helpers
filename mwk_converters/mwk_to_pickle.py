#!/usr/bin/env python

import logging, os, sys

import json
import cPickle as pickle

import mworks.data as mwk

def mwk_to_pickle(inFile, outFile, blacklist=[]):
    m = mwk.MWKFile(inFile)
    try:
        m.open()
    except:
        m.reindex()
        m.open()
    
    # fix codec
    codec = m.codec
    codec[0], codec[1], codec[2], codec[3] = ('#codec', '#systemEvent', '#components', '#termination')
    revCodec = {}
    for k,v in codec.iteritems():
        revCodec[v] = k
    
    # open output file for writing
    oFile = open(outFile, 'w')
    
    # add data to output file
    events = m.get_events()
    codeBlacklist = [revCodec[e] for e in blacklist]
    pData = {'codec': codec, 'revCodec': revCodec, 'events': []}
    for e in events:
        if e.code in codeBlacklist:
            continue
        pData['events'].append({'code': e.code, 'time': e.time, 'value': json.dumps(e.value)})
    pickle.dump(pData, oFile, protocol=2)
    
    # Close the file
    oFile.close()
    
    # close mworks file
    m.close()

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    
    eventsBlacklist = ['#announceCurrentState','#codec', '#systemEvent', '#components', '#termination']
    
    # parse command line arguments
    logging.debug("Parsing command line arguments")
    if len(sys.argv) == 3:
        inFile = sys.argv[1]
        outFile = sys.argv[2]
    elif len(sys.argv) == 2:
        inFile = sys.argv[1]
        outFile = '%s.p' % os.path.splitext(os.path.basename(inFile))[0]
    else:
        print "Usage: %s input_mwk_file (output_h5_file)" % __file__
        sys.exit(1)
    
    # open up and read mwks file
    logging.debug("opening and reading mwks file: %s" % inFile)
    mwk_to_pickle(inFile, outFile, eventsBlacklist)
    
    # m = mwk.MWKFile(inFile)
    # m.open()
    # # fix codec
    # c = m.codec
    # c[0], c[1], c[2], c[3] = ('#codec', '#systemEvent', '#components', '#termination')
    # codec = m.codec
    # revCodec = m.reverse_codec
    # 
    # # open file for writing
    # oFile = open(outFile, 'w')
    # 
    # # add data to file
    # events = m.get_events()
    # codeBlacklist = [revCodec[e] for e in eventsBlacklist]
    # pData = {'codec': codec, 'revCodec': revCodec, 'events': []}
    # for e in events:
    #     if e.code in codeBlacklist:
    #         continue
    #     pData['events'].append({'code': e.code, 'time': e.time, 'value': json.dumps(e.value)})
    # pickle.dump(pData, oFile, protocol=2)
    # 
    # # Close the file
    # oFile.close()
    # 
    # # close mworks file
    # m.close()
    
    # exit nicely
    sys.exit(0)