#!/usr/bin/env python
# -*- coding: utf-8 -*-
# DMS to DD
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
Use this component to convert a coordinate in degrees, minutes and seconds (DMS) format to decimal degrees (DD) format.
This can be useful for Gismo component's "Create Location" inputs in case you have latitude/longitude coordinates in DMS instead of DD format.
-
Provided by Gismo 0.0.2

    input:
        _dms: A string representing degrees minutes and seconds (DMS) coordinate.
              -
              In dms degrees.
    
    output:
        decimalDegree: _dms coordinate converted to decimal degree
                       -
                       In dd degrees.
"""

ghenv.Component.Name = "Gismo_DMS To DD"
ghenv.Component.NickName = "DMSToDD"
ghenv.Component.Message = "VER 0.0.2\nMAY_01_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | Gismo"
#compatibleGismoVersion = VER 0.0.2\nMAR_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper


def main(dms):
    
    # check inputs
    if (dms == None):
        decimalDegree = None
        validInputData = False
        printMsg = "Please add a coordinate in DMS (degree,minute,second) format to \"_dms\" input.\n" + \
                   "Here is an example: 18° 20' 45.6\" E"
        return decimalDegree, validInputData, printMsg
    
    
    # replacing ″ character with "
    dms2 = dms.replace("″", "\"")
    
    # replacing ` and ′ characters in case they are used instead of '
    dms3 = dms2.replace("`", "'")
    dms4 = dms3.replace("′", "'")
    
    if ("°" in dms4) and ("'" in dms4) and ("\"" in dms4):
        # extract degrees, minutes, seconds from "_dms"
        dms_stripped = dms4.strip()
        degrees = dms_stripped.split("°")[0].strip()
        
        dms_stripped_withoutDegree = dms_stripped.split("°")[-1].strip()
        minutes = dms_stripped_withoutDegree.split("'")[0].strip()
        
        dms_stripped_withoutDegreeMinute = dms_stripped_withoutDegree.split("'")[-1].strip()
        seconds = dms_stripped_withoutDegreeMinute.split("\"")[0].strip()
        
        cardinalDirection = dms_stripped_withoutDegreeMinute[-1].strip()
        
        # extract cardinal direction from "_dms"
        if (cardinalDirection.upper() == "N") or (cardinalDirection.upper() == "E"):
            plusOrMinus = 1
        elif (cardinalDirection.upper() == "S") or (cardinalDirection.upper() == "W"):
            plusOrMinus = -1
        else:
            decimalDegree = None
            validInputData = False
            printMsg = "The \"_dms\" input should end with one of the following 4 cardinal direction: N, S, E, W.\n" + \
                       "Here is an example: 42° 42' 43.2\" N"
            return decimalDegree, validInputData, printMsg
        
        
        decimalDegree = float(degrees) + (  ( float(minutes) + (float(seconds)/60))/60  )
        decimalDegree = plusOrMinus * decimalDegree
    
    
    else:
        decimalDegree = None
        validInputData = False
        printMsg = "Something is wrong with the \"_dms\" input.\n" + \
                   "It should represent a coordinate in degree,minute,second format.\n" + \
                   "Here is an example: 18° 20' 45.6\" E\n" + \
                   "\n" + \
                   "Sometimes the problem may be with one of the degree, minute, second label characters you used: °, ', \".\n"
        return decimalDegree, validInputData, printMsg
    
    
    validInputData = True
    printMsg = "ok"
    return decimalDegree, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        
        decimalDegree, validInputData, printMsg = main(_dms)
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
