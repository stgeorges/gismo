# OSM shapes
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2021, Djordje Spasic <djordjedspasic@gmail.com>
# with assistance of Paul Meems <bontepaarden@gmail.com>
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
Use this component to generate Open Street Map shapes for the chosen _location and radius_.
OSM shapes represent linear or point map elements from openstreetmap.org service - the largest free map online service.
Linear OSM shapes include: buildings footprints, park footprints, roads axes, rivers, lake boundaries, and any other linear map element ...
Point OSM shapes include: trees, bus stations, restaurants, pubs, markets, address plates ...
-
Component requires that you are connected to the Internet, as it has to download osm data.
It also requires MapWinGIS application to be installed in order for it to work. Download the MapWinGIS from:
https://github.com/MapWindow/MapWinGIS/releases
If you are using Rhino 5 x86, then download the "Win32" version.
If you are using Rhino 5 x64, then download the "x64" version.
-
Provided by Gismo 0.0.3
    
    input:
        _location: Output from Gismo's \"Create Location\" component. This is essentially a text containing information (latitude, longitude, name...) about a location on the Earth.
        radius_: Horizontal distance to which the surrounding terrain will be taken into account.
                 -
                 It can not be shorter than 50 meters.
                 It can not be larger than from 5000 to 27000 meters. This depends on _location's latitude. The higher it is, the closer it is to 5000.
                 -
                 The component itself might inform the user to alter the initial radius_ inputted by the user.
                 This is due to restriction of downloadable OSM data being limited to 0.5 latitude x 0.5 longitude range. If radius_ value for the chosen _location is equal to the mentioned range, or larger than it, the component will inform the user to shrink the radius_ for a certain amount.
                 -
                 If not supplied, default value of 100 meters will be used.
                 -
                 In meters.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        origin_: Origin for the final "shapes" output.
                 -
                 If not supplied, default point of (0,0,0) will be used.
        shapeType_: There are four shape geometry types:
                    -
                    0 - polygons: anything consisted of closed polygons: buildings, grass areas, forests, lakes, etc
                    1 - polylines: non closed polylines as: streets, roads, highways, rivers, canals, train tracks ...
                    2 - points: any point features, like:
                               Trees, building entrances, junctions between roads ...
                               Store locations: restaurants, bars, pharmacies, post offices ...
                    -
                    If nothing supplied, 0 will be used as a default value (polygons).
        requiredKeys_: A list of specific OpenStreetMap keys that you would like to use for each "shapeType_" input.
                       -
                       There are thousands of OpenStreetMap keys describing various map elements. You can find them listed in here: www.taginfo.openstreetmap.org/keys
                       -
                       However due to their enormous number it is suggested that you use the "OSM keys" component, which will automatically generate specific keys for specific object type.
                       Either that, or simply leave this input empty. It that way the component will take only those keys which are attached to all shapeType_ shapes.
                       -
                       If not supplied, only those keys that appear at that particular "location_" and "radius_" will be used.
        onlyRemove_Ids_: Use this input to define lists of Open Street Map ids. "OSM ids" component will generate them.
                         -
                         These lists can be used to define:
                         1) only those ids which will be included (isolated) when "OSM shapes" component is ran (use "osm_id_Only" and "osm_way_id_Only" inputs for this).
                         2) ids which will be removed when "OSM shapes" component is ran (use "osm_id_Remove" and "osm_way_id_Remove" inputs for this).
                         3) you can combine 1) and 2) and both define the: included and removed ids.
                         -
                         If nothing supplied to this input, then no OSM ids will be isolated nor removed: meaning all of them will be included.
        bakeIt_: Set to "True" to bake the shapes geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        shapes: Geometry of each shape.
                -
                Depening on the shapeType_ input this can be either a polygon (shapeType_ = 0), a polyline (shapeType_ = 1) or a point (shapeType_ = 2)
        keys: Each upper shape contains certain information (keys) attached to it (example: address, type of the building, area etc.).
              This output lists the available keys for all the shapes, or 
              in case some specific keys have been supplied to the "requiredKeys_" output, then they will be listed here.
        values: Each upper shape contains a value which corresponds to a certain key (example: "key=addr_stree; value=Second Avenue 14/2", "key=building; value=yes", "key:area; value=100" etc.)
                This ouput lists all values corresponding to each key, for each shape.
        titleOriginPt: Title base point, which can be used to move the "title" geometry with grasshopper's "Move" component.
                       -
                       Connect this output to a Grasshopper's "Point" parameter in order to preview the point in the Rhino scene.
        title: Title geometry with information about location, radius, north angle and shapeType.
"""

ghenv.Component.Name = "Gismo_OSM Shapes"
ghenv.Component.NickName = "OSMshapes"
ghenv.Component.Message = "VER 0.0.3\nOCT_28_2021"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import shutil
import Rhino
import math
import time
import clr
import os
import gc


def checkInputData(radiusM, north, originPt, shapeType, requiredKeys, onlyRemove_Ids):
    
    # check if MapWinGIS is properly installed
    gismoGismoComponentNotRan = False  # initial value
    if sc.sticky.has_key("gismo_mapwingisFolder"):
        mapFolder_ = sc.sticky["gismo_mapwingisFolder"]
        iteropMapWinGIS_dll_folderPath, gdalDataPath_folderPath, validInputData, printMsg = gismo_mainComponent.mapWinGIS(mapFolder_)
        if not validInputData:
            radiusM = northRad = northDeg = originPt = requiredKeys = shapeType = shapeTypeLabel = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = iteropMapWinGIS_dll_folderPath = unitConversionFactor = None
            return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg
        if sc.sticky.has_key("MapWinGIS"):
            global MapWinGIS
            import MapWinGIS
        else:
            gismoGismoComponentNotRan = True
    else:
        gismoGismoComponentNotRan = True
    
    if (gismoGismoComponentNotRan == True):
        radiusM = northRad = northDeg = originPt = requiredKeys = shapeType = shapeTypeLabel = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = iteropMapWinGIS_dll_folderPath = unitConversionFactor = None
        validInputData = False
        printMsg = "The \"Gismo Gismo\" component has not been run. Run it before running this component."
        return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg
    
    
    # check inputs
    if (radiusM == None):
        radiusM = 100  # default in meters
    elif (radiusM < 50):  # values of 10 or 20 meters can download an invalid .osm file from http://api.openstreetmap.org
        radiusM = northRad = northDeg = originPt = requiredKeys = shapeType = shapeTypeLabel = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = iteropMapWinGIS_dll_folderPath = unitConversionFactor = None
        validInputData = False
        printMsg = "radius_ input only supports values equal or larger than 50 meters."
        
        return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg
    #arcAngleD = math.degrees( math.atan( radiusM / (6371000+elevation) ) )  # assumption of Earth being a sphere
    #arcLength = (arcAngleD*math.pi*R)/180
    # correction of radiusM length due to light refraction can not be calculated, so it is assumed that arcLength = radiusM. radiusM variable will be used from now on instead of arcLength.
    
    
    if (north == None):
        northRad = 0  # default, in radians
        northVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            north = float(north)
            if north < 0 or north > 360:
                radiusM = northRad = northDeg = originPt = requiredKeys = shapeType = shapeTypeLabel = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = iteropMapWinGIS_dll_folderPath = unitConversionFactor = None
                validInputData = False
                printMsg = "Please input north angle value from 0 to 360."
                return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = gismo_preparation.angle2northClockwise(north)
    northVec.Unitize()
    northDeg = int(360-math.degrees(northRad))
    if northDeg == 360: northDeg = 0
    
    
    if (originPt == None):
        originPt = Rhino.Geometry.Point3d(0,0,0)
    # send the origin of this component ("OSM shapes") to sc.sticky, in order for it be used in the "OSM 3D" and "OSM search" components
    sc.sticky["gismo_OSMshapesComp_origin"] = originPt
    
    
    if (len(requiredKeys) == 0):
        requiredKeys = []
    elif (len(requiredKeys) > 250):
        # .dbf files require maximal number of fields to be 255 (254 if one of the fields contains None values)
        # source: https://msdn.microsoft.com/en-us/library/3kfd3hw9
        radiusM = northRad = northDeg = originPt = requiredKeys = shapeType = shapeTypeLabel = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = iteropMapWinGIS_dll_folderPath = unitConversionFactor = None
        validInputData = False
        printMsg = "requiredKeys_ input accepts maximum 250 keys.\n" + \
                   "You inputted %s keys. Remove some of them." % len(requiredKeys)
        requiredKeys = None  # set in here so that it can be printed in the printMsg
        return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg
    
    
    if (shapeType == None):
        shapeType = 0  # polygons
        shapeTypeLabel = "polygons"
    elif (shapeType == 0):
        shapeTypeLabel = "polygons"
    elif (shapeType == 1):
        shapeTypeLabel = "polylines"
    elif (shapeType == 2):
        shapeTypeLabel = "points"
    elif (shapeType < 0) or (shapeType > 2):
        radiusM = northRad = northDeg = originPt = requiredKeys = shapeType = shapeTypeLabel = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = iteropMapWinGIS_dll_folderPath = unitConversionFactor = None
        validInputData = False
        printMsg = "shapeType_ input can not be smaller than 0, nor larger than 2.\n" + \
                   "Please input some of the following values:\n" + \
                   "0 (polygons)\n" + \
                   "1 (polylines)\n" + \
                   "2 (points)."
        return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg
    
    
    if (onlyRemove_Ids.BranchCount == 1) and (onlyRemove_Ids.Branches[0][0] == None):
        # in "OSM ids" component, an id exists both in "osm_id_Only_" and "osm_id_Remove_" inputs,  or an id exists both in "osm_way_id_Only_" and "osm_way_id_Remove_" inputs
        radiusM = northRad = northDeg = originPt = requiredKeys = shapeType = shapeTypeLabel = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = iteropMapWinGIS_dll_folderPath = unitConversionFactor = None
        validInputData = False
        printMsg = "Your \"_onlyRemove_Ids\" input is invalid. Check the \"readMe!\" output of \"OSM ids\" component to see what's wrong with it."
        return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg
    elif (onlyRemove_Ids.BranchCount == 0):
        # nothing inputted to "OSM ids" component's four inputs
        osm_id_Only = [];  osm_way_id_Only = [];  osm_id_Remove = [];  osm_way_id_Remove = []
    else:
        # something inputted to at least one input of "OSM ids" component
        onlyRemove_IdsLL = onlyRemove_Ids.Branches
        osm_id_Only = list(onlyRemove_IdsLL[0])
        osm_way_id_Only = list(onlyRemove_IdsLL[1])
        osm_id_Remove = list(onlyRemove_IdsLL[2])
        osm_way_id_Remove = list(onlyRemove_IdsLL[3])
    
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    
    
    validInputData = True
    printMsg = "ok"
    
    return radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg


def setupOsmconf_ini_File(requiredKeys, shapeType, overpassFile_filePathL, osmconf_ini_filePath):
    
    # identify unique keys from overpassFile_filePathL files
    if (len(requiredKeys) == 0):
        # nothing supplied to "requiredKeys_" input. Use the keys provided in the .osm file
        fullName_keysL = []
        for overpassFile_filePath in overpassFile_filePathL:
            requiredKeys = []
            
            # open the overpassFile files (4 of them) one by one
            with open(overpassFile_filePath) as overpassFile:
                foundTags = False
                lines = overpassFile.readlines()
                for line in lines:
                    if "tags" in line:
                        # "  "tags": {" line found
                        foundTags = True
                        continue  # start extracting the tags below it
                    if (foundTags == True) and ("}" not in line):
                        strippedLine = line.strip()
                        splittedLine = strippedLine.split(": ")
                        fieldName = splittedLine[0].replace("\"", "")
                        requiredKeys.append(fieldName)
                    else:
                        foundTags = False
                    
                foundTags = False
                overpassFile.close()
                del lines; del overpassFile
                
                #print "requiredKeys: ", requiredKeys
                requiredKeysSet = set(requiredKeys)
                uniqueKeys = list(requiredKeysSet)
                uniqueKeys.sort()  # sort the keys alphabetically
                fullName_keysL.append(uniqueKeys)
    
    elif (len(requiredKeys) != 0):
        # something supplied to "requiredKeys_" input. Use those keys
        fullName_keysL = [requiredKeys, requiredKeys, requiredKeys, requiredKeys, requiredKeys]  # polygons, points, polylines, polylines2, irrelevant
    
    
    
    # create lines for the new osmconf.ini file by inserting the fullName_keysL to each section ([points], [lines], [multipolygons], [multilinestrings], [other_relations])
    osmconf_ini_newFileLines = []
    points_tagPassed = False; lines_tagPassed = False; multipolygons_tagPassed = False; multilinestrings_tagPassed = False; other_relations_tagPassed = False  # initial values
    
    # open the current "osmconf.ini" file and iterate through its lines in order to create the new "osmconf.ini" file
    with open(osmconf_ini_filePath) as osmconf_ini_File:
        lines = osmconf_ini_File.readlines()
        for line in lines:
            # setting keys are considered to be polygons. This puts all shapes with these keys into the multipolygons.shp file. Otherwise (their key is not listed in this line) if they are closed ways, they will be put into the lines.shp file
            if line.startswith("closed_ways_are_polygons="):
                line = "closed_ways_are_polygons=aeroway,amenity,boundary,building,building:levels,building:part,craft,geological,historic,landuse,leisure,military,natural,office,place,shop,sport,tourism\n"
            
            # checking for switches
            if (line == "[points]\n"):
                points_tagPassed = True
            elif (line == "[lines]\n"):
                lines_tagPassed = True
            elif (line == "[multipolygons]\n"):
                multipolygons_tagPassed = True
            elif (line == "[multilinestrings]\n"):
                multilinestrings_tagPassed = True
            elif (line == "[other_relations]\n"):
                other_relations_tagPassed = True
            
            # set "other_tags" and "all_tags" to "no"
            if (line == "#other_tags=no\n") or (line == "#other_tags=yes\n") or (line == "other_tags=yes\n"):
                line = "other_tags=no\n"
            if (line == "#all_tags=no\n") or (line == "#all_tags=yes\n") or (line == "all_tags=yes\n"):
                line = "all_tags=no\n"
            # set "attribute_name_laundering" to "no" (do not change ":" to "_" in key names)
            if (line == "#attribute_name_laundering=yes\n") or (line == "attribute_name_laundering=no\n") or (line == "attribute_name_laundering=yes\n"):
                line = "#attribute_name_laundering=no\n"
            # comment-out certain 3 lines to remove the "z_order" key from [lines].
            if line.startswith("computed_attributes="):
                line = "#" + line
            if line.startswith("z_order_type="):
                line = "#" + line
            if line.startswith("z_order_sql="):
                line = "#" + line
            
            if (points_tagPassed == True) and (lines_tagPassed == False) and (multipolygons_tagPassed == False) and (multilinestrings_tagPassed == False) and (other_relations_tagPassed == False):
                if line.startswith("attributes="):
                    line = "attributes="
                    for index, key in enumerate(fullName_keysL[2]):  # [points] (points) keys
                        if index != len(fullName_keysL[2])-1:
                            line = line + key + ","
                        else:
                            # last key in fullName_keysL[1]
                            line = line + key + "\n"
            elif (points_tagPassed == True) and (lines_tagPassed == True) and (multipolygons_tagPassed == False) and (multilinestrings_tagPassed == False) and (other_relations_tagPassed == False):
                if line.startswith("attributes="):
                    line = "attributes="
                    for index, key in enumerate(fullName_keysL[1]):  # [lines] (polylines) keys
                        if index != len(fullName_keysL[1])-1:
                            line = line + key + ","
                        else:
                            # last key in fullName_keysL[2]
                            line = line + key + "\n"
            elif (points_tagPassed == True) and (lines_tagPassed == True) and (multipolygons_tagPassed == True) and (multilinestrings_tagPassed == False) and (other_relations_tagPassed == False):
                if line.startswith("attributes="):
                    line = "attributes="
                    for index, key in enumerate(fullName_keysL[0]):  # [multipolygons] (polygons) keys
                        if index != len(fullName_keysL[0])-1:
                            line = line + key + ","
                        else:
                            # last key in fullName_keysL[0]
                            line = line + key + "\n"
            elif (points_tagPassed == True) and (lines_tagPassed == True) and (multipolygons_tagPassed == True) and (multilinestrings_tagPassed == True) and (other_relations_tagPassed == False):
                if line.startswith("attributes="):
                    line = "attributes="
                    for index, key in enumerate(fullName_keysL[3]):  # [multilinestrings] (polylines2) keys
                        if index != len(fullName_keysL[3])-1:
                            line = line + key + ","
                        else:
                            # last key in fullName_keysL[3]
                            line = line + key + "\n"
            elif (points_tagPassed == True) and (lines_tagPassed == True) and (multipolygons_tagPassed == True) and (multilinestrings_tagPassed == True) and (other_relations_tagPassed == True):
                if line.startswith("attributes="):
                    line = "attributes="
                    for index, key in enumerate(fullName_keysL[4]):  # [other_relations] keys
                        if index != len(fullName_keysL[4])-1:
                            line = line + key + ","
                        else:
                            # last key in fullName_keysL[4]
                            line = line + key + "\n"
            
            osmconf_ini_newFileLines.append(line)
    
    points_tagPassed = False; lines_tagPassed = False; multipolygons_tagPassed = False; multilinestrings_tagPassed = False; other_relations_tagPassed = False  # setting them back to "False" values
    osmconf_ini_File.close()
    #os.remove(osmconf_ini_filePath)  # delete the original "osmconf.ini" file
    
    
    # create the new osmconf.ini file
    new_osmconf_ini_FilePath = osmconf_ini_filePath
    
    with open(new_osmconf_ini_FilePath, "w") as new_osmconf_ini_File:
        for line in osmconf_ini_newFileLines:
            new_osmconf_ini_File.write(line)
    new_osmconf_ini_File.close()
    
    
    # deleting
    del lines
    del osmconf_ini_File
    del new_osmconf_ini_File
    del osmconf_ini_newFileLines
    
    
    # return fullName_keysL (unlike those from the shapefiles ("shortenedName_keys") these are not limited to 10 characters and do not have ":" replaced with "_")
    if shapeType == 0:
        return ["osm_id", "osm_way_id"] + fullName_keysL[shapeType]
    else:
        return ["osm_id"] + fullName_keysL[shapeType]


def checkOsmShpFiles(locationLatitudeD, locationLongitudeD, fileNameIncomplete, radiusM, requiredKeys, shapeType):
    
    latitudeTopD, longitudeTopD, latitudeBottomD, longitudeBottomD, latitudeLeftD, longitudeLeftD, latitudeRightD, longitudeRightD = gismo_gis.destinationLatLon(locationLatitudeD, locationLongitudeD, radiusM)
    
    # check if osm region is 0.5x0.5 degrees
    validRadiusM = True  # initial value
    if ((latitudeTopD - latitudeBottomD) >= 0.5):
        validRadiusM = False
        latitude2D = locationLatitudeD - 0.24  # 0.24 is 0.25*2 (0.25 from both sides of the _location) - 0.01 (for safety)
        longitude2D = locationLongitudeD
        distanceM = gismo_gis.distanceBetweenTwoPoints(locationLatitudeD, locationLongitudeD, latitude2D, longitude2D)
        correctedRadiusM_for_latitude = int(distanceM)  # int(distanceM) will always perform the math.floor(distanceM)
    if ((longitudeRightD - longitudeLeftD) >= 0.5):
        validRadiusM = False
        latitude2D = locationLatitudeD 
        longitude2D = locationLongitudeD - 0.24  # 0.24 is 0.25*2 (0.25 from both sides of the _location) - 0.01 (for safety)
        distanceM = gismo_gis.distanceBetweenTwoPoints(locationLatitudeD, locationLongitudeD, latitude2D, longitude2D)
        correctedRadiusM_for_longitude = int(distanceM)  # int(distanceM) will always perform the math.floor(distanceM)
    
    if (validRadiusM == False):
        #print "correctedRadiusM_for_latitude, correctedRadiusM_for_longitude: ", correctedRadiusM_for_latitude, ",", correctedRadiusM_for_longitude
        shapeFile_filePath = fullName_keys = None
        printMsg = "This component downloads map data from openstreetmap.org in order to create the shapes for the chosen _location.\n" + \
                   "But mentioned openstreetmap.org download data has limits: the radius can not be longer than 0.25 degrees of latitude and longitude.\n" + \
                   "This is why the inputted radius_ value, needs to be shrank.\n" + \
                   " \n" + \
                   "Please supply the \"radius_\" input with the value not larger than: %s.\n" % min(correctedRadiusM_for_latitude, correctedRadiusM_for_longitude)  # always choose the smallest corrected radius
        return shapeFile_filePath, fullName_keys, validRadiusM, printMsg
    
    
    
    # create "gismoFolder_\osm_files" folder
    # always use the "gismoFolder_" input of Gismo_Gismo component + "\osm_files" as the working folder for downloaded .osm files and converted shapefiles
    gismoFolder = sc.sticky["gismo_gismoFolder"]  # "gismoFolder_" input of Gismo_Gismo component
    osm_files_folderPath = os.path.join(gismoFolder, "osm_files")
    if not os.path.isdir(osm_files_folderPath):
        os.mkdir(osm_files_folderPath)
    
    # fileNames
    fileName = fileNameIncomplete + "_radius=" + str(round(radiusM/1000, 2)) + "KM"
    osm_shp_file_folderPath = os.path.join(osm_files_folderPath, fileName)
    if not os.path.isdir(osm_shp_file_folderPath):
        os.mkdir(osm_shp_file_folderPath)
    
    osmFile_filePath = os.path.join(osm_shp_file_folderPath, fileName + ".osm")
    
    osmconf_ini_filePath = os.path.join(iteropMapWinGIS_dll_folderPath, "gdal-data\\osmconf.ini")  # for MapWinGIS
    osmconf_ini_present = os.path.isfile(osmconf_ini_filePath)
    if osmconf_ini_present == False:
        osmconf_ini_filePath = os.path.join(iteropMapWinGIS_dll_folderPath, "MapWinGIS\\gdal-data\\osmconf.ini")  # for Map Window GIS Light
    
    overpassFile_nodeTags_filePath = os.path.join(osm_shp_file_folderPath, fileName + "_nodeTags" + ".txt")
    overpassFile_wayTags_filePath = os.path.join(osm_shp_file_folderPath, fileName + "_wayTags" + ".txt")
    overpassFile_filePathL = [overpassFile_wayTags_filePath, overpassFile_wayTags_filePath, overpassFile_nodeTags_filePath, overpassFile_wayTags_filePath, overpassFile_wayTags_filePath]  # [ [multipolygons] (polygons) keys, [lines] (polylines) key, [points] (points) key, [multilinestrings] (we use polylines again) key, [other_relations] (we use polylines again) keys ]
    
    shpMultipolygonsFile_filePath = os.path.join(osm_shp_file_folderPath, "multipolygons" + ".shp")
    shpLinesFile_filePath = os.path.join(osm_shp_file_folderPath, "lines" + ".shp")
    shpPointsFile_filePath = os.path.join(osm_shp_file_folderPath, "points" + ".shp")
    shpMultilinestringsFile_filePath = os.path.join(osm_shp_file_folderPath, "multilinestrings" + ".shp")
    
    
    #  check internet connection
    connectedToInternet = gismo_preparation.checkInternetConnection()
    
    
    # always delete the .shp/.shx/.dbg/.prj files, whenever the "OSM Shapes" component is run
    files = os.listdir(osm_shp_file_folderPath)
    for fileNameWithExtension in files:
        fileExtension = fileNameWithExtension[-4:]
        if (fileExtension != ".osm") and (fileExtension != ".txt"):  # delete only .shp/.shx/.dbf/.prj files
            filePath = os.path.join(osm_shp_file_folderPath, fileNameWithExtension)
            os.remove(filePath)
    
    
    if len(requiredKeys) != 0:
        # something supplied to the "requiredKeys_" input, use those keys for the osmconf.ini file
        pass
    else:
        # nothing supplied to the "requiredKeys_" input
        # 2) check if overpassNodeTags....txt, overpassWayTags....txt, overpassRelationTags....txt files exist in "osm_files\osm_shp_file_folderPath\" folder
        if os.path.isfile(overpassFile_nodeTags_filePath) and os.path.isfile(overpassFile_wayTags_filePath):
            # 2) overpassNodeTags....txt, overpassWayTags....txt, overpassRelationTags....txt files EXIST in "osm_files\osm_shp_file_folderPath\" folder. Extract the "requiredKeys" from them
            requiredKeys = []
        else:
            # overpassNodeTags....txt, overpassWayTags....txt, overpassRelationTags....txt files DO NOT exist in "osm_files\osm_shp_file_folderPath\" folder
            downloadOverpassNodeFile_link = "http://overpass-api.de/api/interpreter?data=[out:json];node[~\".\"~\".\"](%s,%s,%s,%s);out;" % (latitudeBottomD, longitudeLeftD, latitudeTopD, longitudeRightD)
            downloadOverpassWayFile_link = "http://overpass-api.de/api/interpreter?data=[out:json];way[~\".\"~\".\"](%s,%s,%s,%s);out;" % (latitudeBottomD, longitudeLeftD, latitudeTopD, longitudeRightD)
            
            overpassNodeFileDownloaded = gismo_preparation.downloadFile(downloadOverpassNodeFile_link, overpassFile_nodeTags_filePath)
            overpassWayFileDownloaded = gismo_preparation.downloadFile(downloadOverpassWayFile_link, overpassFile_wayTags_filePath)
            
            if (overpassNodeFileDownloaded == True) and (overpassWayFileDownloaded == True):
                # overpassNodeTags....txt, overpassWayTags....txt, overpassRelationTags....txt files SUCCESSFULLY DOWNLOADED in "osm_files\osm_shp_file_folderPath\" folder. Extract the "requiredKeys" from them
                requiredKeys = []
            else:
                # one of the overpass .txt files has NOT BEEN DOWNLOADED. Use default requiredKeys:
                requiredKeys = ["name",
                                "name:en",
                                "amenity",
                                "addr:country",
                                "addr:city",
                                "addr:postcode",
                                "addr:street",
                                "addr:housenumber",
                                "height",
                                "building:levels",
                                "min_height",
                                "building",
                                "natural",
                                "leaf_type",
                                "leaf_cycle",
                                "diameter_crown"]
                if connectedToInternet == True:
                    print "Component failed to retrieve keys from the .osm file.\n" + \
                          "The following default list of keys will be used instead:\n" + \
                          "%s\n" % requiredKeys + \
                          " \n" + \
                          "You can also define your own keys through \"requiredKeys_\" input."
                elif connectedToInternet == False:
                    print "This component requires internet access in order to retrieve the keys from the .osm file.\n" + \
                          "As there's no internet access, default list of keys will be used instead:\n" + \
                          "%s\n" % requiredKeys + \
                          " \n" + \
                          "You can also define your own keys through \"requiredKeys_\" input."
    
    fullName_keys = setupOsmconf_ini_File(requiredKeys, shapeType, overpassFile_filePathL, osmconf_ini_filePath)
    
    
    # 1) check if lines.shp, multilinestrings....shp, multipolygons....shp, points....shp files exist in "osm_files\osm_shp_file_folderPath\" folder
    if os.path.isfile(shpMultipolygonsFile_filePath) and os.path.isfile(shpLinesFile_filePath) and os.path.isfile(shpPointsFile_filePath) and os.path.isfile(shpMultilinestringsFile_filePath):
        #print "_1_SHP files exist!"
        # lines.shp, multilinestrings.shp, multipolygons.shp, points.shp files EXIST in "osm_files\osm_shp_file_folderPath\" folder. Disregard the .osm file
        valid_osm_or_shp_files = True
        osmToShpSwitch = False  # dummy value
        printMsg = "ok"
    else:
        #print "_1_SHP files DO NOT exist"
        # lines.shp, multilinestrings.shp, multipolygons.shp, points.shp files do NOT exist in "osm_files\osm_shp_file_folderPath\" folder
        # check if .osm file exists in "osm_files\osm_shp_file_folderPath\" folder
        if os.path.isfile(osmFile_filePath):
            ####print "_2_OSM files exist!"
            # the .osm file exists. Convert it to 4 .shp files
            osmToShpSwitch = True
        else:
            ####print "_2_OSM file DOES NOT exist"
            # the .osm file does NOT exist. Download it first
            
            if connectedToInternet == False:
                # you are NOT connected to the Internet, exit this function
                shpLinesFile_filePath = shpMultilinestringsFile_filePath = shpMultipolygonsFile_filePath = shpPointsFile_filePath = None
                valid_osm_or_shp_files = osmToShpSwitch = False
                printMsg = "This component requires you to be connected to the Internet, in order to download the OSM shape data.\n" + \
                           "Please do connect, then rerun the component (set \"_runIt\" to False, then to True)."
            elif connectedToInternet == True:
                # you ARE connected to the Internet
                
                # download .osm file
                # based on: http://wiki.openstreetmap.org/wiki/Downloading_data
                downloadOSMfile_link = "http://overpass-api.de/api/map?bbox=%s,%s,%s,%s" % (longitudeLeftD,latitudeBottomD,longitudeRightD,latitudeTopD)
                osmFileDownloaded = gismo_preparation.downloadFile(downloadOSMfile_link, osmFile_filePath)
                
                if osmFileDownloaded == False:
                    # .osm file has NOT been downloaded
                    shpLinesFile_filePath = shpMultilinestringsFile_filePath = shpMultipolygonsFile_filePath = shpPointsFile_filePath = None
                    valid_osm_or_shp_files = osmToShpSwitch = False
                    printMsg = "This component requires OSM data to be downloaded from openstreetmap.org. It has just failed to do that. Try the following two fixes:\n" + \
                               " \n" + \
                               "1) Sometimes due to large number of requests, the component fails to download the OSM data even if openstreetmap.org website and their services are up and running.\n" + \
                               "In this case, wait a couple of seconds and try rerunning the component.\n" + \
                               " \n" + \
                               "2) Try lowering the \"radius_\" input.\n" + \
                               " \n" + \
                               "If each of two mentioned advices fails, open a new topic about this issue on: www.grasshopper3d.com/group/gismo/forum."
                    
                elif osmFileDownloaded == True:
                    ####print "_OSM successfully downloaded!!!"
                    # .osm file has been downloaded. Convert it to 4 .shp files
                    osmToShpSwitch = True
    
    
    
    if osmToShpSwitch == True:
        # .osm file exists or has been downloaded. Convert it to 4 .shp files
        utils = MapWinGIS.UtilsClass()
        bstrOptions = '--config OSM_USE_CUSTOM_INDEXING NO -skipfailures -f "ESRI Shapefile"'
        convertToShapefilesResult = MapWinGIS.UtilsClass.OGR2OGR(utils, osmFile_filePath, osm_shp_file_folderPath, bstrOptions, None)
        if convertToShapefilesResult == False:
            # converting an .osm file to a .shp file failed. Possible "HTTP" error
            convertErrorNo = MapWinGIS.GlobalSettingsClass().GdalLastErrorNo
            convertErrorMsg = MapWinGIS.GlobalSettingsClass().GdalLastErrorMsg
            convertErrorType = MapWinGIS.GlobalSettingsClass().GdalLastErrorType
            print "convertErrorNo: ", convertErrorNo
            print "convertErrorMsg: ", convertErrorMsg
            print "convertErrorType: ", convertErrorType
            print "utils.ErrorMsg: ", utils.ErrorMsg
            print "utils.LastErrorCode: ", utils.LastErrorCode
            del utils
            del convertToShapefilesResult
            shpLinesFile_filePath = shpMultilinestringsFile_filePath = shpMultipolygonsFile_filePath = shpPointsFile_filePath = None
            valid_osm_or_shp_files = False
            printMsg = "An error:\n" + \
                       " \n" + \
                       "%s\n" % convertErrorMsg + \
                       " \n" + \
                       "emerged while processing the OSM shape data.\n" + \
                       "Restart Rhino and Grasshopper (close them, then run again) and run this component again.\n" + \
                       "If this same message appears again open a new topic about it on: www.grasshopper3d.com/group/gismo/forum."
        
        else:
            # converting an .osm file to a .shp file SUCCESSFUL
            del utils
            valid_osm_or_shp_files = True
            printMsg = "ok"
    
    if shapeType == 0:
        shapeFile_filePath = shpMultipolygonsFile_filePath
    elif shapeType == 1:
        shapeFile_filePath = shpLinesFile_filePath
    elif shapeType == 2:
        shapeFile_filePath = shpPointsFile_filePath
    elif shapeType == 3:
        shapeFile_filePath = shpMultilinestringsFile_filePath
    
    
    return shapeFile_filePath, fullName_keys, valid_osm_or_shp_files, printMsg


def createShapesKeysValues(locationName, locationLatitudeD, locationLongitudeD, shapeFile_filePath, northRad, originPt, shapeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor):
    
    # this is the "main" function. It extracts shapes from the .shp file
    
    outputCRS = gismo_gis.UTM_CRS_from_latitude(locationLatitudeD, locationLongitudeD)
    
    
    # fix invalid shapes, overlapping shape issues, shape vertices direction ...
    shapefile = MapWinGIS.ShapefileClass()
    openShapefileSuccess = MapWinGIS.ShapefileClass.Open(shapefile, shapeFile_filePath, None)
    if openShapefileSuccess:
        numOfsuccessfullyReprojectedShapes = clr.StrongBox[System.Int32]()
        shapefileFixedSuccess, fixedShapefile = MapWinGIS.ShapefileClass.FixUpShapes(shapefile)  # fails on MapWinGIS 4.9.4.2. Does not fail on Map Window Lite 32x
        if shapefileFixedSuccess:
            # shape file has been fixed
            reprojectedShapefile = MapWinGIS.ShapefileClass.Reproject(shapefile, outputCRS, numOfsuccessfullyReprojectedShapes)
            #reprojectedShapefile = MapWinGIS.ShapefileClass.Reproject(fixedShapefile, outputCRS, numOfsuccessfullyReprojectedShapes)
        else:
            # shapefile has NOT been fixed. Use the initial shapefile
            reprojectedShapefile = MapWinGIS.ShapefileClass.Reproject(shapefile, outputCRS, numOfsuccessfullyReprojectedShapes)
        
        """
        # testing fixing of shapes
        print "numOfsuccessfullyReprojectedShapes: ", numOfsuccessfullyReprojectedShapes
        print "reprojectedShapefile: ", reprojectedShapefile
        # testing MapWinGIS.ShapefileClass.FixUpShapes
        shapeFile_filePath_saved = shapeFile_filePath[:-4] + "_saved_" + str(int(time.time())) + ".shp"
        print "shapeFile_filePath_saved: ", shapeFile_filePath_saved
        #success = MapWinGIS.ShapefileClass.SaveAs(reprojectedShapefile, shapeFile_filePath_saved, None)
        #print "success: ", success
        """
        
        if reprojectedShapefile == None:
            # reprojection failed
            utils = MapWinGIS.UtilsClass()
            convertErrorNo = MapWinGIS.GlobalSettingsClass().GdalLastErrorNo
            convertErrorMsg = MapWinGIS.GlobalSettingsClass().GdalLastErrorMsg
            convertErrorType = MapWinGIS.GlobalSettingsClass().GdalLastErrorType
            reprojectErrorMsg = MapWinGIS.GlobalSettingsClass().GdalReprojectionErrorMsg
            print "numOfsuccessfullyReprojectedShapes: ", numOfsuccessfullyReprojectedShapes
            print "convertErrorNo: ", convertErrorNo
            print "convertErrorMsg: ", convertErrorMsg
            print "convertErrorType: ", convertErrorType
            print "reprojectErrorMsg: ", reprojectErrorMsg
            print "utils.ErrorMsg: ", utils.ErrorMsg
            print "utils.LastErrorCode: ", utils.LastErrorCode
            
            reprojectionError = fixedShapefile.ErrorMsg(fixedShapefile.LastErrorCode)
            shpLinesFile_filePath = shpMultilinestringsFile_filePath = shpMultipolygonsFile_filePath = shpPointsFile_filePath = None
            validShapes = False
            printMsg = "The following error emerged while processing the data:\n" + \
                       " \n" + \
                       "\"%s\"\n" % reprojectionError + \
                       "numOfsuccessfullyReprojectedShapes: %s\n" % numOfsuccessfullyReprojectedShapes + \
                       " \n" + \
                       "Restart Rhino and Grasshopper (close them, then run again) and run this component again.\n" + \
                       "If this same message appears again open a new topic about it on: www.grasshopper3d.com/group/gismo/forum."
            
            return None, None, None, validShapes, printMsg
    
    
    originPtProjected_meters = gismo_gis.projectedLocationCoordinates(locationLatitudeD, locationLongitudeD)  # in meters!
    originPtProjected = Rhino.Geometry.Point3d(originPtProjected_meters.X/unitConversionFactor, originPtProjected_meters.Y/unitConversionFactor, originPtProjected_meters.Z/unitConversionFactor)  # in Rhino units
    
    # rotation due to north angle position
    #transformMatrixRotate = Rhino.Geometry.Transform.Rotation(-northRad, Rhino.Geometry.Vector3d(0,0,1), originPt)  # counter-clockwise
    transformMatrixRotate = Rhino.Geometry.Transform.Rotation(northRad, Rhino.Geometry.Vector3d(0,0,1), originPt)  # clockwise
    
    
    # open reprojectedShapefile
    
    # loop through shortenedName_keys (these are shapefile fields (":" is replaced with "_" and maximal size is 10 characters))
    shortenedName_keys = []
    for i in range(reprojectedShapefile.NumFields):
        field = reprojectedShapefile.Field(i)
        shortenedName_keys.append(field.Name)
    
    
    values = Grasshopper.DataTree[object]()
    shapes = Grasshopper.DataTree[object]()
    for i in range(reprojectedShapefile.NumShapes):
        shape = reprojectedShapefile.Shape[i]
        
        moveVector = originPt - originPtProjected
        
        if (shape.ShapeType == 0):  # NULL_SHAPE
            # ShapeType: NULL_SHAPE
            
            # values
            subValuesL = []
            for g in range(reprojectedShapefile.NumFields):
                value = reprojectedShapefile.CellValue(g,i)
                subValuesL.append(value)
            values.AddRange(subValuesL, Grasshopper.Kernel.Data.GH_Path(i))
            
            # pts
            ptsPerShape = [None]
            shapes.AddRange(ptsPerShape, Grasshopper.Kernel.Data.GH_Path(i))
        
        if (shape.ShapeType == 1):  # SHP_POINT
            # ShapeType: POINT
            
            # values
            subValuesL = []
            for g in range(reprojectedShapefile.NumFields):
                value = reprojectedShapefile.CellValue(g,i)
                if value == "yes": value = True  # for example: "building=yes"
                subValuesL.append(value)
            
            # pts
            ptsPerShape = []
            for k in range(shape.numPoints):
                pt = shape.Point[k]
                point3dProjected = Rhino.Geometry.Point3d(pt.x/unitConversionFactor, pt.y/unitConversionFactor, pt.z/unitConversionFactor)
                point3dMoved = point3dProjected + moveVector
                transformBoolSuccess = point3dMoved.Transform(transformMatrixRotate)
                ptsPerShape.append(point3dMoved)
            
            subValuesL_filtered, ptsPerShape_filtered = gismo_gis.filterShapes(shortenedName_keys, subValuesL, ptsPerShape, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove)
            
            values.AddRange(subValuesL_filtered, Grasshopper.Kernel.Data.GH_Path(i))
            shapes.AddRange(ptsPerShape_filtered, Grasshopper.Kernel.Data.GH_Path(i))
            del ptsPerShape
        
        if (shape.ShapeType == 3) or (shape.ShapeType == 5):  # POLYLINE and 
            # ShapeType: POLYLINE OR POLYGON
            
            for n in range(shape.NumParts):
                # values
                subValuesL = []
                for g in range(reprojectedShapefile.NumFields):
                    value = reprojectedShapefile.CellValue(g,i)
                    if value == "yes": value = True  # for example: "building=yes"
                    subValuesL.append(value)
                
                
                # points
                ptsPerPart = []
                subShape = shape.PartAsShape(n)
                for k in range(subShape.numPoints):
                    pt = subShape.Point[k]
                    point3dProjected = Rhino.Geometry.Point3d(pt.x/unitConversionFactor, pt.y/unitConversionFactor, pt.z/unitConversionFactor)  # in Rhino document units
                    point3dMoved = point3dProjected + moveVector
                    transformBoolSuccess = point3dMoved.Transform(transformMatrixRotate)
                    ptsPerPart.append(point3dMoved)
                polyline = Rhino.Geometry.Polyline(ptsPerPart)
                
                subValuesL_filtered, shapesL_filtered = gismo_gis.filterShapes(shortenedName_keys, subValuesL, [polyline], osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove)
                
                values.AddRange(subValuesL_filtered, Grasshopper.Kernel.Data.GH_Path(i,n))
                shapes.AddRange(shapesL_filtered, Grasshopper.Kernel.Data.GH_Path(i,n))
                del subValuesL
                del ptsPerPart
                del polyline
                del subValuesL_filtered
                del shapesL_filtered
            subShape = None
    
    shapefile.Close()  # naknadno dodat - proveriti da li pravi neke probleme
    fixedShapefile.Close()
    reprojectedShapefile.Close()
    
    
    if (shapes.DataCount == 0) and (onlyRemove_Ids_.DataCount == 0):
        # no data was added to the "shapes" list, AND nothing has been added to "onlyRemove_Ids_" input.
        # this may happen when there is literally no geometry generated inside the specific .shp file for the chosen "shapeType_" input (you have shapeType_ = 2 in a place where there are no points on openstreetmap.org)
        if shapeType_ == 0: shapeTypeLabel = "polygons"
        elif shapeType_ == 1: shapeTypeLabel = "polylines"
        elif shapeType_ == 2: shapeTypeLabel = "points"
        shortenedName_keys = values = shapes = None
        validShapes = False
        printMsg = "No %s geometry exist for that location/radius/shapeType.\n" % shapeTypeLabel + \
                   "Either change the \"_location\" input, or increase the \"radius_\" input, or change the \"shapeType_\" input."
        
        return shortenedName_keys, values, shapes, validShapes, printMsg
    
    elif (shapes.DataCount == 0) and (onlyRemove_Ids_.DataCount != 0):
        # this may happen if ids supplied to the "osm_id_Only_" and/or "osm_way_id_Only_" inputs of "OSM ids" component can not be found in this _location and/or radius_ (they may correspond to other _location and/or radius_)
        shortenedName_keys = values = shapes = None
        validShapes = False
        printMsg = "The ids you supplied through \"osm_id_Only_\" and/or \"osm_way_id_Only_\" inputs do not exist for this \"_location\" and/or \"radius_\" inputs.\nTry removing the ids from the \"osm_id_Only_\" and/or \"osm_way_id_Only_\" inputs of \"OSM ids\" component."
        
        return shortenedName_keys, values, shapes, validShapes, printMsg
    
    
    validShapes = True
    printMsg = "ok"
    
    return shortenedName_keys, values, shapes, validShapes, printMsg


def titleAndBaking(locationName, locationLatitudeD, locationLongitudeD, radiusM, northDeg, originPt, shapeType, shapeTypeLabel, shapes):
    
    # title
    titleLabelText = "OSM shapes for: %s\nLatitude: %s, Longitude: %s\nRadius: %sm, North: %s, GeometryType: %s" % (locationName, locationLatitudeD, locationLongitudeD, radiusM, northDeg, shapeTypeLabel)
    customTitle = None  # "legendBakePar_" input does not exist
    
    shapesFlattenedList = []
    ptcloud = Rhino.Geometry.PointCloud()  # use it for shapeType = 2 (because Point3d class does not contain the "GetBoundingBox" method)
    for subL in shapes.Branches:
        if len(subL) > 0:
            for shape in subL:
                if shapeType == 2:
                    # points (shapeType = 2)
                    ptcloud.Add(shape)
                else:
                    # polygons, polyline (shapeType = 0, 1)
                    curve = shape.ToNurbsCurve()
                    shapesFlattenedList.append(curve)
    
    if (shapeType == 2):
        titleLabelMesh, titleStartPt, titleTextSize = gismo_preparation.createTitle("mesh", [ptcloud], [titleLabelText])
    else:
        titleLabelMesh, titleStartPt, titleTextSize = gismo_preparation.createTitle("mesh", shapesFlattenedList, [titleLabelText])
    
    
    # hide titleOriginPt
    ghenv.Component.Params.Output[5].Hidden = True
    
    
    # baking
    if bakeIt_:
        layerName = locationName + "_" + str(locationLatitudeD) + "_" + str(locationLongitudeD) + "_RADIUS=" + str(radiusM) + "M" + "_NORTH=" + str(northDeg) + "_SHAPETYPE=" + str(shapeType)
        
        layParentName = "GISMO"; laySubName = "OSM"; layerCategoryName = "SHAPES"
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # green
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor) 
        
        if (shapeType == 2):
            geometryToBakeL = [ptcloud, originPt]
        else:
            geometryToBakeL = shapesFlattenedList + [originPt]
        geometryIds = gismo_preparation.bakeGeometry(geometryToBakeL, layerIndex)
        
        geometryToBakeL2 = [titleLabelMesh]
        geometryIds2 = gismo_preparation.bakeGeometry(geometryToBakeL2, layerIndex)
        
        # grouping
        groupIndex = gismo_preparation.groupGeometry("OSM_SHAPES" + "_" + layerName + "_shapesOnly", geometryIds)
        groupIndex2 = gismo_preparation.groupGeometry("OSM_SHAPES" + "_" + layerName + "_shapesAndTitleOrigin_", geometryIds2)
    
    
    # deleting
    del shapes; del ptcloud; del shapesFlattenedList
    
    return titleLabelMesh, titleStartPt


def printOutput(locationName, locationLatitudeD, locationLongitudeD, radiusM, northDeg, originPt, requiredKeys, shapeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "OSM shapes component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Location (deg.): %s
Latitude (deg.): %s
Longitude (deg.): %s
North (deg.): %s

Radius (m): %s
Origin: %s
Shape type: %s
Required keys: %s
Only remove Ids: %s, %s, %s, %s
    """ % (locationName, locationLatitudeD, locationLongitudeD, northDeg, radiusM, originPt, shapeType, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_mainComponent = sc.sticky["gismo_mainComponent"]()
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_geometry = sc.sticky["gismo_CreateGeometry"]()
        gismo_gis = sc.sticky["gismo_GIS"]()
        
        locationName, locationLatitudeD, locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_preparation.checkLocationData(_location)
        if validLocationData:
            fileNameIncomplete = locationName + "_" + str(locationLatitudeD) + "_" + str(locationLongitudeD)  # incomplete due to missing "_radius=100KM" part
            radiusM, northRad, northDeg, originPt, shapeType, shapeTypeLabel, requiredKeys, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, iteropMapWinGIS_dll_folderPath, unitConversionFactor, validInputData, printMsg = checkInputData(radius_, north_, origin_, shapeType_, requiredKeys_, onlyRemove_Ids_)
            if validInputData:
                if _runIt:
                    shapeFile_filePath, fullName_keys, valid_osm_or_shp_files, printMsg = checkOsmShpFiles(locationLatitudeD, locationLongitudeD, fileNameIncomplete, radiusM, requiredKeys, shapeType)
                    if valid_osm_or_shp_files:
                        shortenedName_keys, values, shapes, validShapes, printMsg = createShapesKeysValues(locationName, locationLatitudeD, locationLongitudeD, shapeFile_filePath, northRad, originPt, shapeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor)
                        #keys = shortenedName_keys
                        keys = fullName_keys
                        if validShapes:
                            validShapefiles, printMsg = gismo_gis.checkIfShapefilesAreValid(keys, values)
                            if validShapefiles:
                                title, titleOriginPt = titleAndBaking(locationName, locationLatitudeD, locationLongitudeD, radiusM, northDeg, originPt, shapeType, shapeTypeLabel, shapes)
                                printOutput(locationName, locationLatitudeD, locationLongitudeD, radiusM, northDeg, originPt, requiredKeys, shapeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove)
                                gc.collect()
                            else:
                                print printMsg
                                ghenv.Component.AddRuntimeMessage(level, printMsg)
                        else:
                            print printMsg
                            ghenv.Component.AddRuntimeMessage(level, printMsg)
                    else:
                        print printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
                else:
                    print "All inputs are ok. Please set \"_runIt\" to True, in order to run the OSM Shapes component"
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
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
