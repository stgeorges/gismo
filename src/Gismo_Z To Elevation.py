# z to elevation
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
Use this component to calculate the elevation height of particular point.
For example: you have a terrain made by Gismo or Ladybug "Terrain Generator" component, and you would like to know what is the elevation height of particular point on the terrain.
-
Provided by Gismo 0.0.2
    
    input:
        _point: Plug in the point for which you would like to calculate elevation height.
        _origin: Plug in the "origin" output from Gismo "Terrain Generator" or Ladybug "Terrain Generator" components.
        _elevation: Plug in the "elevation" output from Gismo "Terrain Generator" or Ladybug "Terrain Generator" components.
                    -
                    In Rhino document units (meters, feets...).
    
    output:
        readMe!: ...
        pointElevation: Elevation of the inputted _point.
                        -
                        In Rhino document units (meters, feets...).
"""

ghenv.Component.Name = "Gismo_Z To Elevation"
ghenv.Component.NickName = "ZtoElevation"
ghenv.Component.Message = "VER 0.0.2\nMAR_01_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | Gismo"
#compatibleGismoVersion = VER 0.0.2\nMAR_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper


def main(point, originPt, originPtElevation):
    
    # check inputs
    if (point == None):
        pointElevation_ = None
        validInputData = False
        printMsg = "Please input the \"_point\" for which you would like to calculate elevation."
        return pointElevation_, validInputData, printMsg
    
    if (originPt == None):
        pointElevation_ = None
        validInputData = False
        printMsg = "Please input \"origin\" output from Gismo or Ladybug \"Terrain Generator\" components, to this component's \"_origin\" input."
        return pointElevation_, validInputData, printMsg
    
    if (originPtElevation == None):
        pointElevation_ = None
        validInputData = False
        printMsg = "Please input \"elevation\" output from Gismo or Ladybug \"Terrain Generator\" components, to this component's \"_elevation\" input."
        return pointElevation_, validInputData, printMsg
    
    
    pointZ = point.Z
    originPtZ = originPt.Z
    pointElevation_ = (pointZ-originPtZ) + originPtElevation
    
    validInputData = True
    printMsg = "ok"
    
    return pointElevation_, validInputData, printMsg

level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_osm = sc.sticky["gismo_OSM"]()
        
        pointElevation, validInputData, printMsg = main(_point, _origin, _elevation)
        if validInputData:
            pass
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