import re
from .info import *
from ..common.misc import *

# === BFD2 KIT PIECE FUNCTIONS ===

kpInfoClassName = "BFD2KitPieceInfo"
kpiNameAttributeName = "kpi_name"
kpiTextAttributeName = "kpi_text"
kpiLibraryAttributeName = "kpi_library" # deprecated

kpiClassAttributeName = "kpi_class"
kpiSubClassAttributeName = "kpi_subclass"

kpiMfrAttributeName = "kpi_manufacturer"
kpiModelAttributeName = "kpi_model"
kpiDateAttributeName = "kpi_date"

kpiDimensionsAttributeName = "kpi_dimensions"
kpiDepthAttributeName = "kpi_depth"
kpiDiamAttributeName = "kpi_diam"

kpiMaterialsAttributeName = "kpi_materials"
kpiSkinAttributeName = "kpi_skin"

kpiBeaterAttributeName = "kpi_beater"
kpiStrainerAttributeName = "kpi_strainer"
kpiDampingAttributeName = "kpi_damping"

g_artics = dict( Metronome=["Bar", "Beat", "Tatum", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight" ],
              Kick=["Hit","NoSnare"],
              Snare=["Hit","Drag","Flam","Rim shot","Side stick","Half","Variable"],
              Hihat=["Open tip","Open shank","3/4 tip","3/4 shank","Half tip","Half shank","1/4 tip","1/4 shank","Closed Tip","Closed shank","Pedal","Variable tip","Variable shank","Splash"],
              Tom=["Hit","Alternative","Rim Shot","Rim Click"],
              Cymbal=["Hit","Bell","Edge"],
              Perc=["Hit","Alternative"]
              )

###########################################
# Get artic ID for the named artic within the named class
# @param matchcls The class name to match
# @param articName The artic name to match
# @retval (integer) Artic index within that class

def getArticIndexForClass(matchcls, articName):
    classArtics = g_artics[matchcls]
    return classArtics.index(articName)

def matchModelOrName(path, valuedict, searchstring, subClassString):
        kpiName = valuedict[kpiNameAttributeName]
        model = valuedict[kpiModelAttributeName]
        if re.search(searchstring, model) is not None:
                return subClassString
        else:
                if re.search(searchstring, kpiName) is not None:
                        return subClassString
                else:
                        if re.search(searchstring, path) is not None:
                                return subClassString
        return ""

def deriveDimensions(valuedict, path, mark, depthFirst):
        depth = valuedict[kpiDepthAttributeName]
        diameter = valuedict[kpiDiamAttributeName]
        
        if (depth != None and depth != '') or (diameter != None and diameter != ''):
                return
        
        dims = valuedict[kpiDimensionsAttributeName]
        text = valuedict[kpiTextAttributeName]
        
        if dims == "" and re.search('Size: ',text) is not None:
                dims = re.sub('.*?Size: ([0-9x]*).*', '\\1', text)

        # dims
        if (dims != ""):
                dims = re.sub('\"', '', dims)
                if re.search('x', dims) is not None:
                        if depthFirst == True:
                                depth = re.sub('x.*', '', dims)
                                diameter = re.sub('.*x', '', dims)
                        else:
                                diameter = re.sub('x.*', '', dims)
                                depth = re.sub('.*x', '', dims)
                else:
                        diameter = dims
                        depth = ''
        else:
                diameter = ''
                depth = ''

        valuedict[kpiDepthAttributeName] = depth + mark
        valuedict[kpiDiamAttributeName] = diameter + mark

def deriveSubClass(valuedict, path, modifiedmark, nosubclassmark):
        kpiSubClass = valuedict[kpiSubClassAttributeName]
        if kpiSubClass != None and kpiSubClass != '':
                return
        
        kpiClass = valuedict[kpiClassAttributeName]
        derivedSubClass = nosubclassmark
        if kpiClass == "Cymbal":
                derivedSubClass = ""
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Cc]rash", "Crash"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Ss]plash", "Splash"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Rr]ide", "Ride"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Cc]hina", "China"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Gg]ong", "Gong"))
        if kpiClass == "Tom":
                derivedSubClass = ""
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Ff]loor", "Floor"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Hh]igh", "High"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "([Hh]i )|([Hh]i\Z)", "High"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "([Ll]o )|([Ll]ow)", "Low"))
                derivedSubClass = concatenateTerms(derivedSubClass, matchModelOrName(path, valuedict, "[Mm]id", "Mid"))

        if derivedSubClass == nosubclassmark:
                valuedict[kpiSubClassAttributeName] = nosubclassmark # this didn't expect a subclass
        else:
                valuedict[kpiSubClassAttributeName] = derivedSubClass + modifiedmark

def deriveBeater(valuedict, path, modifiedmark):
        beater = valuedict[kpiBeaterAttributeName]
        if beater != None and beater != '':
                return

        kpiClass = valuedict[kpiClassAttributeName]

        # handle matching patterns in the name or model
        if beater == "":
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Ww]ood\S", "Wood"))
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Ff]elt\S", "Felt"))
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Rr]ubber\S", "Rubber"))
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Bb]rush\S", "Brush"))
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Ss]tick\S", "Stick"))
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Mm]allet\S", "Mallet"))
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Rr]od\S", "Rod"))
                beater = concatenateTerms(beater, matchModelOrName(path, valuedict, "[Nn]ylon\S", "Nylon"))

        # if still nothing, look for matching patterns in the plain text
        text = valuedict[kpiTextAttributeName]
        if beater == "" and re.search('Beater: ', text) is not None:
                beater = re.sub('.*?Beater: ([A-Za-z0-9 ]+).*', '\\1', text)

        if beater == "" and re.search('[Bb]rush', text) is not None:
                beater = "Brush"
        if beater == "" and re.search('[Ss]tick', text) is not None:
                beater = "Stick"
        if beater == "" and re.search('[Mm]allet', text) is not None:
                beater = "Mallet"
        if beater == "" and re.search('[Rr]od', text) is not None:
                beater = "Rod"

        valuedict[kpiBeaterAttributeName] = beater + modifiedmark

def deriveStrainer(valuedict, path, modifiedmark):
        strainer = valuedict[kpiStrainerAttributeName]
        if strainer != None and strainer != '':
                return

        # need to process all
        kpiClass = valuedict[kpiClassAttributeName]
        if kpiClass != 'Snare' and kpiClass != 'Tom' and kpiClass != 'Kick':
                return
        
        # handle matching patterns in the name
        name = valuedict[kpiNameAttributeName]
        if strainer == "" and re.search('[Ss]nare(s)? [Oo]n', name) is not None:
                strainer = "On"
        if strainer == "" and re.search('[Ss]nare(s)? [Oo]ff', name) is not None:
                strainer = "Off"
        if strainer == "" and re.search('[Ss]trainer(s)? [Oo]n', name) is not None:
                strainer = "On"
        if strainer == "" and re.search('[Ss]trainer(s)? [Oo]ff', name) is not None:
                strainer = "Off"

        # if still nothing, look for matching patterns in the plain text
        text = valuedict[kpiTextAttributeName]
        if strainer == "" and re.search('[Ss]nare(s)? [Oo]n', text) is not None:
                strainer = "On"
        if strainer == "" and re.search('[Ss]nare(s)? [Oo]ff', text) is not None:
                strainer = "Off"
        if strainer == "" and re.search('[Ss]trainer(s)? [Oo]n', text) is not None:
                strainer = "On"
        if strainer == "" and re.search('[Ss]trainer(s)? [Oo]ff', text) is not None:
                strainer = "Off"

        valuedict[kpiStrainerAttributeName] = strainer + modifiedmark

def copyMissingInfoLibraryFromKPI(valuedict, path, modifiedmark):
    # Fix up any missing/duff data - writing back into the value fields
    if valuedict[infoLibraryAttributeName] == None or valuedict[infoLibraryAttributeName] == "":
        valuedict[infoLibraryAttributeName] = valuedict[kpiLibraryAttributeName] + modifiedmark
