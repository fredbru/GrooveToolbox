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

class Counter1Level:

    def __init__(self):
        self.map = dict()

    def printIndented(self, title):
        print(title)
        for k,v in sorted(self.map.items()):
            print("- " + k + ' --- (' + str(v) + ')')
        print("========")

    def increment(self, index):
        if not index in self.map:
            self.map[index] = 0
        self.map[index] += 1

class Counter2Level:

    def __init__(self):
        self.map = dict()

    def printIndented(self, title):
        print(title)
        for k1,v1 in sorted(self.map.items()):
            print("- " + k1)
            for k2, v2 in sorted(v1.items()):
                print("  - " + k2 + ' --- (' + str(v2) + ')')
        print("========")

    def printCSV(self, title, col1name, col2name):
        print(title)
        print(col1name + ',' + col2name + ',count')
        for k1,v1 in sorted(self.map.items()):
            for k2, v2 in sorted(v1.items()):
                print(k1 + ',' + k2 + ',' + str(v2))
        print("========")

    def printCSVWithLevel1Summary(self, title, col1name, col2name):
        print(title)
        print(col1name + ',totalcount,' + col2name + ',count')
        for k1,v1 in sorted(self.map.items()):
            summaryCount = 0
            for k2, v2 in v1.items():
                summaryCount += v2
            for k2, v2 in sorted(v1.items()):
                print(k1 + ',' + str(summaryCount) + ',' + k2 + ',' + str(v2))
        print("========")

    def increment(self, index1, index2):
        if not index1 in self.map:
            self.map[index1] = dict()
        if not index2 in self.map[index1]:
            self.map[index1][index2] = 0
        self.map[index1][index2] += 1

