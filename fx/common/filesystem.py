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
# scan a folder on disk running fn for each matching file
# @param srcfolder root path to scan
# @param match wildcard string of files to process, e.g. *.* or *.bfd2pal
# @param fn A function taking the name of the file and an XML document node, and processing it
# @retval Number of files found

def walkTree(srcfolder, match, fn):
        count = 0
        for dir, subdirs, files in os.walk(srcfolder):
                for file in files:
                        path = os.path.join(dir, file)
                        try:
                                if re.search(match, path):
                                        walkFile(srcfolder, path, fn)
                                        count += 1
                        except:
                                print ("Exception at path: ", path)
                                raise
        return count

#####
# scan a folder on disk checking fn returns True for each matching file
# @param srcfolder root path to scan
# @param match wildcard string of files to process, e.g. *.* or *.bfd2pal
# @param fn A function taking an XML document node, should return True if okay, False if not

def checkTree(srcfolder, match, fn):
        for dir, subdirs, files in os.walk(srcfolder):
                for file in files:
                        path = os.path.join(dir, file)
                        if re.search(match, path):
                                if checkFile(path, fn):
                                        print (path, " ok")
                                else:
                                        print (path, " *** FAIL ***")
                        else:
                                print ("ignoring ", path)

#####
# scan two folders on disk checking fn returns True for each matching file
# @param srcfolder root path to scan
# @param match wildcard string of files to process, e.g. *.* or *.bfd2pal
# @param fnGetSecondPath A function path -> path to get the path of the file to compare against the first file
#                        This function should return None if it encounters that same comparison file
# @param fn A function taking two XML document nodes, should return True if okay, False if not

def compareTree(srcfolder0, match, fnGetSecondPath, fn):
        if not os.path.exists(srcfolder0):
                raise Exception('Folder not found ' + srcfolder0);

        for dir, subdirs, files in os.walk(srcfolder0):
                for file in files:
                        path0 = os.path.join(dir, file)
                        if re.search(match, path0):
                                path1 = fnGetSecondPath(path0)
                                if path1 != None:
                                        if compareFiles(path0, path1, fn):
                                                print (path0, " ok")
                                        else:
                                                print (path0, " *** FAIL ***")
                                else:
                                        print ("ignoring ", path0)

                        else:
                                print ("ignoring ", path0)

#####
# scan a file on disk checking fn against the file
# @param file path to scan
# @param fn A function taking an XML document node, should return True if okay, False if not


def checkFile(file, fn):
        doc = xml.dom.minidom.parse(file)
        return fn(doc)

#####
# compare two XML files on disk
# @param file0 path to first file
# @param file1 path to second file
# @param fn A function taking 2 XML document nodes, should return True if okay, False if not

def compareFiles(file0, file1, fn):
        doc0 = xml.dom.minidom.parse(file0)
        doc1 = xml.dom.minidom.parse(file1)
        return fn(doc0, doc1)

#####
# scan a file on disk running fn against the file
# @param file path to scan
# @param fn A function taking the filename and an XML document node

def walkFile(root, path, fn):
        doc = xml.dom.minidom.parse(path)
        fn(root, path, doc)

#####
# scan a folder on disk applying a function to the xml of each matching file
# a folder will be created for the processed output files, this folder will
# also include copies of unprocessed files
# @param srcfolder Root path to scan
# @param match Wildcard string of files to process, e.g. *.* or *.bfd2pal
# @param fn A function taking an XML document node as input which it processes in place, no return value
# @param dstfolder Path to output folder
# @retval count Number of files processed

def fixTree(srcfolder, match, fn, dstfolder):

        # create a temporary copy of the folder to process
        tmpfolder = srcfolder + ".tmp"
        shutil.rmtree(tmpfolder, True)
        shutil.copytree(srcfolder, tmpfolder)

        # recurse the temp folder, applying fn to each matching file in turn
        count = 0
        for dir, subdirs, files in os.walk(tmpfolder):
                for file in files:
                        path = os.path.join(dir, file)
                        if re.search(match, path):
                                print ("processing ", path)
                                fixFile(path, fn)
                                count += 1
                                print ("done")
                        else:
                                print ("ignoring ", path)

        # move the temp folder to its final name
        shutil.rmtree(dstfolder, True)
        shutil.move(tmpfolder, dstfolder)
        return count
        
#####
# scan a folder on disk applying a function to the xml of each matching file
# a folder will be created for the processed output files, this folder will
# also include copies of unprocessed files
# @param srcfolder Root path to scan
# @param match Wildcard string of files to process, e.g. *.* or *.bfd2pal
# @param fn A function taking an XML document node as input which it processes in place, no return value
# @param suffix for output XML file (next to original)
# @retval count Number of files processed

def fixTreeInPlace(srcfolder, match, fn, suffix):

        # recurse the temp folder, applying fn to a copy of each matching file in turn
        count = 0
        for dir, subdirs, files in os.walk(srcfolder):
                for file in files:
                        path = os.path.join(dir, file)
                        if re.search(match, path):
                                dstpath = path + suffix
                                print ("processing ", path, " -> ", dstpath)
                                if dstpath != path:
                                        shutil.copyfile(path, dstpath)
                                if (fixFileInPlace(srcfolder, path, dstpath, fn) == False) and dstpath != path:
                                        shutil.deletefile(dstpath)
                                count += 1
#                                print ("done")
#                        else:
#                                print ("ignoring ", path)

        return count
        
#####
# apply a function to the xml of a file on disk in-place
# @param file File to process - will be overwritten with processed output
# @param fn A function taking an XML document node as input which it processes in place, no return value

def fixFileInPlace(rootFolder, origfile, actualfile, fn):
        
        # parse file into xml, and apply fn to the xml
        doc = xml.dom.minidom.parse(actualfile)
        success = fn(rootFolder, origfile, doc)

        if success == True:
                # strip the xml prolog from the output xml (BFD2 seems to cope if you leave it in, but remove for safety)
                stringrep = doc.toxml().replace("<?xml version=\"1.0\" ?>","")

                # write the xml back to the file
                f = codecs.open(actualfile, "w", "utf-8")
                f.write(stringrep);
                f.close()

        return success

#####
# scan a folder on disk transforming the filenames
# @param srcfolder Root path to scan
# @param match Wildcard string of files to process, e.g. *.* or *.bfd2pal
# @param fn A function converting the old filename to the new one
# @retval count Number of files processed

def renameTreeInPlace(srcfolder, match, fn):

        # recurse the temp folder, applying fn to a copy of each matching file in turn
        count = 0
        for dir, subdirs, files in os.walk(srcfolder):
                for file in files:
                        path = os.path.join(dir, file)
                        if re.search(match, path):
                                dstpath = fn(path)
                                print ("renaming ", path, " -> ", dstpath)
                                if dstpath != path:
                                        shutil.move(path, dstpath)
                                count += 1
        return count
        
#####
# apply a function to the xml of a file on disk in-place
# @param file File to process - will be overwritten with processed output
# @param fn A function taking an XML document node as input which it processes in place, no return value

def fixFile(file, fn):
        
        # parse file into xml, and apply fn to the xml
        doc = xml.dom.minidom.parse(file)
        fn(doc)

        # strip the xml prolog from the output xml (BFD2 seems to cope if you leave it in, but remove for safety)
        stringrep = doc.toxml().replace("<?xml version=\"1.0\" ?>","")

        # write the xml back to the file
        f = codecs.open(file, "w", "utf-8")
        f.write(stringrep);
        f.close()

