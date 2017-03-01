# deconstruct location
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
Use this component to exlode a location to its parts: locationName, latitude, longitude, timeZone, elevation.
-
Provided by Gismo 0.0.2

    input:
        _location: An .epw file location: joined string containing information about location's components: locationName, latitude, longitude, timeZone and elevation.
    
    output:
        readMe!: ...
        locationName: A name of the location.
                       -
                       If nothing added to this input, "unknown location" will be used as default locationName_.
        latitude: Location's latitude coordinate.
                   It ranges from -90 for locations south of equator, to 90 for locations above the equator.
        longitude: Location's longitude coordinate.
                    It ranges from -180 for locations west of Prime Meridian, to 180 for locations east of Prime Meridian.
        timeZone: The time zone of the location.
        elevation: Elevation (Altitude) height of the .epw location.
                   -
                   In meters.
"""

ghenv.Component.Name = "Gismo_Deconstruct Location"
ghenv.Component.NickName = "DeconstructLocation"
ghenv.Component.Message = "VER 0.0.2\nMAR_01_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "0 | Gismo"
#compatibleGismoVersion = VER 0.0.2\nMAR_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper


def checkInputs(location):
    
    # check inputs
    if (location == None):
        locationName = latitude = longitude = timeZone = elevation = None
        validInputData = False
        printMsg = "Please input the \"_location\"."
        return locationName, latitude, longitude, timeZone, elevation, validInputData, printMsg
    
    locationName, latitude, longitude, timeZone, elevation = gismo_preparation.deconstructLocation(location)
    
    validInputData = True
    printMsg = "ok"
    return locationName, latitude, longitude, timeZone, elevation, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        locationName, latitude, longitude, timeZone, elevation, validInputData, printMsg = checkInputs(_location)
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
