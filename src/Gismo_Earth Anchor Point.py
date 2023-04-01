# earth anchor point
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2019, Djordje Spasic <djordjedspasic@gmail.com>
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to get or set 'EarthAnchorPoint' property of the currently opened Rhino .3dm file. The following properties are provided/set: locationName, latitude, longitude.
-
Provided by Gismo 0.0.3

    input:
        location_: An .epw file location: joined string containing information about location's components: locationName, latitude, longitude, timeZone and elevation.
                   If this input is empty, then the 'EarthAnchorPoint' property of the currently opened Rhino .3dm file, will be returned in the outputs of this component.
                   If this input is not empty, 'EarthAnchorPoint' property of the currently opened Rhino .3dm file, will be modified according this new 'location_' data.
    
    output:
        readMe!: ...
        locationName: A name of the location.
                      -
                      If nothing added to this input, "unknown location" will be used as default locationName_.
        latitude: Location's latitude coordinate.
                   It ranges from -90 for locations south of equator, to 90 for locations above the equator.
        longitude: Location's longitude coordinate.
                    It ranges from -180 for locations west of Prime Meridian, to 180 for locations east of Prime Meridian.
"""

ghenv.Component.Name = "Gismo_Earth Anchor Point"
ghenv.Component.NickName = "EarthAnchorPoint"
ghenv.Component.Message = "VER 0.0.3\nAPR_01_2023"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "0 | Gismo"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import Rhino


def RhinoEarthAnchorPt(locationStr=None):
    """
    get 'EarthAnchorPoint' object from the current .3dm file.
    if 'locationStr' is provided, then 'EarthAnchorPoint' obj in the current .3dm file will be replaced with 'locationStr' data.
    """
    
    # a) get 'EarthAnchorPoint' info obj from current .3dm file
    earthAnchorPt = Rhino.RhinoDoc.ActiveDoc.EarthAnchorPoint
    
    locationName = earthAnchorPt.Name
    latitude = earthAnchorPt.EarthBasepointLatitude
    longitude = earthAnchorPt.EarthBasepointLongitude
    
    
    
    
    # b) set 'EarthAnchorPoint' info obj from current .3dm file
    if locationStr:  # 'locationStr' input is not 'None'
        locationName, latitude_str, longitude_str, timeZone_dumm, elevation_dumm = gismo_preparation.deconstructLocation(locationStr)
        
        # convert from string to numbers
        latitude = float(latitude_str)
        longitude = float(longitude_str)
        
        # assign properties
        earthAnchorPt.Name = locationName
        earthAnchorPt.EarthBasepointLatitude = latitude  # 'latitude' is in decimal degrees. RhinoCommon will automatically convert it to degrees, minutes and seconds (DMS)
        earthAnchorPt.EarthBasepointLongitude = longitude  # 'longitude' is in decimal degrees. RhinoCommon will automatically convert it to degrees, minutes and seconds (DMS)
        
        
        # assing the 'EarthAnchorPoint' object back to current .3dm file
        Rhino.RhinoDoc.ActiveDoc.EarthAnchorPoint = earthAnchorPt  # assign the upper new values back to current .3dm file
    
    
    locationStr_current = gismo_preparation.constructLocation(locationName, latitude, longitude)
    
    return locationStr_current



level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        locationStr_current = RhinoEarthAnchorPt(location_)
        locationName, latitude, longitude, timeZone_dumm, elevation_dumm = gismo_preparation.deconstructLocation(locationStr_current)
    
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
