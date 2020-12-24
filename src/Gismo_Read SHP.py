# read SHP
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
Use this component to read shapefile (.shp).
Its shapes will be always reprojected to UTM coordinate system.
-
Provided by Gismo 0.0.3
    
    input:
        _shpFile: File path to shapefile (.shp).
        _location: Represents anchor latitude,longitude coordinates which correspond to origin_ in Rhino scene.
                   -
                   Use 'Gismo_SHP to Location' component, or 'Gismo_Construct Location' components for this input."
        origin_: A point in Rhino scene which corresponds to anchorLocation_.
                -
                If nothing added to this input, origin will be set to: 0,0,0.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        bakeIt_: Set to "True" to bake the shapes geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    output:
        readMe!: ...
        shapes: Geometry of each shapefile shape.
                It can be either a point or an open/closed polyline, depening on the type of the input shapefile.
        keys: A list of keys for all shapes.
              For example: address, type of the building, area etc.
        values: Values corresponding to each key, for each shape.
                Each upper shape contains a value which corresponds to a certain key (example: "key=addr_street; value=Second Avenue 14/2", "key=building; value=yes", "key:area; value=100" etc.)
"""

ghenv.Component.Name = "Gismo_Read SHP"
ghenv.Component.NickName = "ReadShapefile"
ghenv.Component.Message = "VER 0.0.3\nDEC_24_2020"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | Gismo"
#compatibleGismoVersion = VER 0.0.3\nDEC_24_2020
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import Rhino
import math
import os



def main(shpFile, anchorLocation, north, originPt):
    
    # check inputs
    
    # _shpFile
    if (shpFile == None):
        locationName = latitude = longitude = northDeg = originPt = shortenedName_keys = values = shapes = shapefileShapeType = proj4_str = None
        validShapes = False
        printMsg = "Please add file path of the shapefile(.shp) to '_shpFile' input."
        return locationName, latitude, longitude, northDeg, originPt,  shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg
    else:
        filePathValid = os.path.isfile(shpFile)
        if (filePathValid == False):
            locationName = latitude = longitude = northDeg = originPt = shortenedName_keys = values = shapes = shapefileShapeType = proj4_str = None
            validShapes = False
            printMsg = "'_shpFile' input is incorrect. Correct its filepath."
            return locationName, latitude, longitude, northDeg, originPt,  shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg
    
    
    # _anchorLocation
    if (anchorLocation == None):
        locationName = latitude = longitude = northDeg = originPt = shortenedName_keys = values = shapes = shapefileShapeType = proj4_str = None
        validShapes = False
        printMsg = "Please add location to '_location' input.\n" + \
                   "Use 'Gismo_SHP to Location' component, or 'Gismo_Construct Location' components for this input."
        return locationName, latitude, longitude, northDeg, originPt,  shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg
    else:
        locationName, latitude, longitude, timeZone, elevation = gismo_prep.deconstructLocation(anchorLocation)
    
    
    # north_
    northRad, northVec = gismo_prep.angle2northClockwise(north)
    northDeg = math.degrees(northRad)
    
    # _runIt
    if (_runIt == False):
        locationName = latitude = longitude = northDeg = originPt = shortenedName_keys = values = shapes = shapefileShapeType = proj4_str = None
        validShapes = False
        printMsg = "All inputs are ok. Please set \"_runIt\" to True, in order to run the Read SHP component."
        return locationName, latitude, longitude, northDeg, originPt,  shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg
    
    
    
    
    # check units
    unitConversionFactor, unitSystemLabel = gismo_prep.checkUnits()
    
    # read SHP
    shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg = gismo_gis.readSHPfile(shpFile, float(latitude), float(longitude), northRad, originPt, unitConversionFactor, osm_id_Only=[], osm_way_id_Only=[], osm_id_Remove=[], osm_way_id_Remove=[])  # from 'unitConversionFactor' input onwards, inputs are default - do not change them
    
    if not validShapes:
        locationName = latitude = longitude = northDeg = originPt = shortenedName_keys = values = shapes = shapefileShapeType = proj4_str = None
        validShapes = False
        return locationName, latitude, longitude, northDeg, originPt,  shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg
    
    
    
    
    # bake
    if bakeIt_:
        folder, filename = gismo_prep.splitFolderAndFile(shpFile)
        lay = filename
        
        layParentName = "GISMO"; laySubName = "SHP"; layCategoryName = shapefileShapeType; newLayerCategory = False
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(0,0,0)  # black
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layIndex, lay_dummy = gismo_prep.createLayer(layParentName, laySubName, layCategoryName, newLayerCategory, lay, laySubName_color, layerColor) 
        
        # convert 'shapes' DT to L
        shapes_LL = gismo_prep.grasshopperDTtoLL(shapes)
        shapes_L = gismo_prep.flattenLL(shapes_LL)
        
        
        geometry_id_L = gismo_prep.bakeGeometry(shapes_L, layIndex)
    
    
    
    
    validShapes = True
    printMsg = "ok"
    
    return locationName, latitude, longitude, northDeg, originPt,  shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg


def printOutput(locationName, latitude, longitude, northDeg, originPt, shapefileShapeType, proj4_str):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "Read SHP component results successfully completed {}!".format( bakedOrNot )
    printOutputMsg = \
    """
Input data:

Location (deg.): {}
Latitude (deg.): {}
Longitude (deg.): {}
North (deg.): {}
Origin: {}

Shape type: {}
Input proj4 string: '{}'
    """.format(locationName, latitude, longitude, northDeg, originPt, shapefileShapeType, proj4_str)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_prep = sc.sticky["gismo_Preparation"]()
        gismo_gis = sc.sticky["gismo_GIS"]()
        
        locationName, latitude, longitude, northDeg, originPt, keys, values, shapes, shapefileShapeType, proj4_str, validShapes, printMsg = main(_shpFile, _location, north_, origin_)
        if not validShapes:
            print printMsg
            if not printMsg.startswith("All inputs"):  # if '_runIt=False'
                ghenv.Component.AddRuntimeMessage(level, printMsg)
        else:
            printOutput(locationName, latitude, longitude, northDeg, originPt, shapefileShapeType, proj4_str)
            #print "Read SHP component successfully ran."
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
