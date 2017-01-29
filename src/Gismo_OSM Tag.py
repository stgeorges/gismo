# OSM tag
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2017, Djordje Spasic <djordjedspasic@gmail.com>
# Component icon based on free OSM icon from: <https://icons8.com/web-app/13398/osm>
#
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to generate "requiredTag" output. This output is used as input for "OSM search" component. It represents a combination of a key and value(s) for which search at "OSM search" component will be performed.
-
Search for any OSM tag at: http://taginfo.openstreetmap.org/tags
-
Provided by Gismo 0.0.1
    
    input:
        _OSMobjectName: OSM object name.
                        Use "OSM Objects" dropdown list to generate it.
        _requiredKey: Required key for which "requiredTag" output will be created.
                      -
                      If you add data to upper "_OSMobjectName" input, you do not have to use this input.
                      -
                      This input (and "requiredValues_" below it) is used if one would like to create custom "requiredTag" output not based on "OSM Objects" drowdown list.
                      For example, if we supply "leisure" to this input, and "park" to the one below ("requiredValues_"), then "requiredTag" output will be created as: "leisure,park" which will be a prerequisite for finding all parks in "OSM search" component.
        requiredValues_: Required values for which "requiredTag" output will be created.
                         -
                         If you add data to upper "_OSMobjectName" input, you do not have to use this input.
                         -
                         This input (and "_requiredKey" above it) is used if one would like to create custom "requiredTag" output not based on "OSM Objects" drowdown list.
                         For example, if we supply "park" to this input, and "leisure" to "_requiredKey" above, then "requiredTag" output will be created as: "leisure,park" which will be a prerequisite for finding all parks in "OSM search" component.
                         -
                         This input can also be left blank. In that case "_requiredKey" input ("leisure") will only be taken into account when generating the "requiredTag" output.
    
    output:
        readMe!: ...
        requiredTag: A tag represents a combination between a key and value(s).
                     It is prerequisite for finding particular object in "OSM search" component:  so use this output as "_requiredTag" input for "OSM search" component.
"""

ghenv.Component.Name = "Gismo_OSM Tag"
ghenv.Component.NickName = "OSMtag"
ghenv.Component.Message = "VER 0.0.1\nJAN_29_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.1\nJAN_29_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import Rhino
import math


def changeInputNamesAndDescriptions(inputIndex, inputtedOrNot):
    
    inputNickNames = [["_OSMobjectName", "-"], [], ["_requiredKey", "-"], ["requiredValues_", "-"]]
    inputDescriptions = [ 
     ["Name of the OSM object for which \"requiredTag\" needs to be created. Use the \"OSM Objects\" dropdown list to create it.", 
      "This inputt is not necessary. If you would like to generate \"requiredTag\" output based on \"_OSMobjectName\" input (instead of \"_requiredKey\" and \"requiredValues_\") then the data you supplied to this input is enough."]
     ,
     []
     ,
     ["A key for which \"requiredTag\" output will be created.\n \nFor example: \"leisure\". If we also supply \"park\" to the \"requiredValues_\" below, then \"requiredTag\" would be: \"leisure,park\" which will be a prerequisite for finding all parks in \"OSM search\" component.",
      "This inputt is not necessary. If you would like to generate \"requiredTag\" output based on \"_requiredKey\" and \"requiredValues_\" inputs (instead of \"_OSMobjectName\") then the data you supplied to these inputs is enough."]
     ,
     ["Values for which \"requiredTag\" output will be created.\n \nFor example: if we supply \"leisure\" in the upper \"_requiredKey\" and we supply \"park\" to this input, then \"requiredTag\" would be: \"leisure,park\" which will be a prerequisite for finding all parks in \"OSM search\" component.\n \nThis input can also be left blank. In that case \"_requiredKey\" input will only be taken into account when generating the \"requiredTag\" output.",
      "This inputt is not necessary. If you would like to generate \"requiredTag\" output based on \"_requiredKey\" and \"requiredValues_\" inputs (instead of \"_OSMobjectName\") then the data you supplied to these inputs is enough."]
     ]
    
    ghenv.Component.Params.Input[inputIndex-1].Name = inputNickNames[inputIndex-1][inputtedOrNot]
    ghenv.Component.Params.Input[inputIndex-1].NickName = inputNickNames[inputIndex-1][inputtedOrNot]
    ghenv.Component.Params.Input[inputIndex-1].Description = inputDescriptions[inputIndex-1][inputtedOrNot]


def checkInputData(OSMobjectNameInput, requiredKeyInput, requiredValuesInput):
    
    if (OSMobjectNameInput == None)  and  ((requiredKeyInput == None) and (len(requiredValuesInput) == 0)):  # data NOT inputted into _OSMobjectName, NOT inputted into _requiredKey, and NOT inputted into requiredValues_
        # assign output names and descriptions to _OSMobjectName and _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(3, 0)
        changeInputNamesAndDescriptions(4, 0)
        OSMobjectNameInput = requiredTag = None
        validInputData = False
        printMsg = "There are two ways to run this component:\n" + \
                   " \n" + \
                   "1) Add data only to \"_OSMobjectName\" input by using \"OSM Objects\" dropdown list.  Or,\n" +\
                   "2) Add data to \"_requiredKey\" and \"requiredValues_\" inputs, and disregard the upper \"_OSMobjectName\" input."
        return OSMobjectNameInput, requiredTag, validInputData, printMsg
    
    
    if (OSMobjectNameInput == None)  and  ((requiredKeyInput == None) and (len(requiredValuesInput) != 0)):  # data NOT inputted into _OSMobjectName, NOT inputted into _requiredKey, BUT INPUTTED into requiredValues_
        # assign output names and descriptions to _OSMobjectName and _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(3, 0)
        changeInputNamesAndDescriptions(4, 0)
        OSMobjectNameInput = requiredTag = None
        validInputData = False
        printMsg = "Add a key to \"_requiredKey\" input.\n" + \
                   " \n" + \
                   "For example: if we supply \"leisure\" in the upper \"_requiredKey\" and we supply \"park\" to this input, then \"requiredTag\" would be: \"leisure,park\" which will be a prerequisite for finding all parks in \"OSM search\" component.\n \nThis input can also be left blank. In that case \"_requiredKey\" input (\"leisure\") will only be taken into account when generating the \"requiredTag\" output."
        return OSMobjectNameInput, requiredTag, validInputData, printMsg
    
    
    if (OSMobjectNameInput != None)  and  ((requiredKeyInput != None) or (len(requiredValuesInput) != 0)):  # data inputted into both _OSMobjectName  and  (_requiredKey or requiredValues_)
        # assign output names and descriptions to _OSMobjectName and _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(3, 0)
        changeInputNamesAndDescriptions(4, 0)
        OSMobjectNameInput = requiredTag = None
        validInputData = False
        printMsg = "Do not input data to _OSMobjectName, along with _requiredKey or requiredValues_.\n \n" +\
                   "If you would like to generate \"requiredTag\" output based on \"_OSMobjectName\" input (instead of \"_requiredKey\" and \"requiredValues_\") then supply data to \"_OSMobjectName\" input only!\n" +\
                   "If you would like to generate \"requiredTag\" output based on \"_requiredKey\" and \"requiredValues_\" inputs (instead of \"_OSMobjectName\") then supply data to \"_requiredKey\",  or  \"_requiredKey\" and \"requiredValues_\" input(s) only!"
        return OSMobjectNameInput, requiredTag, validInputData, printMsg
    
    
    if (OSMobjectNameInput != None)  and  ((requiredKeyInput == None) and (len(requiredValuesInput) == 0)):  # data inputted to _OSMobjectName  and  NOT to _requiredKey and requiredValues_
        # assign output names and descriptions to _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(3, 1)
        changeInputNamesAndDescriptions(4, 1)
    elif (OSMobjectNameInput == None)  and  ((requiredKeyInput != None) or (len(requiredValuesInput) != 0)):  # data NOT inputted into _OSMobjectName  and  inputted into either _requiredKey or requiredValues_
        # assign output names and descriptions to _OSMobjectName input
        changeInputNamesAndDescriptions(1, 1)
    
    
    
    if OSMobjectNameInput:
        # something inputted to "_OSMobjectName"
        requiredKeyRequiredValue_dict = gismo_osm.requiredTag_dictionary()
        if requiredKeyRequiredValue_dict.has_key(str(OSMobjectNameInput)):
            requiredKey, requiredValues = requiredKeyRequiredValue_dict[str(OSMobjectNameInput)]
            del requiredKeyRequiredValue_dict
        else:
            # inputted "_OSMobjectName" does not exist in "requiredKeyRequiredValue_dict"
            OSMobjectNameInput = requiredTag = None
            validInputData = False
            printMsg = "Supplied \"_OSMobjectName\" does not exist among this component's data.\n" + \
                       "Use \"OSM Objects\" dropdown list to generate it.\n" + \
                       " \n" + \
                       "Or instead of using \"_OSMobjectName\" input, use \"_requiredKey\" and \"requiredValues_\" inputs."
            return OSMobjectNameInput, requiredTag, validInputData, printMsg
    else:
        # nothing inputted to "_OSMobjectName"
        requiredKey = str(requiredKeyInput).strip()  # remove " " (empty spaces) from beginning and start
        requiredValues = [str(value).strip()  for value in requiredValuesInput]  # remove " " (empty spaces) from beginning and start
    
    if requiredValues == ("^",):  # "^" means there is no specific value for this key
        requiredValues = []  # this is to prevent confusion by looking at "requiredTag" outut. "^" will be returned back in "OSM search" component
    
    requiredTag = Grasshopper.DataTree[object]()
    requiredTag.AddRange([requiredKey], Grasshopper.Kernel.Data.GH_Path(0))
    requiredTag.AddRange(requiredValues, Grasshopper.Kernel.Data.GH_Path(1))
    
    validInputData = True
    printMsg = "ok"
    return OSMobjectNameInput, requiredTag, validInputData, printMsg


def printOutput(OSMobjectName, requiredKeyInput, requiredValueInput):
    requiredValueInput_python = [System.String(value)  for value in requiredValueInput]
    
    resultsCompletedMsg = "OSM tag component results successfully completed!"
    printOutputMsg = \
    """
Input data:

OSMobjectName: %s
requiredKey: %s
requiredValue: %s
    """ % (OSMobjectName, requiredKeyInput, requiredValueInput_python)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_osm = sc.sticky["gismo_OSM"]()
        
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(3, 0)
        changeInputNamesAndDescriptions(4, 0)
        
        try:
            OSMobjectNameInput = list(ghenv.Component.Params.Input[0].VolatileData[0])[0]
        except Exception, e:
            OSMobjectNameInput = None
        
        try:
            requiredKeyInput = list(ghenv.Component.Params.Input[2].VolatileData[0])[0]
        except Exception, e:
            requiredKeyInput = None
        
        try:
            requiredValuesInput = list(ghenv.Component.Params.Input[3].VolatileData[0])
        except Exception, e:
            requiredValuesInput = []
        
        OSMobjectName, requiredTag, validInputData, printMsg = checkInputData(OSMobjectNameInput, requiredKeyInput, requiredValuesInput)
        if validInputData:
            printOutput(OSMobjectName, requiredKeyInput, requiredValuesInput)
        else:
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)