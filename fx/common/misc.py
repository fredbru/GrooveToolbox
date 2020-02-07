from __future__ import print_function
import xml.dom.minidom
from xml.dom.minidom import Node
import codecs
import os
import shutil
import re
import unicodedata
import csv

import sys, csv, codecs

PY3 = sys.version > '3'


# === GENERIC FUNCTIONS ===

#####
# set up globals for unicode character stripping

if PY3:
    #python 3.1.2 version
    all_chars = (chr(i) for i in range(0x10000))
    control_chars = ''.join(c for c in all_chars if unicodedata.category(c) == 'Cc')
    #control_chars = ''.join(map(unichr, range(0,32) + range(127,0x10000)))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))
else:
    #python 2.6.1 version
    all_chars = (unichr(i) for i in xrange(0x10000))
    control_chars = ''.join(map(unichr, range(0,32)))
    control_char_re = re.compile('[%s]' % re.escape(control_chars))


#####
# strips out non-printable (ASCII) characters - can be used to strip out unicode chars
# @param s The string to strip

def stripControl(s):
    if PY3:
        #python 3.1.2 version
        return control_char_re.sub('|', s)
    else:
        return control_char_re.sub('|', s)

#####
# parse a CSV file

#####
# Concatenates multiple terms into comma separated value
def concatenateTerms(existing, new):
        if new == "":
                return existing
        if existing == "":
                return new
        return existing + "," + new

