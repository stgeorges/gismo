# support gismo
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2017, Djordje Spasic <djordjedspasic@gmail.com>
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
If you like Gismo, use this component to see in which ways you can contribute and support it.
-
Provided by Gismo 0.0.2
    
    input:
        _supportIndex: Add a number from 0 to 3, to see in which ways you can support Gismo plugin.
    
    output:
        readMe!: This output shows support text for chosen _supportIndex input.
"""

ghenv.Component.Name = "Gismo_Support Gismo"
ghenv.Component.NickName = "SupportGismo"
ghenv.Component.Message = "VER 0.0.2\nMAR_01_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.2\nMAR_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import scriptcontext as sc
import Grasshopper


def main(supportIndex):
    
    # check inputs
    if (supportIndex == None):
        validInputData = False
        printMsg = "Please add a number from 0 to 3 to \"_supportIndex\" input."
        return validInputData, printMsg
    elif (supportIndex < 0) or (supportIndex > 3):
        validInputData = False
        printMsg = "\"_supportIndex\" input can only be either 0,1,2 or 3.\n" + \
                   "Choose one of these four."
        return validInputData, printMsg
    
    
    startingString = "Do you like Gismo? Here is one of the ways you can support it, and make it better:\n\n "
    
    if (supportIndex == 0):
        supportString = "Use Gismo components.\n" + \
                        "There is no better way of helping Gismo than actually using it. The more it's used, the more suggestions we will get, and more bugs will be found.\n" + \
                        "Make suggestions, or report bugs on our grasshopper page:\n" + \
                        "http://www.grasshopper3d.com/group/gismo"
    elif (supportIndex == 1):
        supportString = "It would be nice if you could follow, share or like the content from Gismo's facebook page:\n" + \
                        "https://www.facebook.com/GismoTools\n\n" + \
                        "Or retweet/like content from Gismo's twitter page:\n" + \
                        "https://twitter.com/gismo_tools\n\n" + \
                        "Or invite your friends to do that.\n" + \
                        "In this way, a word about Gismo will be spread."
    elif (supportIndex == 2):
        supportString = "Make a new Gismo component.\n" + \
                        "We welcome new developers. Even a single new component can benefit and make Gismo a better plugin.\n" + \
                        "To do that check Gismo \"New Component Example\" component. It provides a simple template of how you can make a new one."
    elif (supportIndex == 3):
        supportString = "Donate to services which Gismo uses.\n" + \
                        "Gismo is a free and open source plugin, and it will remain like this. Gismo will never ask you to donate money to its developers!\n" + \
                        "Still Gismo depends on some services from which it take data. The most important two are: OpenStreetMap and OpenTopography.\n" + \
                        "In case you can, and you want, you can donate a dollar or so to either:\n \n" + \
                        "OpenStreetMap:\n" + \
                        "https://donate.openstreetmap.org\n \n" + \
                        "or\n \n" + \
                        "OpenTopography:\n" + \
                        "http://www.opentopography.org/donate\n "
    
    print startingString
    print supportString
    
    validInputData = True
    printMsg = "ok"
    
    return validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        
        validInputData, printMsg = main(_supportIndex)
        if not validInputData:
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)