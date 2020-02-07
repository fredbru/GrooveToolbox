from .kit import *
from .info import *
from ..common.fxxml import *

# === BFD2 GROOVE PALETTE FUNCTIONS ===

grvkpClassName = "BFD2GrooveKitPiece"
grvkpSlotAttributeName = "slotindex"
grvkpSlotClassAttributeName = "kpclass"
grvkpSlotLocalIndexAttributeName = "kpindex"

grvkpArticClassName = "BFD2GrooveArtic"
grvkpArticIndexAttributeName = "articid"
grvkpArticNameAttributeName = "articname"

grvhitClassName = "BFD2GrooveHit"
grvhitSlotAttributeName = "kpslot"
grvhitArticIndexAttributeName = "kpartic"
grvhitPositionAttributeName = "pos"
grvhitVelocityAttributeName = "vel"
grvhitMuteAttributeName = "mute"
ghostName = "ghost"

grvInfoClassName = "BFD2GrooveInfo"
grvBundleInfoClassName = "BFD2GrooveBundleInfo"
grvClassName = "BFD2Groove"
grvBundleClassName = "BFD2GrooveBundle"

grvInfoTimeSigAttributeName = "timesig"
grvInfoDenomBeatsAttributeName = "denombeats"
grvInfoBarsAttributeName = "bars"

grvInfoTempoAttributeName = "bpm"

class GrooveHit:
    def __init__(self):
        self.slotIndex = 0
        self.articIndex = 0
        self.beats = 0.0
        self.velocity = 0.0
        self.muted = False

    def __eq__(self, other):
        return self.slotIndex == other.slotIndex \
        and self.articIndex == other.articIndex \
        and self.beats == other.beats \
        and self.velocity == other.velocity \
        and self.muted == other.muted

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "{:10.6f}".format(self.beats) + " " + "{:>2}".format(self.slotIndex) + ":" + "{:4}".format(self.articIndex) + " vel " + "{:1.6f}".format(self.velocity) + (" muted" if self.muted else "")

class TimeSig:
    def __init__(self):
        self.numerator = 4
        self.denominator = 4
        
    def __str__(self):
        return str(self.numerator) + "/"+ str(self.denominator)

    def getDenominatorInBeats(self):
        return float(self.denominator) / 4.0

class Groove:
    def __init__(self):
        self.lengthInBeats = 0.0
        self.hits = []
        self.name = ""
        self.tempo = 120
        self.timeSig = TimeSig()

    def getAudibleHits(self):
        return list(self.getAudibleHitsGenerator())

    def getAllHits(self):
        return self.hits

    def getAudibleHitsGenerator(self):
        for hit in self.hits:
            if hit.muted:
                continue
            if hit.beats >= self.lengthInBeats:
                continue
            yield hit

def getGrooveName(node):
        info = node.getElementsByTagName(grvInfoClassName)
        return info[0].getAttribute(infoNameAttributeName)

# remap a kit piece slot in a palette file
# @param doc XML document to be processed in-place
# @param srcslot Current slot number (as an integer)
# @param dstslot New slot number (as an integer)

def remapKitPieceSlotInGrooves(doc, srcslot, dstslot):
        if not (isinstance(srcslot, int) and isinstance(dstslot, int)):
            raise TypeError('Kit piece slot should be of type int')

        srcslotstr = str(srcslot)
        dstslotstr = str(dstslot)

        dstslotclass = getSlotClass(dstslot)
        dstslotindex = str(getSlotClassLocalIndex(dstslot))

        for node in doc.getElementsByTagName(grvClassName):

            if testTagConditional(node, grvkpClassName, grvkpSlotAttributeName, srcslotstr):

                print ("warning: \"" + getGrooveName(node) + '\": requires patching for slot ' + srcslotstr)

                if testTagConditional(node, grvkpClassName, grvkpSlotAttributeName, dstslotstr):
                    # if dst slot groove kp exists, just kill the source one
                    deleteNodeConditional(node, grvkpClassName, grvkpSlotAttributeName, srcslotstr)
                else:
                    # dst slot doesn't exist in groove al
                    patchTagsConditional(node, grvkpClassName, grvkpSlotAttributeName, srcslotstr,
                                         [(grvkpSlotAttributeName, dstslotstr), 
                                          (grvkpSlotClassAttributeName,dstslotclass), 
                                          (grvkpSlotLocalIndexAttributeName,dstslotindex)])

            patchTagConditional(node, grvhitClassName, grvhitSlotAttributeName, srcslotstr, dstslotstr)

# remap the artic for a particular slot
# @param doc XML document to be processed in-place
# @param slot Slot number (as a string)
# @param srcArticIndex Source artic number
# @param desArticIndex Destination artic number

def remapArtic(doc, slotIndex, srcArticIndex, srcArticName, dstArticIndex, dstArticName):

    #--this code replaces the ids and names of matching groove kp artic elements, but that's really not what was wanted--
    #for node in doc.getElementsByTagName(grvkpClassName):
    #    value = node.getAttribute(grvkpSlotAttributeName)
    #    if value == slotIndex:
    #        # find and patch artic subnode
    #        for subnode in node.getElementsByTagName(grvkpArticClassName):
    #            articIndex = subnode.getAttribute(grvkpArticIndexAttributeName)
    #            articName = subnode.getAttribute(grvkpArticNameAttributeName)
    #            if articIndex == srcArticIndex:
    #                if articName != srcArticName:
    #                    raise "incorrect source artic name found"
    #                subnode.setAttribute(grvkpArticIndexAttributeName, dstArticIndex)
    #                subnode.setAttribute(grvkpArticNameAttributeName, dstArticName)
    #--end of section--

    hitsChanged = 0
    for node in doc.getElementsByTagName(grvhitClassName):
        hitSlotIndex = node.getAttribute(grvhitSlotAttributeName)
        hitArticIndex = node.getAttribute(grvhitArticIndexAttributeName)
        if hitSlotIndex == slotIndex and hitArticIndex == srcArticIndex:
            node.setAttribute(grvhitArticIndexAttributeName, dstArticIndex)
            hitsChanged += 1

    if hitsChanged > 0:
        print("Changed", hitsChanged, "hits from slot", slotIndex, "artic", srcArticIndex, "to artic", dstArticIndex)


# delete all references to a kit piece slot in a palette file (kp infos and hits)
# @param doc XML document to be processed in-place
# @param slot Slot number to be purged (as a string)

def deleteSlot(doc, slot):
        deleteNodeConditional(doc, grvkpClassName, grvkpSlotAttributeName, slot)
        deleteNodeConditional(doc, grvhitClassName, grvhitSlotAttributeName, slot)
        
# change the info_library name for kp infos and hits in a palette
# @param doc XML document to be processed in-place
# @param libname New library name

def changeLibraryName(doc, libname):
        patchTag(doc, grvInfoClassName, "info_library", libname)
        patchTag(doc, grvBundleInfoClassName, "info_library", libname)
        patchTag(doc, grvInfoClassName, "info_librarylong", libname)
        patchTag(doc, grvBundleInfoClassName, "info_librarylong", libname)

# check whether all references to slot numbers in a palette file are within range
# @param doc XML document to be checked
# @retval True if the attribute value for all nodes is within range, False otherwise

def checkEcoSlotNumbers(doc):
        retval = True
        if not checkIntegerAttributeRange(doc, grvkpClassName, grvkpSlotAttributeName, 0, 11):
                retval = False
        if not checkIntegerAttributeRange(doc, grvhitClassName, grvhitSlotAttributeName, 0, 11):
                retval = False
        return retval

# remap bfd3 zero-based groove slot numbers to eco note 60-based groove slot numbers
# @param doc XML document to be processed in-place
# @param srcslot Current slot number (as a string)
# @param dstslot New slot number (as a string)

def remapGrooveSlotNumber(doc, srcslot, dstslot):
        patchTagConditional(doc, grvkpClassName, grvkpSlotAttributeName, srcslot, dstslot)
        patchTagConditional(doc, grvhitClassName, grvhitSlotAttributeName, srcslot, dstslot)

# Gets the groove bundle node for a doc
# @param doc XML document to be processed in-place
# @param slot Slot number to be purged (as a string)

def getGrooveBundleNode(doc):
    pathToSlots = [(grvBundleClassName,"bundle"), ("VDictionary", "grooves")]
    return navigateDocToSubnode(doc, pathToSlots)
        

# === COMBINED KIT PIECE & SLOT FUNCTIONS ===

###########################################
# Remaps artics for all slots of a given class and subclass
# @param kpClassName The kit piece class name
# @param kpSubClassName The kit piece sub class name
# @param oldArticName The old artic name to match (must be a valid artic name for the kp class)
# @param newArticName The new artic name to use (must be a valid artic name for the kp class)

def remapArticsForSlots(doc, kpClassName, kpSubClassName, oldArticName, newArticName):
    slots = getSlotsForSubClass(kpClassName, kpSubClassName)
    oldArticIndex = getArticIndexForClass(kpClassName, oldArticName)
    newArticIndex = getArticIndexForClass(kpClassName, newArticName)
    for slotID in slots:
        remapArtic(doc, str(slotID), str(oldArticIndex), oldArticName, str(newArticIndex), newArticName)

###########################################
# Get a BFD2Time-format time attribute and returns as floating point number of beats
# NOTE: this doesn't check the timing resolution in the file and only uses the current 1000000 ticks per beat standard
# @param node The node in which to find the attribute
# @param attribute The attribute name

def getBeatsAttribute(node, attribute):
    return float(node.getAttribute(attribute)) / 1000000.0

###########################################
# Parses a time signature attribute in a document node
# @param node The node in which to find the attribute
# @param attribute The attribute name
# @retval TimeSig object

def getTimeSigAttribute (node, attribute):
    timeSigString = node.getAttribute(attribute)
    timeSigParts = timeSigString.split('/')
    timeSig = TimeSig()
    timeSig.numerator = int(timeSigParts[0])
    timeSig.denominator = int(timeSigParts[1])
    return timeSig
    
###########################################
# Parses a tempo attribute in a document node
# @param node The node in which to find the attribute
# @param attribute The attribute name
# @retval Tempo

def getTempoAttribute (node, attribute):    
    tempoString = node.getAttribute(attribute)
    tempo = float(str(tempoString).rstrip())
    return tempo

###########################################
# Returns all the XML nodes for grooves in the given doc
# @param doc The XML doc in which to search

def getGrooveNodes (doc):
    grooves = []
    return doc.getElementsByTagName(grvClassName)

###########################################
# Parses a groove node in the XML
# @param grooveNode The node to parse
# @retval Groove object

def getGrooveFromNode (grooveNode):
    groove = Groove()
    groove.name = getGrooveName (grooveNode)
    #print(groove.name)
    grooveInfoNode = getSingleSubnodeByClass (grooveNode, grvInfoClassName)
    #lengthInDenomUnits = int(grooveInfoNode.getAttribute(grvInfoDenomBeatsAttributeName))
    #print("lidm=", lengthInDenomUnits)
    timeSig = getTimeSigAttribute (grooveInfoNode, grvInfoTimeSigAttributeName)
    tempo   = getTempoAttribute (grooveInfoNode, grvInfoTempoAttributeName)
    denomUnitLength = timeSig.getDenominatorInBeats()
    groove.lengthInBeats = 2 * timeSig.denominator
    hitNodes = grooveNode.getElementsByTagName(grvhitClassName)
    for hitNode in hitNodes:
        hit = GrooveHit()
        hit.beats = getBeatsAttribute(hitNode, grvhitPositionAttributeName)
        hit.slotIndex = hitNode.getAttribute(grvhitSlotAttributeName)
        hit.articIndex = hitNode.getAttribute(grvhitArticIndexAttributeName)
        hit.velocity = float(hitNode.getAttribute(grvhitVelocityAttributeName))
        hit.muted = getBoolAttribute(hitNode, grvhitMuteAttributeName, False)
        ghost = getBoolAttribute(hitNode,"ghost", False)
        if ghost == 'true':
            print(ghost)
        groove.hits.append(hit)
    return groove, tempo

###########################################
# Returns a single groove object from a groove file XML doc (i.e. not a bundle file)
# @param doc Groove file XML doc (may only contain a single groove, i.e. not a bundle file)

def getGrooveFromGrooveFileXML(doc):
    grooves = getGrooveNodes(doc)
    if len(grooves) != 1:
        raise Exception('Expected single groove node within file ' + file);
    return getGrooveFromNode(grooves[0])
