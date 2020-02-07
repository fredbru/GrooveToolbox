import xml.dom.minidom
from xml.dom.minidom import Node

#####
# change attribute values for given nodes which match an existing value
# @param domElement XML element to be processed in-place
# @param classname XML node class name to be matched
# @param attribute XML attribute name to be tested
# @param oldvalue XML attribute value to check for
# @param newvalue XML attribute value to replace the existing value with

def patchTagConditional(domElement, classname, attribute, oldvalue, newvalue):
        for node in domElement.getElementsByTagName(classname):
                value = node.getAttribute(attribute)
                if value == oldvalue:
                        node.setAttribute(attribute, newvalue)
        
#####
# change attribute values for given nodes which match an existing value
# @param domElement XML element to be processed in-place
# @param classname XML node class name to be matched
# @param attribute XML attribute name to be tested
# @param oldvalue XML attribute value to check for
# @param attributePairs a list of (attribute name, new value) pairs

def patchTagsConditional(domElement, classname, attribute, oldvalue, attributePairs):
        for node in domElement.getElementsByTagName(classname):
                value = node.getAttribute(attribute)
                if value == oldvalue:
                        for attributePair in attributePairs:
                                node.setAttribute(attributePair[0], attributePair[1])
        

#####
# test for the presence of a given attribute values for given nodes
# @param domElement XML element to be processed in-place
# @param classname XML node class name to be matched
# @param attribute XML attribute name to be tested
# @param testvalue XML attribute value to check for
# @retval bool True or False

def testTagConditional(domElement, classname, attribute, testvalue):
        for node in domElement.getElementsByTagName(classname):
                value = node.getAttribute(attribute)
                if value == testvalue:
                    return True;
        return False;
        

       
#####
# delete nodes with an attribute matching a given value
# @param domElement XML element to be processed in-place
# @param classname XML node class name to be matched
# @param attribute XML attribute name to be tested
# @param oldvalue XML attribute value to check for

def deleteNodeConditional(domElement, classname, attribute, oldvalue):
        for node in domElement.getElementsByTagName(classname):
                value = node.getAttribute(attribute)
                if value == oldvalue:
                        node.parentNode.removeChild(node)
        
#####
# change attribute values for all nodes of a given class
# @param domElement XML element to be processed in-place
# @param classname XML node class name to be matched
# @param attribute XML attribute name to patch
# @param value XML attribute value to write into the XML

def patchTag(domElement, classname, attribute, value):
        for node in domElement.getElementsByTagName(classname):
                node.setAttribute(attribute, value)

#####
# get the text of a VString attribute
# @param node parent node
# @param attribute name of VString element

def getVStringAttribute(node, attribute):
        if node.getAttributeNode(attribute) is not None:        # getAttributeNode: test node existence
                return node.getAttribute(attribute)             # vs. getAttribute: get node as string
        for subnode in node.getElementsByTagName("VString"):
                if (subnode.getAttribute("name") == attribute):
                        return subnode.getAttribute("string")
                
#####
# get the text of a VString node
# @param VString node
# @param text from VString node

def getTextFromVStringNode(node):
    if node.getAttributeNode("string") is not None:        # getAttributeNode: test node existence
        return node.getAttribute("string")             # vs. getAttribute: get node as string
    return node.firstChild.nodeValue
                
#####
# get a bool value from an FX XML node
# @param node
# @param attribute name of XML attribute to test
# @param defaultValue value to return if attribute not found

def getBoolAttribute(node, attribute, defaultValue = False):
    if node.getAttributeNode(attribute) is not None:    # getAttributeNode: test node existence
        value = node.getAttribute(attribute)            # vs. getAttribute: get node as string
        return value.lower() == "true" or value == "yes"
    return defaultValue
                
#####
# get (a single) child nodes with a given class name and a given FX instance name
# @param node parent node
# @param classname of child element required
# @param name of child element required (will match using the 'name' attribute)

def getSingleSubnodeByClassAndName(node, classname, name):
    foundNode = None
    for subnode in node.getElementsByTagName(classname):
        if (subnode.getAttribute("name") == name):
            if foundNode is None:
                foundNode = subnode
            else:
                raise Exception('Expected single child of class ' + classname + ' found multiple');

    if foundNode is None:
        raise Exception('Expected single child of class ' + classname + ' found none');

    return foundNode

#####
# get (a single) child nodes with a given class name
# @param node parent node
# @param classname of child element required
# @exception if no or multiple children returned

def getSingleSubnodeByClass(node, classname):
    subnodes = node.getElementsByTagName(classname)
    if len(subnodes) != 1:
        raise Exception('Expected single child of class ' + classname);
    return subnodes[0];

                
#####
# Traverse down to a particular subnode navigating down from the root node based on a sequence of pairs
# @param doc Document
# @param classInstancePairs List of (classname, instancename) pairs, e.g. [("BFD2GrooveBundle","bundle"), ("VDictionary", "grooves")]
#                           The first pair identifies a desired subnode in the root, the second identifies a desired subnode within the first subnode, and so on

def navigateDocToSubnode(doc, classInstancePairs):
        node = doc.documentElement
        return navigateToSubnode(node, classInstancePairs)

#####
# Traverse down to a particular subnode navigating down from the node based on a sequence of pairs
# @param node Node to start from
# @param classInstancePairs List of (classname, instancename) pairs, e.g. [("BFD2GrooveBundle","bundle"), ("VDictionary", "grooves")]
#                           The first pair identifies a desired subnode in the node, the second identifies a desired subnode within the first subnode, and so on

def navigateToSubnode(node, classInstancePairs):
        if (len(classInstancePairs) == 0):
                return node
        thisPair = classInstancePairs.pop(0)
        subnode = getSingleSubnodeByClassAndName(node, thisPair[0], thisPair[1])
        if (subnode is None):
            return None
        return navigateToSubnode(subnode, classInstancePairs)

#####
# check whether a given attribute is within a given integer range
# @param doc XML document to be checked
# @param classname XML node class name to be matched
# @param attribute XML attribute name to be tested
# @param low Minimum acceptable value for the attribute (inclusive)
# @param high Maximum acceptable value for the attribute (inclusive)
# @retval True if the attribute value for all nodes is within range, False otherwise

def checkIntegerAttributeRange(doc, classname, attribute, low, high):
        retval = True
        for node in doc.getElementsByTagName(classname):
                value = node.getAttribute(attribute)
                intvalue = int(value)
                if (intvalue < low) or (intvalue > high):
                        print("attribute " + attribute + " out of range (" + value + ")")
                        retval = False

        return retval
        
