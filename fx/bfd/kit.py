g_slots = [
	dict ( name="Kick", cls="Kick",	subcls=""),
	dict(name="Snare", cls="Snare", subcls=""),
	dict(name="Hihat", cls="Hihat", subcls=""),
	dict(name="Floor Tom", cls="Tom", subcls="Floor"),
	dict(name="Mid Tom", cls="Tom", subcls="Mid"),
	dict(name="High Tom", cls="Tom", subcls="High"),
	dict(name="Crash 1", cls="Cymbal", subcls="Crash"),
	dict(name="Cymbal 1", cls="Cymbal", subcls=""),
	dict(name="Ride 1", cls="Cymbal", subcls="Ride"),
	dict(name="Perc", cls="Perc", subcls=""),
	dict(name="Kick 2", cls="Kick", subcls=""),
	dict(name="Snare 2", cls="Snare", subcls=""),
	dict(name="Floor Tom 2", cls="Tom", subcls="Floor"),
	dict(name="Mid Tom 2", cls="Tom", subcls="Mid"),
	dict(name="High Tom 2", cls="Tom", subcls="High"),
	dict(name="Crash 2", cls="Cymbal", subcls="Crash"),
	dict(name="Cymbal 2", cls="Cymbal", subcls=""),
	dict(name="Ride 2", cls="Cymbal", subcls="Ride"),
	dict(name="Perc 2", cls="Perc", subcls=""),
	dict(name="Perc 3", cls="Perc", subcls=""),
	dict(name="Perc 4", cls="Perc", subcls=""),
	dict(name="Perc 5", cls="Perc", subcls=""),
	dict(name="Perc 6", cls="Perc", subcls=""),
	dict(name="Perc 7", cls="Perc", subcls=""),
	dict(name="Perc 8", cls="Perc", subcls=""),
	dict(name="Perc 9", cls="Perc", subcls=""),
	dict(name="Perc 10", cls="Perc", subcls=""),
	dict(name="Perc 11", cls="Perc", subcls=""),
	dict(name="Perc 12", cls="Perc", subcls=""),
	dict(name="Perc 13", cls="Perc", subcls=""),
	dict(name="Perc 14", cls="Perc", subcls=""),
	dict(name="Perc 15", cls="Perc", subcls=""),
	dict(name="Kick 3", cls="Kick", subcls=""),
	dict(name="Kick 4", cls="Kick", subcls=""),
	dict(name="Kick 5", cls="Kick", subcls=""),
	dict(name="Snare 3", cls="Snare", subcls=""),
	dict(name="Snare 4", cls="Snare", subcls=""),
	dict(name="Snare 5", cls="Snare", subcls=""),
	dict(name="Floor Tom 3", cls="Tom", subcls="Floor"),
	dict(name="Floor Tom 4", cls="Tom", subcls="Floor"),
	dict(name="Floor Tom 5", cls="Tom", subcls="Floor"),
	dict(name="Mid Tom 3", cls="Tom", subcls="Mid"),
	dict(name="Mid Tom 4", cls="Tom", subcls="Mid"),
	dict(name="Mid Tom 5", cls="Tom", subcls="Mid"),
	dict(name="High Tom 3", cls="Tom", subcls="High"),
	dict(name="High Tom 4", cls="Tom", subcls="High"),
	dict(name="High Tom 5", cls="Tom", subcls="High"),
	dict(name="Crash 3", cls="Cymbal", subcls="Crash"),
	dict(name="Crash 4", cls="Cymbal", subcls="Crash"),
	dict(name="Crash 5", cls="Cymbal", subcls="Crash"),
	dict(name="Cymbal 3", cls="Cymbal", subcls=""),	
	dict(name="Cymbal 4", cls="Cymbal", subcls=""),
	dict(name="Cymbal 5", cls="Cymbal", subcls=""),
	dict(name="Ride 3", cls="Cymbal", subcls="Ride"),
	dict(name="Ride 4", cls="Cymbal", subcls="Ride"),
	dict(name="Ride 5", cls="Cymbal", subcls="Ride"),
	dict(name="Perc 16", cls="Perc", subcls=""),
	dict(name="Perc 17", cls="Perc", subcls=""),
	dict(name="Perc 18", cls="Perc", subcls=""),
	dict(name="Perc 19", cls="Perc", subcls=""),
	dict(name="Perc 20", cls="Perc", subcls=""),
	dict(name="Perc 21", cls="Perc", subcls=""),
	dict(name="Perc 22", cls="Perc", subcls=""),
	dict(name="Perc 23", cls="Perc", subcls="")]

def appendLocalIndicesToSlots(slots):
    classCount = dict()
    for slotID in range(len(slots)):
        slot = g_slots[slotID]
        cls = slot["cls"]
        if cls in classCount:
            classCount[cls] += 1
        else:
            classCount[cls] = 0;
        slot["localindex"] = classCount[cls]
        #print("slot " + str(slotID) + " cls " + cls + " local " + str(slot["localindex"]))

appendLocalIndicesToSlots(g_slots);

###########################################
# Get list of slot IDs for a class
# @param matchcls The class name to match
# @retval List of slot IDs for that class (integer)

def getSlotsForClass(matchcls):
    slotsList = []
    for slotID in range(len(g_slots)):
        slot = g_slots[slotID]
        if slot["cls"] == matchcls:
            slotsList.append(slotID)
    return slotsList

###########################################
# Get list of slot IDs for a class and subclass
# @param matchcls The class name to match
# @param matchsub The subclass name to match
# @retval List of slot IDs for that class&subclass (integer)

def getSlotsForSubClass(matchcls, matchsub):
    slotsList = []
    for slotID in range(len(g_slots)):
        slot = g_slots[slotID]
        if slot["cls"] == matchcls and slot["subcls"] == matchsub:
            slotsList.append(slotID)
    return slotsList

###########################################
# Get the class name of the given slot ID
# @param slotID the slot number
# @retval (string) Slot class string

def getSlotClass(slotID):
    return g_slots[slotID]["cls"]

###########################################
# Get the class local index of the given slot ID
# @param slotID the slot number
# @retval (integer) Slot class local index

def getSlotClassLocalIndex(slotID):
    return g_slots[slotID]["localindex"]

