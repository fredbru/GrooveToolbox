import os
import sys
import inspect

def addRelativePathToSystemPath(relPath):
    thisFilePath = inspect.getfile(inspect.currentframe())
    thisDir = os.path.split(thisFilePath)[0]
    absPath = os.path.join(thisDir, relPath)
    canonicalPath = os.path.realpath(os.path.abspath(absPath))
    if canonicalPath not in sys.path:
        sys.path.insert(0, canonicalPath)

addRelativePathToSystemPath("modules")

import json
import base64
import requests
import time
import socket
import struct
import subprocess
import re
import glob

# send using the juce IPC message protocol
def sendLuaCodeToBFD(msg):
    print ('Sending LUA to BFD:')
    print (msg)
    #host = "192.168.0.35"
    host = "127.0.0.1"
    port = 0xbfd
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect ((host,port))
        s.send (struct.pack('<I', 0xf2b49e2c)) # magic juce IPC header
        s.send (struct.pack('<I', len(msg)))
        s.send (msg)
        s.close ()
    except socket.error as e:
        print "Failed to send message to BFD - error: ", e.strerror

if __name__ == "__main__":
    cmdargs = str(sys.argv[1:])
    print "args: ", cmdargs
    if len(sys.argv) == 1:
        print "Use: sendLuaCodeToBFD <command>"
    elif len(sys.argv) == 2:
        sendLuaCodeToBFD(sys.argv[1] +'''(bfd)''')
    elif len(sys.argv) == 3:
        sendLuaCodeToBFD(sys.argv[1] +'''(bfd, "''' + sys.argv[2] + '''")''')