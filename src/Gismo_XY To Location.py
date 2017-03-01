# xy to location
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
Use this component to calculate latitude and longitude coordinates of the _point in Rhino scene.
For example: you created some building shapes with Gismo "OSM Shapes" component, and now you would like to check what are the latitude and longtitude coordinates of particular part of the building.
-
Provided by Gismo 0.0.2
    
    input:
        _point: A point for which we would like to calculate its latitude and longitude coordinates
        anchorLocation_: Represents latitude,longitude coordinates which correspond to anchorOrigin_ in Rhino scene.
                         -
                         If nothing added to this input, anchorLocation_ with both latitude and longitude set to "0" will be used as a default.
        anchorOrigin_: A point in Rhino scene which corresponds to anchorLocation_.
                       -
                       If nothing added to this input, anchorOrigin will be set to: 0,0,0.
    output:
        readMe!: ...
        location: Location (latitude, longitude coordinates) of the _point input.
"""

ghenv.Component.Name = "Gismo_XY To Location"
ghenv.Component.NickName = "XYtoLocation"
ghenv.Component.Message = "VER 0.0.2\nMAR_01_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | Gismo"
#compatibleGismoVersion = VER 0.0.2\nMAR_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import Rhino


def main(requiredPoint, anchorLocation, anchorOrigin):
    
    # check inputs
    if (requiredPoint == None):
        required_location = None
        validInputData = False
        printMsg = "Please add a point to this component's \"_point\" input."
        return required_location, validInputData, printMsg
    
    if (anchorLocation == None):
        locationName = "unknown location"
        anchor_locationLatitudeD = 0
        anchor_locationLongitudeD = 0
        timeZone = 0
        elevation = 0
    else:
        locationName, anchor_locationLatitudeD, anchor_locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_preparation.checkLocationData(anchorLocation)
    
    if (anchorOrigin == None):
        anchorOrigin = Rhino.Geometry.Point3d(0,0,0)
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    anchorOrigin_meters = Rhino.Geometry.Point3d(anchorOrigin.X*unitConversionFactor, anchorOrigin.Y*unitConversionFactor, anchorOrigin.Z*unitConversionFactor)
    requiredPoint_meters = Rhino.Geometry.Point3d(requiredPoint.X*unitConversionFactor, requiredPoint.Y*unitConversionFactor, requiredPoint.Z*unitConversionFactor)
    
    
    # inputCRS
    EPSGcode = 4326
    inputCRS_dummy = gismo_osm.CRS_from_EPSGcode(EPSGcode)
    # outputCRS
    outputCRS_dummy = gismo_osm.UTM_CRS_from_latitude(anchor_locationLatitudeD, anchor_locationLongitudeD)
    
    anchor_originProjected_meters = gismo_osm.convertBetweenTwoCRS(inputCRS_dummy, outputCRS_dummy, anchor_locationLongitudeD, anchor_locationLatitudeD)  # in meters
    
    
    # inputCRS
    # based on assumption that both anchorLocation_ input and required_location belong to the same UTM zone
    inputCRS = gismo_osm.UTM_CRS_from_latitude(anchor_locationLatitudeD, anchor_locationLongitudeD, anchor_locationLatitudeD, anchor_locationLongitudeD)
    
    # outputCRS
    EPSGcode = 4326
    outputCRS = gismo_osm.CRS_from_EPSGcode(EPSGcode)
    
    
    latitudeLongitudePt = gismo_osm.convertBetweenTwoCRS(inputCRS, outputCRS, (anchor_originProjected_meters.X - anchorOrigin_meters.X) + requiredPoint_meters.X, (anchor_originProjected_meters.Y - anchorOrigin_meters.Y) + requiredPoint_meters.Y)
    required_location = gismo_preparation.constructLocation(locationName, latitudeLongitudePt.Y, latitudeLongitudePt.X, timeZone, elevation)
    
    
    validInputData = True
    printMsg = "ok"
    
    return required_location, validInputData, printMsg

level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_osm = sc.sticky["gismo_OSM"]()
        
        location, validInputData, printMsg = main(_point, anchorLocation_, anchorOrigin_)
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