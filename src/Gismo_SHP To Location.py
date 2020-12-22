# SHP to location
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2020, Djordje Spasic <djordjedspasic@gmail.com>
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to extract middle location from a shapefile (.shp).
-
Provided by Gismo 0.0.3
    
    input:
        _shpFile: File path to shapefile (.shp).
    output:
        readMe!: ...
        location: Middle location (latitude, longitude coordinates) of the '_shpFile' input.
"""

ghenv.Component.Name = "Gismo_SHP To Location"
ghenv.Component.NickName = "ShapefileToLocation"
ghenv.Component.Message = "VER 0.0.3\nDEC_20_2020"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | Gismo"
#compatibleGismoVersion = VER 0.0.3\nDEC_20_2020
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper



level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_gis = sc.sticky["gismo_GIS"]()
        
        if _shpFile:
            location, printMsg = gismo_gis.constructLocationFromShapefileMidExtent(_shpFile)
            if not location:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printMsg = "Add a file path of the shapefile (.shp) to '_shpFile' input."
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
