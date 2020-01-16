# Example use of GrooveToolbox
# Put in a folder of 8 example loops in numpy format - like the ones that I sent Olivier ages ago.
# Then people just starting out can have a go at doing the analysis using data that
# definitely works.

import numpy as np
import Groove

nameA = "Glam Get Down 5.npy"
nameB = "Glam Get Down 7.npy"

GlamGetDown5 = Groove.Groove("Glam Get Down 5.npy")

print(GlamGetDown5.rhythmFeatures.autocorrelationCentroid)