# location to xy
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
Use this component to calculate the point in Rhino scene based on latitude and longitude coordinates (_location input).
For example: you created some building shapes with Gismo "OSM Shapes" component, and now you would like to check where among those shapes does particular latitude, longitude location lies.
-
Provided by Gismo 0.0.2
    
    input:
        _location: A location (latitude,longitude coordinates) which is suppose to be projected in Rhino scene.
        anchorLocation_: Represents latitude,longitude coordinates which correspond to anchorOrigin_ in Rhino scene.
                         -
                         If nothing added to this input, anchorLocation_ with both latitude and longitude set to "0" will be used as a default.
        anchorOrigin_: A point in Rhino scene which corresponds to anchorLocation_.
                       -
                       If nothing added to this input, anchorOrigin will be set to: 0,0,0.
    output:
        readMe!: ...
        point: A projected point in Rhino scene which coresponds to "_location" latitude and longitude coordinates.
                       -
                       In Rhino document units (meters, feets...).
"""

ghenv.Component.Name = "Gismo_Location To XY"
ghenv.Component.NickName = "LocationToXY"
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


def main(requiredLocation, anchorLocation, anchorOrigin):
    
    # check inputs
    if (requiredLocation == None):
        pointElevation_ = None
        validInputData = False
        printMsg = "Please add location from Gismo's \"Create Location\" component, to this component's \"_location\" input."
        return pointElevation_, validInputData, printMsg
    else:
        locationName, required_locationLatitudeD, required_locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_preparation.checkLocationData(requiredLocation)
    
    if (anchorLocation == None):
        anchor_locationLatitudeD = 0
        anchor_locationLongitudeD = 0
    else:
        locationName, anchor_locationLatitudeD, anchor_locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_preparation.checkLocationData(anchorLocation)
    
    if (anchorOrigin == None):
        anchorOrigin = Rhino.Geometry.Point3d(0,0,0)
    
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    anchorOrigin_meters = Rhino.Geometry.Point3d(anchorOrigin.X*unitConversionFactor, anchorOrigin.Y*unitConversionFactor, anchorOrigin.Z*unitConversionFactor)  # in meters
    
    
    # inputCRS
    EPSGcode = 4326
    inputCRS = gismo_osm.CRS_from_EPSGcode(EPSGcode)
    # outputCRS
    outputCRS = gismo_osm.UTM_CRS_from_latitude(required_locationLatitudeD, required_locationLongitudeD)
    
    required_originPtProjected_meters = gismo_osm.convertBetweenTwoCRS(inputCRS, outputCRS, required_locationLongitudeD, required_locationLatitudeD)  # in meters
    required_originPtProjected = Rhino.Geometry.Point3d(required_originPtProjected_meters.X/unitConversionFactor, required_originPtProjected_meters.Y/unitConversionFactor, required_originPtProjected_meters.Z/unitConversionFactor)  # in Rhino document units
    
    
    # inputCRS2 = inputCRS
    
    # outputCRS2
    outputCRS2 = gismo_osm.UTM_CRS_from_latitude(anchor_locationLatitudeD, anchor_locationLongitudeD)
    
    anchor_originPtProjected_meters = gismo_osm.convertBetweenTwoCRS(inputCRS, outputCRS2, anchor_locationLongitudeD, anchor_locationLatitudeD)  # in meters
    anchor_originPtProjected = Rhino.Geometry.Point3d(anchor_originPtProjected_meters.X/unitConversionFactor, anchor_originPtProjected_meters.Y/unitConversionFactor, anchor_originPtProjected_meters.Z/unitConversionFactor)  # in Rhino document units
    
    
    originPtProjectedFinal = required_originPtProjected - anchor_originPtProjected  # in Rhino document units
    transformMatrix = Rhino.Geometry.Transform.Translation(originPtProjectedFinal)
    anchorOrigin.Transform(transformMatrix)
    
    
    validInputData = True
    printMsg = "ok"
    
    return anchorOrigin, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_osm = sc.sticky["gismo_OSM"]()
        
        point, validInputData, printMsg = main(_location, anchorLocation_, anchorOrigin_)
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