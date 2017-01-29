# OSM 3D
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2017, Djordje Spasic <djordjedspasic@gmail.com>
# with assistance of Vladimir Elistratov and his Blender OSM project <https://github.com/vvoovv/blender-osm>
# Component icon based on free OSM icon from: <https://icons8.com/web-app/13398/osm> and <http://www.freeiconspng.com/free-images/3d-icon-9783>
#
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to create 3d geometry of structures/building and tree shapes created with Gismo "OSM shapes" component.
Creation of 3d shapes can be done in three ways:
1) If there is a valid value (not equal to "") for the "height" key, then the shape will always be extruded according to this value.
2) If this value is lacking (equal to ""), then the shape can be extruded according to the "building:levels" key value.
3) If both of these two values are lacking (equal to ""), or the very keys are lacking, and there is a valid value ("True") for the "building" key, then the shape will be extruded, according to the supplied domain generated from the randomHeightRange_ input.
If neither of these three ways are fulfilled, then no creation of 3d shapes will be performed.
-
Provided by Gismo 0.0.1
    
    input:
        _shapes: Plug in the shapes from the Gismo OSM shapes "shapes" output
        _keys: Plug in the keys from the Gismo OSM shapes "keys" output.
        _values: Plug in the values from the Gismo OSM shapes "values" output.
        onlyRemove_Ids_: Use this input to define lists of Open Street Map ids. "OSM ids" component will generate them.
                         These lists can be used to define:
                         1) only those ids which will be included (isolated) when "OSM 3D" component is ran (use "osm_id_Only" and "osm_way_id_Only" inputs for this).
                         2) ids which will be removed when "OSM 3D" component is ran (use "osm_id_Remove" and "osm_way_id_Remove" inputs for this).
                         3) you can combine 1) and 2) and both define the: included and removed ids.
                         -
                         If nothing supplied to this input, then no OSM ids will be isolated nor removed: meaning all of them will be included.
        heightPerLevel_: Some supplied "_shapes" may contain "building_l" keys. This can be used to extrude those buildings, by supplying the height value of each level (above ground) in Rhino document units (meters, feets...).
                         -
                         If nothing supplied, the default value of 3 meters (9.84 feets) per level will be used.
                         -
                         In Rhino document units (meters, feets...).
        randomHeightRange_: This output can be useful if supplied "_shapes" do not contain valid values for "height" and "building_l" keys.
                            If they still contain the "building" key with value "True", then this can be used to extrude the shapes, by using some random extrude domain.
                            So to randomly extrude "buildings" shapes, just supply the "Construct Domain" to the randomHeightRange_ input. For example, input the "Construct Domain" component by using "20" and "30" as its starting and ending domain values. This will randomly extrude all buildings by 20 to 30 meters height. Of course in case the Rhino document units is: meters. It can be any other unit.
                            -
                            If nothing supplied, no random extrusion of the shapes will be applied.
                            -
                            Domain in Rhino document units (meters, feets...).
        treeType_: There are three tree geometric types:
                   0 - round
                   1 - polygonized
                   2 - random shaped
                   -
                   If nothing supplied, the default type 2 type (random) will be used.
                   -
                   Integer.
        groundTerrain_: The ground terrain on which the "threeDeeShapes" will be layed onto.
                        Supply it by using "terrain" output of the Ladybug "Terrain Generator" or Gismo "Terrain Generator" components.
                        -
                        If nothing supplied, the "threeDeeShapes" will always be layed flat onto a horizontal plane, with plane origin being the "origin" input of the "OSM shapes" component.
        bakeIt_: Set to "True" to bake the extruded _shape geometry into the Rhino scene.
                 The geometry will be grouped. To ungroup it, select it and call the "Ungroup" Rhino command.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        threeDeeValues: Generated 3d shapes from the inputted "_shapes".
                        -
                        Those can be extruded buildings, or trees.
                        -
                        If 3d shape has not been created then that branch will be empty.
                        Use "Clean Tree" component and set the "E" input to "True" to remove all these empty branches.
        threeDeeKeys: A list of keys. This output is the same as "keys" output of "OSM shapes" component.
        threeDeeValues: Values corresponding to each shape in "threeDeeValues" output.
                        -
                        If 3d shape has not been created then that branch will not have any values (it will be empty).
                        Use "Clean Tree" component and set the "E" input to "True" to remove all these empty branches.
        height: The height of each shape from the "threeDeeShapes" output.
                -
                In Rhino document units (meters, feets...).
"""

ghenv.Component.Name = "Gismo_OSM 3D"
ghenv.Component.NickName = "OSM3D"
ghenv.Component.Message = "VER 0.0.1\nJAN_29_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.1\nJAN_29_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import scriptcontext as sc
import Grasshopper
import System
import random
import Rhino
import math
import time
import gc


def checkInputData(shapes, keys, values, heightPerLevel, randomHeightRange, treeType, onlyRemove_Ids):
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    
    # check inputs
    if (shapes.DataCount == 0):
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "Please connect the \"shapes\" output from Gismo \"OSM shapes\" component to this component's \"_shapes\" input."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    elif (len(shapes.Branches) == 1) and (shapes.Branches[0][0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_shapes\" input.\n" + \
                   " \n" + \
                   "Please connect the \"shapes\" output from Gismo \"OSM shapes\" component to this component's \"_shapes\" input.\n" + \
                   "And make sure that you set the \"OSM shapes\" \"_runIt\" input to \"True\"."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    
    if (len(keys) == 0):
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "Please connect the \"keys\" output from Gismo \"OSM shapes\" component to this component's \"_keys\" input."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    elif (len(keys) == 1) and (keys[0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_keys\" input.\n" + \
                   " \n" + \
                   "Please connect the \"keys\" output from Gismo \"OSM shapes\" component to this component's \"_keys\" input.\n" + \
                   "And make sure that you set the \"OSM shapes\" \"_runIt\" input to \"True\"."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    
    if (values.DataCount == 0):
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "Please connect the \"values\" output from Gismo \"OSM shapes\" component to this component's \"_values\" input."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    elif (len(values.Branches) == 1) and (values.Branches[0][0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_values\" input.\n" + \
                   " \n" + \
                   "Please connect the \"values\" output from Gismo \"OSM shapes\" component to this component's \"_values\" input.\n" + \
                   "And make sure that you set the \"OSM shapes\" \"_runIt\" input to \"True\"."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    
    if len(shapes.Paths) != len(values.Paths):
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "The number of tree branches inputted to the \"_shapes\" and \"_values\" inputs do not match.\n" + \
                   " \n" + \
                   "Make sure that you connected:\n" + \
                   "\"keys\" output from Gismo \"OSM shapes\" component to this component's \"_keys\" input. And:\n" + \
                   "\"values\" output from Gismo \"OSM shapes\" component to this component's \"_values\" input."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    
    # heightPerLevel_ is always in Rhino document units
    if (heightPerLevel == None):
        heightPerLevel = 3/unitConversionFactor  # 3 meters (10 feet)
    elif (heightPerLevel <= 0):
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "heightPerLevel_ input must be larger than 0.\n" + \
                   "Please supply a value larger than 0."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    
    # randomHeightRange_ is always in Rhino document units
    if (randomHeightRange == None):
        randomHeightRangeStart = randomHeightRangeEnd = None  # dummy values, will not be used
    else:
        # randomHeightRangeStart can be larger than randomHeightRangeEnd, the random.uniform will still generate a random value between those two numbers.
        # randomHeightRangeStart == randomHeightRangeEnd, the a single value will always be generated (equal to randomHeightRangeStart and randomHeightRangeEnd)
        randomHeightRangeStart = randomHeightRange.T0
        randomHeightRangeEnd = randomHeightRange.T1
    
    
    if (treeType == None):
        treeType = 2  # default (random)
    elif (treeType < 0) or (treeType > 2):
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "treeType_ input must can only have one of the following values:\n" + \
                   "0 - round tree\n" + \
                   "1 - polygonized tree\n" + \
                   "2 - random shaped tree\n" + \
                   " \n" + \
                   "Please supply one of these values."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    
    if (onlyRemove_Ids.BranchCount == 1) and (onlyRemove_Ids.Branches[0][0] == None):
        # in "OSM ids" component, an id exists both in "osm_id_Only_" and "osm_id_Remove_" inputs,  or an id exists both in "osm_way_id_Only_" and "osm_way_id_Remove_" inputs
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "Your \"_onlyRemove_Ids\" input is invalid. Check the \"readMe!\" output of \"OSM ids\" component to see what's wrong with it."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
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
    
    
    # check the "shapeType_" input value set in the "OSM shapes" component. This value will always exist, as "OSM shapes" component will be ran before the "OSM 3d" component
    shapeType = sc.sticky["OSMshapes_shapeType"]
    if shapeType == 1:
        heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = None
        validInputData = False
        printMsg = "This component supports only creation of 3d buildings and trees. So \"shapeType_\" input of \"OSM shapes\" component needs to be set to either 0 or 2."
        return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg
    
    
    del shapes; del keys; del values  # delete local variables
    validInputData = True
    printMsg = "ok"
    
    return heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg


def isNumber(string):
    """
    check if a string can be converted to a number
    """
    try:
        number = float(string)
        return True
    except:
        return False


def createThreeDeeShapes(shapesDataTree, keys, valuesDataTree, heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, groundTerrain, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor):
    
    # check the "shapeType_" input value set in the "OSM shapes" component. This value will always exist, as "OSM shapes" component will be ran before the "OSM 3d" component
    shapeType = sc.sticky["OSMshapes_shapeType"]
    
    # use the Z coordinate of the origin_ input from "OSM shapes"
    OSMshapesComp_origin = sc.sticky["gismo_OSMshapesComp_origin"]
    
    
    # a) filter all "building" shapes to a single list, to be used for comparison of centroids. This is used so that all shapes with valid "building:part" key within a shape with valid "building" tag will be level to that shape, in case groundTerrain_ is inputted.
    # b) check if shapes with valid "building" tags contain the shapes with valid "building:part" and "height" tags. In that case if "randomHeightRange_" is inputted, the shape with "building" tag will not be extruded.
    building_keyIndex = None
    buildingPart_keyIndex = None
    height_keyIndex = None
    osm_id_keyIndex = None
    osm_way_id_keyIndex = None
    for keyIndex,key in enumerate(keys):
        if (key == "building"):
            building_keyIndex = keyIndex
        elif (key == "building:part"):  # "building_p"
            buildingPart_keyIndex = keyIndex
        elif (key == "height"):
            height_keyIndex = keyIndex
        elif (key == "osm_id"):
            osm_id_keyIndex = keyIndex
        elif (key == "osm_way_id"):
            osm_way_id_keyIndex = keyIndex
    
    buildingShapes = []
    buildingShapes_with_BuildingPartsAndHeight_insideL2 = []
    valueBuilding = ""  # dummy value in case "building" key does not exist
    valueBuildingPart = ""  # dummy value in case "building:part" key does not exist
    valueHeight = ""  # dummy value in case "height" key does not exist
    valueHeight2 = ""  # dummy value in case "height" key does not exist
    value_osm_id = ""  # initial "osm_id" key value
    value_osm_way_id = ""  # dummy value in case "osm_way_id" key does not exist
    if (building_keyIndex != None) and (shapeType == 0):  # "(shapeType == 0)" because a node can also be tagged as: "building=yes"
        
        shapesLL = shapesDataTree.Branches
        valuesLL = valuesDataTree.Branches
        paths = shapesDataTree.Paths  # obrisati ovaj red
        shapePlane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,OSMshapesComp_origin.Z), Rhino.Geometry.Vector3d(0,0,1))  # it will always be constant because each shapesL has a constant height (coming from "OSM shapes" component)
        tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        for branchIndex,shapesL in enumerate(shapesLL):
            if len(shapesL) != 0:  # some shape may have been removed with the "OSM ids" component
                valueBuilding = valuesLL[branchIndex][building_keyIndex]  # for a)
                if (height_keyIndex != None):
                    valueHeight = valuesLL[branchIndex][height_keyIndex]
                else:
                    valueHeight = None  # the "height" key does not exist in "keys"
                    value_osm_id = valuesLL[branchIndex][osm_id_keyIndex]
                if (osm_way_id_keyIndex != None):
                    value_osm_way_id = valuesLL[branchIndex][osm_way_id_keyIndex]
                else:
                    value_osm_way_id = None  # the "osm_way_id" key does not exist in "keys"
                if (valueBuilding != ""):
                    buildingShapes.append(shapesL[0])  # "shapes" output from "OSM shapes" component will always have one item per branch
                    
                    # for b)
                    if (valueHeight == ""):  # there is a shapesL[0] with a valid "building" value but invalid "height" value (it does not have a value for "height" key)
                        shapesLArea = Rhino.Geometry.AreaMassProperties.Compute(shapesL[0]).Area
                        innerShapesTotalArea = 0
                        for branchIndex2,shapesL2 in enumerate(shapesLL):  # for b)
                            if len(shapesL2) != 0:  # some shape may have been removed with the "OSM ids" component
                               if (buildingPart_keyIndex != None) and (height_keyIndex != None):# OVAJ RED JE SKORO DODAT. proveriti da li pravi probleme
                                    valueBuildingPart = valuesLL[branchIndex2][buildingPart_keyIndex]
                                    valueHeight2 = valuesLL[branchIndex2][height_keyIndex]
                                    if (valueBuildingPart != "") and (valueHeight2 != ""):  # there is AT LEAST ONE shapesL2[0] with a valid "building:part" and "height" values
                                        shapeCentroid = Rhino.Geometry.AreaMassProperties.Compute(shapesL2[0]).Centroid
                                        pointContainment = shapesL[0].Contains(shapeCentroid, shapePlane, tol)
                                        if (pointContainment == Rhino.Geometry.PointContainment.Inside):# or (pointContainment == Rhino.Geometry.PointContainment.Coincident):
                                            shapesL2Area = Rhino.Geometry.AreaMassProperties.Compute(shapesL2[0]).Area
                                            innerShapesTotalArea += shapesL2Area
                        
                        if innerShapesTotalArea >= shapesLArea:
                            # shapesL[0] containsts other shapesL2[0]'s which fill up (cover) the complete shapesL[0] area. In that case do not extrude the shapesL[0]
                            if (value_osm_id != ""):
                                #print "value_osm_id: ", value_osm_id
                                osm_id_Remove.append(value_osm_id)
                            elif (value_osm_way_id != ""):
                                #print "value_osm_way_id: ", value_osm_way_id
                                osm_way_id_Remove.append(value_osm_way_id)
                    
                    else:
                        # shapesL[0] does contain a valid "building" value but not a valid "height" value
                        #buildingShapes_with_BuildingPartsAndHeight_insideL[branchIndex].append(False)
                        pass
                else:
                    # shapesL[0] does not contain a valid "building" value
                    #buildingShapes_with_BuildingPartsAndHeight_insideL[branchIndex].append(False)
                    pass
        
        del shapesLL
        del valuesLL
    
    
    # get groundBrep_singleBrepFace
    if (groundTerrain != None):
        groundBrep_singleBrepFace = groundTerrain.Faces[0].DuplicateFace(False)  # always use the top face (the actual terrain) in case inputted groundTerrain_ has been created as a polysurface
        accurate = False
        bb_volume, bb_centroid, bb_length, bb_depth, bb_height, bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner = gismo_preparation.boundingBox_properties([groundTerrain], accurate)
    elif (groundTerrain == None):
        groundBrep_singleBrepFace = None
        bb_height = 10  # dummy value
    
    
    
    
    if (shapeType == 0):
        # shift the paths in "shapes" and "values" data trees by -1, to extrude buildings
        shapes_shiftedPaths_DataTree = gismo_preparation.datatree_shiftPaths(shapesDataTree)
        values_shiftedPaths_DataTree = gismo_preparation.datatree_shiftPaths(valuesDataTree)
    elif (shapeType != 0):
        # no shifting of paths should be done in case the trees need to be created
        shapes_shiftedPaths_DataTree = shapesDataTree
        values_shiftedPaths_DataTree = valuesDataTree
    
    shapes_shiftedPaths_Paths = shapes_shiftedPaths_DataTree.Paths
    shapes_shiftedPaths_LL = shapes_shiftedPaths_DataTree.Branches
    values_shiftedPaths_LL = values_shiftedPaths_DataTree.Branches
    
    threeDeeShapesDataTree = Grasshopper.DataTree[object]()
    threeDeeValuesDataTree = Grasshopper.DataTree[object]()
    heightDataTree = Grasshopper.DataTree[object]()
    
    projectionDirection = Rhino.Geometry.Vector3d(0,0,1)  # it can be direction = Rhino.Geometry.Vector3d(0,0,-1) as well, does not matter
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    atleastOneThreeDeeShapeCanBeCreated = False  # initial value
    for branchIndex,shapesL in enumerate(shapes_shiftedPaths_LL):
        if len(shapesL) == 0:
            # some shape may have been removed with the "OSM ids" component
            height = 0
            threeDeeShapeL = []
            threeDeeValueL = []
        else:
            subValuesL_filtered, shapesL_filtered = gismo_osm.filterShapes(keys, values_shiftedPaths_LL[branchIndex], "shapesL dummy string", osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove)
            if (len(subValuesL_filtered) == 0) and (len(shapesL_filtered) == 0):
                # the id supplied to the "osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove" is found
                height = 0
                threeDeeShapeL = []
                threeDeeValueL = []
            elif (len(subValuesL_filtered) != 0) and (len(shapesL_filtered) != 0):
                # the id supplied to the "osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove" is NOT found
                valueBuilding = ""  # dummy value in case "building" key does not exist
                valueHeight = ""  # dummy value in case "height" key does not exist
                valueMinHeight = ""  # dummy value in case "height" key does not exist
                valueLevel = ""  # dummy value in case "building_l" key does not exist
                valueLeafType = ""  # dummy value in case "leaf_type" key does not exist
                valueCycleType = ""  # dummy value in case "leaf_cycle" key does not exist
                valueNatural = ""  # dummy value in case "natural" key does not exist
                valueDiameterCrown = ""  # dummy value in case "diameter_c" key does not exist
                deciduousOrConiferous = ""  # dummy value in case "leaf_type", "leaf_cycle", "natural" keys do not exist
                for keyIndex,key in enumerate(keys):
                    if (key == "building"):
                        valueBuilding = values_shiftedPaths_LL[branchIndex][keyIndex]
                    elif (key == "height"):
                        valueHeight = values_shiftedPaths_LL[branchIndex][keyIndex]
                    elif (key == "building:levels"):  # the short name is: building_l
                        valueLevel = values_shiftedPaths_LL[branchIndex][keyIndex]
                    
                    elif (key == "leaf_type"):
                        valueLeafType = values_shiftedPaths_LL[branchIndex][keyIndex]
                    elif (key == "leaf_cycle"):
                        valueCycleType = values_shiftedPaths_LL[branchIndex][keyIndex]
                    elif (key == "natural"):
                        valueNatural = values_shiftedPaths_LL[branchIndex][keyIndex]
                    elif (key == "diameter_crown"):  # the short name is: diameter_c
                        valueDiameterCrown = values_shiftedPaths_LL[branchIndex][keyIndex]
                    
                    if (key == "min_height"):
                        valueMinHeight = values_shiftedPaths_LL[branchIndex][keyIndex]
                
                # find the "height" for both extruding buildings and trees
                if isNumber(valueHeight):
                    # there is "height" key, and it's value is not ""
                    height = float(valueHeight)/unitConversionFactor  # in Rhino document units
                    threeDeeShapesObject = "3d building"
                elif isNumber(valueLevel):
                    # there is "building_l" key, and it's value is not ""
                    height = float(valueLevel) * heightPerLevel  # in Rhino document units
                    threeDeeShapesObject = "3d building"
                elif (valueBuilding != "")  and  (not isNumber(valueHeight) and (not isNumber(valueLevel))):
                    # a) there are "height" key and "building_l" keys and both have "" values. And there is "building" key, and it's valid (it's not equal to "". So it's either True or some other value, like: "residential", "house", "industrial"...) or
                    # b) there are NO "height" and "building_l" keys. And there is "building" key, and it's valid (it's not equal to "". So it's either True or some other value, like: "residential", "house", "industrial"...)
                    if (randomHeightRange != None):
                        # domain supplied into the "randomHeightRange_" input
                        height = round(random.uniform(randomHeightRangeStart, randomHeightRangeEnd),2)  # in Rhino document units
                        threeDeeShapesObject = "3d building"
                    else:
                        # nothing inputted to the "randomHeightRange_" input
                        height = 0
                        threeDeeShapesObject = None
                        atleastOneThreeDeeShapeCanBeCreated = True
                else:
                    # there are "height", "building:l", "building" keys but they are all invalid ("", "", "")
                    # there are NO "height", "building_l", "building" keys
                    height = 0
                    threeDeeShapesObject = None
                
                if isNumber(valueMinHeight):
                    valueMinHeight = float(valueMinHeight)
                
                
                
                if (shapeType == 2):
                    # identify whether a 3d tree will be created
                    if (valueLeafType == "broadleaved"):
                        deciduousOrConiferous = "deciduous"
                        threeDeeShapesObject = "3d tree"
                    elif (valueLeafType == "needleleaved"):
                        deciduousOrConiferous = "coniferous"
                        threeDeeShapesObject = "3d tree"
                    elif (valueCycleType == "deciduous") or (valueCycleType == "semi_deciduous"):
                        deciduousOrConiferous = "deciduous"
                        threeDeeShapesObject = "3d tree"
                    elif (valueCycleType == "evergreen") or (valueCycleType == "semi_evergreen"):
                        deciduousOrConiferous = "coniferous"
                        threeDeeShapesObject = "3d tree"
                    elif (valueNatural == "tree"):
                        deciduousOrConiferous = "deciduous"  # always use "deciduous" if not specified which "deciduousOrConiferous" the tree is
                        threeDeeShapesObject = "3d tree"
                    elif (valueDiameterCrown != ""):
                        deciduousOrConiferous = "deciduous"  # always use "deciduous" if not specified which "deciduousOrConiferous" the tree is
                        threeDeeShapesObject = "3d tree"
                    else:
                        threeDeeShapesObject = None
                
                
                
                # 1) try creating 3d trees
                if (threeDeeShapesObject == "3d tree"):
                    if (height == 0):
                        # this happens if the value for the "height" key was: "", or there the "height" key does not even exist
                        if (randomHeightRange != None):
                            # domain supplied into the "randomHeightRange_" input
                            height = round(random.uniform(randomHeightRangeStart, randomHeightRangeEnd),2)  # in Rhino document units
                        else:
                            # nothing inputted to the "randomHeightRange_" input
                            height = 0
                            atleastOneThreeDeeShapeCanBeCreated = True
                    
                    if (height != 0):
                        # there is "height" key, and its value is valid (not "")
                        #atleastOneThreeDeeShapeCanBeCreated = True  # proveriti da li pravi problem
                        threeDeeShapeL = []
                        threeDeeValueL = values_shiftedPaths_LL[branchIndex]
                        
                        if deciduousOrConiferous == "":
                            deciduousOrConiferous = "deciduous"  # by default, if it can not be identified if a tree is deciduous or coniferous always use the deciduous
                            #deciduousOrConiferous = "coniferous"
                        
                        numOfTreeHorizontalSegments = 6  # this value is fixed, and should not be changed
                        
                        # heights and radii
                        trunkRadius = height/random.uniform(44, 48)  # lower values (than 44,48) can result in "bottomCrown_brep" not being able to be created
                        if isNumber(valueDiameterCrown):
                            # there is a valid "valueDiameterCrown" value
                            crownRadius = valueDiameterCrown
                        else: 
                            # valueDiameterCrown == ""
                            crownRadius = height/random.uniform(2, 5)
                        
                        trunkHeight = 0.2*height
                        crownHeight = height - trunkHeight
                        
                        treeBottom_pt = shapesL[0].Location  # convert Point to Point3d
                        unprojectedTrunkBottom_crv = Rhino.Geometry.Circle(treeBottom_pt, trunkRadius).ToNurbsCurve()
                        
                        # project the shapes (points) to the groundTerrain_
                        if (groundTerrain == None):
                            projectedTreeBottom_pt = treeBottom_pt
                            projectedTrunkBottom_crv = unprojectedTrunkBottom_crv
                            
                            extrusionVector = Rhino.Geometry.Vector3d(0, 0, trunkHeight)
                            trunkBrep = Rhino.Geometry.Surface.CreateExtrusion(projectedTrunkBottom_crv, extrusionVector).ToBrep()
                            trunkTop_pt = Rhino.Geometry.Point3d(projectedTreeBottom_pt.X, projectedTreeBottom_pt.Y, projectedTreeBottom_pt.Z + trunkHeight)
                            trunkTop_crv = Rhino.Geometry.Circle(trunkTop_pt, trunkRadius).ToNurbsCurve()
                        elif (groundTerrain != None):
                            projectedTreeBottom_pts = Rhino.Geometry.Intersect.Intersection.ProjectPointsToBreps([groundTerrain], [treeBottom_pt], projectionDirection, tol)
                            if len(projectedTreeBottom_pts) == 0:
                                # the shapeL[0] point is located outside of terrainGround_ input boundaries
                                # add "None" to the threeDeeShapesDataTree
                                height = 0
                                threeDeeShapeL = []
                                threeDeeValueL = []
                                threeDeeShapesDataTree.AddRange(threeDeeShapeL, shapes_shiftedPaths_Paths[branchIndex])
                                threeDeeValuesDataTree.AddRange(threeDeeValueL, shapes_shiftedPaths_Paths[branchIndex])
                                heightDataTree.AddRange([height], shapes_shiftedPaths_Paths[branchIndex])
                                continue
                            else:
                                projectedTreeBottom_pt = projectedTreeBottom_pts[0]
                                projectedTrunkBottom_crv1 = Rhino.Geometry.Curve.ProjectToBrep(unprojectedTrunkBottom_crv, groundTerrain, projectionDirection, tol)[0]
                                if (not projectedTrunkBottom_crv1.IsClosed):
                                    # the projected shape is not a closed curve anymore (it was before the projection)
                                    line = Rhino.Geometry.Line(projectedTrunkBottom_crv1.PointAtStart, projectedTrunkBottom_crv1.PointAtEnd).ToNurbsCurve()
                                    joinedPolyCrv = Rhino.Geometry.Curve.JoinCurves([projectedTrunkBottom_crv1,line], tol)[0]
                                    projectedTrunkBottom_crv = joinedPolyCrv.ToNurbsCurve()
                                else:
                                    # the projected curve is still a closed curve (and it was before the projection)
                                    projectedTrunkBottom_crv = projectedTrunkBottom_crv1
                                
                                # a) trunk
                                trunkTop_pt = Rhino.Geometry.Point3d(projectedTreeBottom_pt.X, projectedTreeBottom_pt.Y, projectedTreeBottom_pt.Z + trunkHeight)
                                trunkTop_crv = Rhino.Geometry.Circle(trunkTop_pt, trunkRadius).ToNurbsCurve()
                                extrudePathCurve = Rhino.Geometry.Line(trunkTop_pt, Rhino.Geometry.Point3d(trunkTop_pt.X, trunkTop_pt.Y, trunkTop_pt.Z - bb_height)).ToNurbsCurve()
                                extrusionVector = Rhino.Geometry.Vector3d(0, 0, -bb_height)
                                extrudedShapeBrep = Rhino.Geometry.Surface.CreateExtrusion(trunkTop_crv, extrusionVector).ToBrep()
                                splittedBreps = Rhino.Geometry.Brep.Split(extrudedShapeBrep, groundBrep_singleBrepFace, tol)
                                trunkBrep = splittedBreps[0]
                                del splittedBreps
                        
                        # b) crown
                        # crown curves/polylines
                        crownSection_crvs = []
                        
                        if deciduousOrConiferous == "deciduous":
                            crownRadii = [0.15*crownRadius, crownRadius, crownRadius, crownRadius, 0.15*crownRadius]  # [crownBottom_crv radius, crownMiddle1_crv, crownMiddle2_crv, crownTop_crv]
                            crownPartitionHeights = [0*crownHeight, 0.275*crownHeight, 0.5*crownHeight, 0.725*crownHeight, 1.0*crownHeight]
                        elif deciduousOrConiferous == "coniferous":
                            crownRadii = [0.2*crownRadius, crownRadius, 0.1*crownRadius]  # [crownBottom_crv radius, crownMiddle1_crv, crownMiddle2_crv, crownTop_crv]
                            crownPartitionHeights = [0*crownHeight, 0.05*crownHeight, 1.0*crownHeight]
                        
                        for i in xrange(len(crownRadii)):
                            crown_pt = Rhino.Geometry.Point3d(trunkTop_pt.X, trunkTop_pt.Y, trunkTop_pt.Z + crownPartitionHeights[i])
                            circleCrv = Rhino.Geometry.Circle(crown_pt, crownRadii[i]).ToNurbsCurve()
                            if (treeType == 0):
                                crownSection_crvs.append(circleCrv)
                            elif (treeType == 1):
                                includeEnds = True
                                circleDivision_tL = list(Rhino.Geometry.Curve.DivideByCount(circleCrv, numOfTreeHorizontalSegments, includeEnds))
                                circleDivision_tL = circleDivision_tL + [circleDivision_tL[0]]  # closing the polyline
                                circleDivision_ptsL = [circleCrv.PointAt(t) for t in circleDivision_tL]
                                crown_polyline = Rhino.Geometry.Polyline(circleDivision_ptsL).ToNurbsCurve()
                                crownSection_crvs.append(crown_polyline)
                            elif (treeType == 2):
                                centroid = Rhino.Geometry.AreaMassProperties.Compute(circleCrv).Centroid
                                includeEnds = True
                                t_L = circleCrv.DivideByCount(12, includeEnds)
                                randomCirclePts = []
                                for t in t_L:
                                    pt = circleCrv.PointAt(t)
                                    vector = pt - centroid
                                    vectorScaleFactor = random.uniform(-0.2, 0.2)
                                    randomPt = pt + vector*vectorScaleFactor
                                    randomCirclePts.append(randomPt)
                                    degree = 3; knotstyle = 3; knotstyle2 = System.Enum.ToObject(Rhino.Geometry.CurveKnotStyle, 3); start_tangent = end_tangent = Rhino.Geometry.Vector3d.Unset
                                randomCirclePts2 = randomCirclePts + [randomCirclePts[0]]  # close the crv
                                randomCrv = Rhino.Geometry.Curve.CreateInterpolatedCurve(randomCirclePts2, degree, knotstyle2, start_tangent, end_tangent)
                                crownSection_crvs.append(randomCrv)
                        
                        # crow brep
                        bottomCrown_brep = Rhino.Geometry.Brep.CreatePlanarBreps([crownSection_crvs[0],trunkTop_crv])[0]
                        topCrown_brep = Rhino.Geometry.Brep.CreatePlanarBreps(crownSection_crvs[-1])[0]
                        if (treeType == 0):
                            loftType2 = Rhino.Geometry.LoftType.Normal
                        elif (treeType == 1):
                            loftType2 = Rhino.Geometry.LoftType.Straight
                        elif (treeType == 2):
                            loftType2 = Rhino.Geometry.LoftType.Normal
                        closed = False
                        crownSideBrep = Rhino.Geometry.Brep.CreateFromLoft(crownSection_crvs, Rhino.Geometry.Point3d.Unset, Rhino.Geometry.Point3d.Unset, loftType2, closed)[0]
                        treeJoinedBrep = Rhino.Geometry.Brep.JoinBreps([bottomCrown_brep, crownSideBrep, topCrown_brep, trunkBrep], tol)[0]
                        treeJoinedBrep.Flip()  # for some reason the "treeJoinedBrep" has always normals pointed downwards
                        threeDeeShapeL.append(treeJoinedBrep)
                
                
                
                # 2) try creating 3d buildings
                elif (threeDeeShapesObject == "3d building"):
                    # check if a building can be created (if height != 0)
                    if (height != 0):
                        
                        bottomCrvControlPt_highestZcoord = None  # check if commenting-out this line will make some errors
                        # find out whether shapesL is included in other building shapes (like shapesL which have valid "building:part" key). If it is, then calculate the "bottomCrvControlPt_highestZcoord" of that other building shape
                        shapePlane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,shapesL[0].PointAtStart.Z), Rhino.Geometry.Vector3d(0,0,1))  # it will always be constant because each shapesL has a constant height (coming from "OSM shapes" component)
                        for buildingShape in buildingShapes:
                            shapeCentroid = Rhino.Geometry.AreaMassProperties.Compute(shapesL[0]).Centroid
                            pointContainment = buildingShape.Contains(shapeCentroid, shapePlane, tol)
                            if (pointContainment == Rhino.Geometry.PointContainment.Inside) or (pointContainment == Rhino.Geometry.PointContainment.Coincident):
                                # shapesL[0]'s centroid is contained inside another shapesL[0] (which has a valid "building" key), so use the "bottomCrvControlPt_highestZcoord" of that another shapesL[0]
                                dummy_topCrvs, bottomCrvControlPt_highestZcoord = gismo_createGeometry.liftingOSMshapes_from_groundTerrain([buildingShape], groundBrep_singleBrepFace, height, valueMinHeight)  # "bottomCrvControlPt_highestZcoord" calculated
                                del dummy_topCrvs
                                break  # the shapesL[0] has found to be inside another shapesL[0] which has a valid "building" key. No need for checking of other shapes
                        
                        topCrvs, dummy_bottomCrvControlPt_highestZcoord = gismo_createGeometry.liftingOSMshapes_from_groundTerrain(shapesL, groundBrep_singleBrepFace, height, valueMinHeight, bottomCrvControlPt_highestZcoord)
                        if (len(topCrvs) == 0):
                            # the shapesL is located outside of the "groundTerrain_" ("if groundTerrain_" inputted. If "groundTerrain_" not inputted, len(projectedShapeCrvs) will never be equal to 0)
                            height = 0
                            threeDeeShapeL = []
                            threeDeeValueL = []
                        elif (len(topCrvs) != 0):
                            threeDeeValueL = values_shiftedPaths_LL[branchIndex]
                            
                            planarBrep = Rhino.Geometry.Brep.CreatePlanarBreps(topCrvs)[0]
                            planarBrep.Flip()  # for some reason the upper planarBrep has always a normal pointed downwards
                            # extrude buildings
                            if (valueMinHeight != ""):
                                # there is a valid "min_height" value
                                extrusionVec = Rhino.Geometry.Vector3d(0,0,-(height-valueMinHeight))
                            elif (valueMinHeight == ""):
                                if (groundTerrain == None):
                                    extrusionVec = Rhino.Geometry.Vector3d(0,0,-height)
                                elif(groundTerrain != None):
                                    shapeExtrudeHeight = -(height + 2 * bb_height)  # "2" is due to safety
                                    extrusionVec = Rhino.Geometry.Vector3d(0,0,shapeExtrudeHeight)
                            
                            topCrvs_StartPt = topCrvs[0].PointAtStart  # if topCrvs has more shapes than 1, the others will also be on the same height
                            extrudeCrv = Rhino.Geometry.Line(topCrvs_StartPt, topCrvs_StartPt + extrusionVec).ToNurbsCurve()
                            planarBrepFace = planarBrep.Faces[0]
                            cap = True
                            extrudedShape = Rhino.Geometry.BrepFace.CreateExtrusion(planarBrepFace, extrudeCrv, cap)
                            if (groundTerrain == None):
                                # nothing inputted into the "groundTerrain_" input
                                threeDeeShapeL = [extrudedShape]
                            elif (groundTerrain != None):
                                if (valueMinHeight != ""):
                                    threeDeeShapeL = [extrudedShape]
                                elif (valueMinHeight == ""):
                                    # something inputted into the "groundTerrain_" input
                                    splittedBreps = Rhino.Geometry.Brep.Split(extrudedShape, groundBrep_singleBrepFace, tol)
                                    if len(splittedBreps) > 0:
                                        threeDeeShapeL = [splittedBreps[0]]
                                    del splittedBreps
                    
                    else:
                        # height is equal to 0
                        threeDeeShapeL = []
                        threeDeeValueL = []
                
                # 3) neither 3d tree nor 3d building could be created with the supplied _keys and _values
                else:
                    height = 0
                    threeDeeShapeL = []
                    threeDeeValueL = []
        
        threeDeeShapesDataTree.AddRange(threeDeeShapeL, shapes_shiftedPaths_Paths[branchIndex])
        threeDeeValuesDataTree.AddRange(threeDeeValueL, shapes_shiftedPaths_Paths[branchIndex])
        heightDataTree.AddRange([height], shapes_shiftedPaths_Paths[branchIndex])
    
    
    if (threeDeeShapesDataTree.DataCount == 0):
        if (len(osm_id_Only) != 0) or (len(osm_way_id_Only) != 0):
            # this may happen if ids supplied to the "osm_id_Only_" and/or "osm_way_id_Only_" inputs of "OSM ids" component can not be found in this _location and/or radius_ (they may correspond to other _location and/or radius_)
            valid_onlyRemove_Ids_or_shapes = False
            printMsg = "The ids you supplied through \"osm_id_Only_\" and/or \"osm_way_id_Only_\" inputs do not exist for this \"_location\" and/or \"radius_\" inputs.\nTry removing the ids from the \"osm_id_Only_\" and/or \"osm_way_id_Only_\" inputs of \"OSM ids\" component."
            
            return threeDeeShapesDataTree, threeDeeValuesDataTree, heightDataTree, valid_onlyRemove_Ids_or_shapes, printMsg
        elif (len(osm_id_Only) == 0) and (len(osm_way_id_Only) == 0):
            if (atleastOneThreeDeeShapeCanBeCreated == True):
                valid_onlyRemove_Ids_or_shapes = False
                printMsg = "Supplied _values and _keys do not contain neither \"height\" nor \"building:levels\" keys which are essential for creation of 3d buildings and/or 3d trees.\n" + \
                           " \n" + \
                           "You can allow the component to create them with random heights with the use of \"randomHeightRange_\" input. Supply some domain to this input (for example: \"20 to 30\") to generate the 3d shapes."
            elif (atleastOneThreeDeeShapeCanBeCreated == False):
                valid_onlyRemove_Ids_or_shapes = False
                printMsg = "No 3D shape (building or tree) could be created with the supplied _values of _keys"
            
            return threeDeeShapesDataTree, threeDeeValuesDataTree, heightDataTree, valid_onlyRemove_Ids_or_shapes, printMsg
    
    
    # baking
    if (groundTerrain != None):
        groundTerrainInputted = "yes"
    elif (groundTerrain == None):
        groundTerrainInputted = "no"
    
    if bakeIt_:
        layerName = "heightPerLevel=" + str(heightPerLevel) + "_randomHeightRange=" + str(randomHeightRangeStart) + "-" + str(randomHeightRangeEnd) + "_groundTerrain=" + groundTerrainInputted
        
        layParentName = "GISMO"; laySubName = "OSM"; layerCategoryName = "3D_SHAPES"
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # green
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor) 
        
        threeDeeShapesFlattened = [shape  for threeDeeShapeL in threeDeeShapesDataTree.Branches  for shape in threeDeeShapeL]
        geometryIds = gismo_preparation.bakeGeometry(threeDeeShapesFlattened, layerIndex)
        
        # grouping
        groupIndex = gismo_preparation.groupGeometry("3D_OSM_SHAPES" + "_" + layerName, geometryIds)
        del threeDeeShapesFlattened
        del geometryIds
    
    
    # deleting
    del shapesDataTree; del shapes_shiftedPaths_Paths; del shapes_shiftedPaths_LL; del valuesDataTree; del values_shiftedPaths_LL; del keys; del buildingShapes  # delete local variables
    gc.collect()
    
    valid_onlyRemove_Ids_or_shapes = True
    printMsg = "ok"
    
    return threeDeeShapesDataTree, threeDeeValuesDataTree, heightDataTree, valid_onlyRemove_Ids_or_shapes, printMsg


def printOutput(osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, heightPerLevel, randomHeightRangeStart, randomHeightRangeEnd, treeType):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    
    if groundTerrain_:
        groundTerrainInputted = "yes"
    else:
        groundTerrainInputted = "no"
    
    resultsCompletedMsg = "OSM 3D component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Only remove Ids: %s, %s, %s, %s

Height per level (rhino doc. units): %s
Random height range (rhino doc. units): %s - %s
Tree geometry type: %s
Ground terrain inputted: %s
    """ % (osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, heightPerLevel, randomHeightRangeStart, randomHeightRangeEnd, treeType, groundTerrainInputted)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_createGeometry = sc.sticky["gismo_CreateGeometry"]()
        gismo_osm = sc.sticky["gismo_OSM"]()
        
        heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor, validInputData, printMsg = checkInputData(_shapes, _keys, _values, heightPerLevel_, randomHeightRange_, treeType_, onlyRemove_Ids_)
        if validInputData:
            if _runIt:
                threeDeeShapes, threeDeeValues, height, valid_onlyRemove_Ids_or_shapes, printMsg = createThreeDeeShapes(_shapes, _keys, _values, heightPerLevel, randomHeightRange, randomHeightRangeStart, randomHeightRangeEnd, treeType, groundTerrain_, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, unitConversionFactor)
                if valid_onlyRemove_Ids_or_shapes:
                    printOutput(osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove, heightPerLevel, randomHeightRangeStart, randomHeightRangeEnd, treeType)
                    threeDeeKeys = _keys
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the OSM 3D component"
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