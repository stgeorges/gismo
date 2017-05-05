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
Provided by Gismo 0.0.2
    
    input:
        _OSMobjectName: A single or a list of OSM object names.
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
ghenv.Component.Message = "VER 0.0.2\nMAY_05_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.2\nMAY_05_2017
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


def checkInputData(OSMobjectNameInputL, requiredKeyInput, requiredValuesInput):
    
    if ((len(OSMobjectNameInputL) == 0) or ((len(OSMobjectNameInputL) > 0) and (OSMobjectNameInputL[0] == None)))  and  ((requiredKeyInput == None) and (len(requiredValuesInput) == 0)):  # data NOT inputted into _OSMobjectName, NOT inputted into _requiredKey, and NOT inputted into requiredValues_
        # assign output names and descriptions to _OSMobjectName and _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(3, 0)
        changeInputNamesAndDescriptions(4, 0)
        OSMobjectNameInputL_python = requiredTag = None
        validInputData = False
        printMsg = "There are two ways to run this component:\n" + \
                   " \n" + \
                   "1) Add data only to \"_OSMobjectName\" input by using \"OSM Objects\" dropdown list.  Or,\n" +\
                   "2) Add data to \"_requiredKey\" and \"requiredValues_\" inputs, and disregard the upper \"_OSMobjectName\" input."
        return OSMobjectNameInputL_python, requiredTag, validInputData, printMsg
    
    
    if ((len(OSMobjectNameInputL) == 0) or ((len(OSMobjectNameInputL) > 0) and (OSMobjectNameInputL[0] == None)))  and  ((requiredKeyInput == None) and (len(requiredValuesInput) != 0)):  # data NOT inputted into _OSMobjectName, NOT inputted into _requiredKey, BUT INPUTTED into requiredValues_
        # assign output names and descriptions to _OSMobjectName and _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(3, 0)
        changeInputNamesAndDescriptions(4, 0)
        OSMobjectNameInputL_python = requiredTag = None
        validInputData = False
        printMsg = "Add a key to \"_requiredKey\" input.\n" + \
                   " \n" + \
                   "For example: if we supply \"leisure\" in the upper \"_requiredKey\" and we supply \"park\" to this input, then \"requiredTag\" would be: \"leisure,park\" which will be a prerequisite for finding all parks in \"OSM search\" component.\n \nThis input can also be left blank. In that case \"_requiredKey\" input (\"leisure\") will only be taken into account when generating the \"requiredTag\" output."
        return OSMobjectNameInputL_python, requiredTag, validInputData, printMsg
    
    
    if (len(OSMobjectNameInputL) != 0)  and  ((requiredKeyInput != None) or (len(requiredValuesInput) != 0)):  # data inputted into both _OSMobjectName  and  (_requiredKey or requiredValues_)
        # assign output names and descriptions to _OSMobjectName and _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(1, 0)
        changeInputNamesAndDescriptions(3, 0)
        changeInputNamesAndDescriptions(4, 0)
        OSMobjectNameInputL_python = requiredTag = None
        validInputData = False
        printMsg = "Do not input data to _OSMobjectName, along with _requiredKey or requiredValues_.\n \n" +\
                   "If you would like to generate \"requiredTag\" output based on \"_OSMobjectName\" input (instead of \"_requiredKey\" and \"requiredValues_\") then supply data to \"_OSMobjectName\" input only!\n" +\
                   "If you would like to generate \"requiredTag\" output based on \"_requiredKey\" and \"requiredValues_\" inputs (instead of \"_OSMobjectName\") then supply data to \"_requiredKey\",  or  \"_requiredKey\" and \"requiredValues_\" input(s) only!"
        return OSMobjectNameInputL_python, requiredTag, validInputData, printMsg
    
    
    if (len(OSMobjectNameInputL) != 0)  and  ((requiredKeyInput == None) and (len(requiredValuesInput) == 0)):  # data inputted to _OSMobjectName  and  NOT to _requiredKey and requiredValues_
        # assign output names and descriptions to _requiredKey, requiredValues_ inputs
        changeInputNamesAndDescriptions(3, 1)
        changeInputNamesAndDescriptions(4, 1)
    elif ((len(OSMobjectNameInputL) == 0) or ((len(OSMobjectNameInputL) > 0) and (OSMobjectNameInputL[0] == None)))  and  ((requiredKeyInput != None) or (len(requiredValuesInput) != 0)):  # data NOT inputted into _OSMobjectName  and  inputted into either _requiredKey or requiredValues_
        # assign output names and descriptions to _OSMobjectName input
        changeInputNamesAndDescriptions(1, 1)
    
    
    
    OSMobjectNameInputL_python = [str(OSMobjectName)  for OSMobjectName in OSMobjectNameInputL]  # convert Grasshopper String objects to python String objects
    
    if (len(OSMobjectNameInputL) != 0):
        # something inputted to "_OSMobjectName"
        requiredKeyL = []
        requiredValuesLL = []
        requiredKeyRequiredValue_dict = gismo_osm.requiredTag_dictionary()
        for OSMobjectName in OSMobjectNameInputL_python:
            if requiredKeyRequiredValue_dict.has_key(OSMobjectName):
                requiredKey, requiredValues = requiredKeyRequiredValue_dict[str(OSMobjectName)]
                requiredKeyL.append(requiredKey)
                requiredValuesLL.append(requiredValues)
            
            else:
                # inputted "_OSMobjectName" does not exist in "requiredKeyRequiredValue_dict"
                OSMobjectNameInputL_python = requiredTag = None
                validInputData = False
                printMsg = "One of supplied \"_OSMobjectName\" does not exist among this component's data.\n" + \
                           "Use \"OSM Objects\" dropdown list to generate it.\n" + \
                           " \n" + \
                           "Or instead of using \"_OSMobjectName\" input, use \"_requiredKey\" and \"requiredValues_\" inputs."
                return OSMobjectNameInputL_python, requiredTag, validInputData, printMsg
    else:
        # nothing inputted to "_OSMobjectName"
        requiredKeyL = [str(requiredKeyInput).strip()]  # remove " " (empty spaces) from beginning and start
        requiredValuesLL = [[str(value).strip()  for value in requiredValuesInput]]  # remove " " (empty spaces) from beginning and start
    
    
    for requiredValuesIndex, requiredValues in enumerate(requiredValuesLL):
        if requiredValues == ("^",):  # "^" means there is no specific value for this key
            requiredValuesLL[requiredValuesIndex] = []  # this is to prevent confusion by looking at "requiredTag" outut. "^" will be returned back in "OSM search" component
    
    
    requiredTag = Grasshopper.DataTree[object]()
    for i in range(len(requiredKeyL)):
        requiredTag.AddRange([requiredKeyL[i]], Grasshopper.Kernel.Data.GH_Path(i,0))
        requiredTag.AddRange(requiredValuesLL[i], Grasshopper.Kernel.Data.GH_Path(i,1))
    
    validInputData = True
    printMsg = "ok"
    return OSMobjectNameInputL_python, requiredTag, validInputData, printMsg


def printOutput(OSMobjectNameInputL_python, requiredKeyInput, requiredValueInput):
    requiredValueInput_python = [System.String(value)  for value in requiredValueInput]
    
    resultsCompletedMsg = "OSM tag component results successfully completed!"
    printOutputMsg = \
    """
Input data:

OSMobjectName: %s
requiredKey: %s
requiredValue: %s
    """ % (OSMobjectNameInputL_python, requiredKeyInput, requiredValueInput_python)
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
            OSMobjectNameInputL = list(ghenv.Component.Params.Input[0].VolatileData[0])
        except Exception, e:
            OSMobjectNameInputL = []
        
        try:
            requiredKeyInput = list(ghenv.Component.Params.Input[2].VolatileData[0])[0]
        except Exception, e:
            requiredKeyInput = None
        
        try:
            requiredValuesInput = list(ghenv.Component.Params.Input[3].VolatileData[0])
        except Exception, e:
            requiredValuesInput = []
        
        OSMobjectNameInputL_python, requiredTag, validInputData, printMsg = checkInputData(OSMobjectNameInputL, requiredKeyInput, requiredValuesInput)
        if validInputData:
            printOutput(OSMobjectNameInputL_python, requiredKeyInput, requiredValuesInput)
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
