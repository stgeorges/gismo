# OSM ids
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2019, Djordje Spasic <djordjedspasic@gmail.com>
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
Use this component to define lists of Open Street Map ids.
These lists can be used to define:
1) only those ids which will be included (isolated) when "OSM shapes" component is ran (use "osm_id_Only" and "osm_way_id_Only" inputs for this)
2) ids which will be removed when "OSM shapes" component is ran (use "osm_id_Remove" and "osm_way_id_Remove" inputs for this)
3) you can combine 1) and 2) and both define the: included and removed ids.
-
Additional info:
Sometimes "OSM shapes" can output invalid or unwanted shapes. In that case the purpose of this component is to remove those shapes by adding their ids to the "osm_id_Remove_" and/or "osm_way_id_Remove_" inputs.
-
Provided by Gismo 0.0.3
    
    input:
        osm_id_Only_: A list (or a single id) of "osm_id" which will only be included when "OSM shapes" component is ran.
                      -
                      If this input remains empty, then all "osm_id" will be presented.
        osm_way_id_Only_: A list (or a single id) of "osm_way_id" which will only be included when "OSM shapes" component is ran.
                          -
                          If this input remains empty, then all "osm_way_id" will be presented.
        osm_id_Remove_: A list (or a single id) of "osm_id" which will be removed when "OSM shapes" component is ran.
                        -
                        If this input remains empty, then none of the "osm_id" will be removed.
        osm_way_id_Remove_: A list (or a single id) of "osm_way_id" which will be removed when "OSM shapes" component is ran.
                            -
                            If this input remains empty, then none of the "osm_way_id" will be removed.
    
    output:
        readMe!: ...
        onlyRemove_Ids: Data tree containing "osm_id_Only_, osm_way_id_Only_, osm_id_Remove_, osm_way_id_Remove_" inputs.
                        -
                        Use it for "OSM shapes" component's "onlyRemove_Ids_" input.
"""

ghenv.Component.Name = "Gismo_OSM Ids"
ghenv.Component.NickName = "OSMids"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper


def checkInputData(osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove):
    
    for osm_id in osm_id_Only:
        if osm_id in osm_id_Remove:
            osm_way_id_Remove_dataTree = None
            validInputData = False
            printMsg = "You chose an id (%s) which exists both in \"osm_id_Only_\" and \"osm_id_Remove_\" inputs.\n" % osm_id  + \
                       "Please remove it from one of these two inputs."
            return osm_way_id_Remove_dataTree, validInputData, printMsg
    
    for osm_id2 in osm_way_id_Only:
        if osm_id2 in osm_way_id_Remove:
            osm_way_id_Remove_dataTree = None
            validInputData = False
            printMsg = "You chose an id (%s) which exists both in \"osm_way_id_Only_\" and \"osm_way_id_Remove_\" inputs.\n" % osm_id2  + \
                       "Please remove it from one of these two inputs."
            return osm_way_id_Remove_dataTree, validInputData, printMsg
    
    
    osm_way_id_Remove_dataTree = Grasshopper.DataTree[object]()
    
    if (len(osm_id_Only) == 0) and (len(osm_way_id_Only) == 0) and (len(osm_id_Remove) == 0) and (len(osm_way_id_Remove) == 0):
        # nothing inputted to either of four inputs (osm_id_Only_, osm_way_id_Only_, osm_id_Remove_, osm_way_id_Remove_)
        pass
    else:
        # some of four inputs has inputted data in it
        path0 = Grasshopper.Kernel.Data.GH_Path(0)
        path1 = Grasshopper.Kernel.Data.GH_Path(1)
        path2 = Grasshopper.Kernel.Data.GH_Path(2)
        path3 = Grasshopper.Kernel.Data.GH_Path(3)
        osm_way_id_Remove_dataTree.AddRange(osm_id_Only, path0)
        osm_way_id_Remove_dataTree.AddRange(osm_way_id_Only, path1)
        osm_way_id_Remove_dataTree.AddRange(osm_id_Remove, path2)
        osm_way_id_Remove_dataTree.AddRange(osm_way_id_Remove, path3)
    
    
    validInputData = True
    printMsg = "ok"
    
    return osm_way_id_Remove_dataTree, validInputData, printMsg


def printOutput(onlyRemove_IdsLL):
    if (len(onlyRemove_IdsLL) == 0): osm_id_Only = []; osm_way_id_Only = []; osm_id_Remove = []; osm_way_id_Remove = []
    else:
        osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove = onlyRemove_IdsLL
    resultsCompletedMsg = "OSM ids component results successfully completed!"
    printOutputMsg = \
    """
Input data:

osm_id_Only_: %s
osm_way_id_Only_: %s
osm_id_Remove_: %s
osm_way_id_Remove_: %s
    """ % (list(osm_id_Only), list(osm_way_id_Only), list(osm_id_Remove), list(osm_way_id_Remove))
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        onlyRemove_Ids, validInputData, printMsg = checkInputData(osm_id_Only_, osm_way_id_Only_, osm_id_Remove_, osm_way_id_Remove_)
        if validInputData:
            onlyRemove_IdsLL = [list(item)  for item in onlyRemove_Ids.Branches]
            printOutput(onlyRemove_IdsLL)
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
