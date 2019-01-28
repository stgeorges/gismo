# OSM search
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
Use this component to search through OSM 2D and 3D shapes. Shapes will be searched by the use of _requiredTag input. To generate _requiredTag input use "OSM tag" component.
-
1) If you would like to search OSM 2D shapes, add data to _shapes, _keys, _values inputs.  Or
2) If you would like to search OSM 3D shapes, then additionally add data to threeDeeShapes_, threeDeeValues_ inputs.
-
Provided by Gismo 0.0.3
    
    input:
        _requiredTag: Required tag represents a combination between a key and value(s) for which this component will perform the search.
                      Use "OSM tag" component to generate it.
        _shapes: Plug in the data from the Gismo OSM shapes "shapes" output
        _keys: Plug in the data from the Gismo OSM shapes "keys" output.
        _values: Plug in the data from the Gismo OSM shapes "values" output.
        threeDeeShapes_: This input is needed only if you are searching 3D shapes.
                         For example: you created 3d buildings with "OSM 3D" component, and now you would like to check which one of all those buildings is a residential building.
                         If this is the case, then plug in the data from the Gismo "OSM 3D" "threeDeeShapes" output.
                         -
                         If nothing supplied, then search of 2d OSM shapes (that's "_shapes" input) will be performed only.
        threeDeeValues_: This input is needed only if you are searching 3D shapes.
                         For example: you created 3d buildings with "OSM 3D" component, and now you would like to check which one of all those buildings is a residential building.
                         If this is the case, then plug in the data from the Gismo "OSM 3D" "threeDeeValues" output.
                         -
                         If nothing supplied, then search of 2d OSM shapes (that's "_shapes" input) will be performed only.
        createFootprints_: In case your shape is a polygon (shapeType_ = 0), this input will create a surface from it.
                           -
                           This input is irrelevant if you are performing search of 3D OSM shapes (if data is supplied to "threeDeeShapes_" and "threeDeeValues_" inputs).
                           -
                           If not supplied, default value "False" will be used.
        createFootprints_add: If your shape is a polyline (shapeType_ = 1), this input will create an offsetted surface from it. The width of the surface is controlled through "polylineWidth_" input.
                              !!! CAUTION !!! If your shape is a polyline (shapeType_ = 1) and you have a terrain added to the "groundTerrain_" input, it may take a bit longer to create offsetted surfaces from those polylines. Sometimes it may even crash your Rhino!
                              So save your .gh/.3dm files before running this component, with upper mentioned inputs!!
        polylineWidth_: Width of each _shapes in case they are polylines ("OSM shapes" component's "shapeType_" input set to 1) and "createFootprints_" set to True.
                        Basically this input enables making offseted curves or surfaces from polylines. For example offseting roads, rivers, railway paths ...
                        -
                        If not supplied, default value of 3 meters/300 centimeters/9.84 feet/118 inches... will be used.
                        -
                        In Rhino document units.
        groundTerrain_: The ground terrain surface on which the "foundShapes" will be laid onto.
                        Supply it by using "terrain" output of the Ladybug "Terrain Generator" (type_ = 1) or Gismo "Terrain Generator" (type_ = 2 or type_ = 3) components.
                        -
                        If nothing supplied, the "foundShapes" will always be laid flat onto a horizontal plane, with plane origin being the "origin" input of the "OSM shapes" component.
        bakeIt_: Set to "True" to bake the extruded _shape geometry into the Rhino scene.
                 The geometry will be grouped. To ungroup it, select it and call the "Ungroup" Rhino command.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        foundShapes: Inputted "_shapes" (for 2d search) or "threeDeeShapes_" (for 3d search) which correspond to the chosen _requiredTag input.
                     -
                     If upper "_shapes"/"threeDeeShapes_" do not satisfy the "_requiredTag", then that shape's branch will be empty.
                     Use "Clean Tree" component and set the "E" input to "True" to remove all these empty branches.
        foundKeys: A list of keys. This output is the same as "keys" output of "OSM shapes" component.
        foundValues: Values corresponding to each "foundShapes".
                     -
                     If upper "_shapes"/"threeDeeShapes_" do not satisfy the "_requiredTag", then that branch will not have any values (it will be empty).
                     Use "Clean Tree" component and set the "E" input to "True" to remove all these empty branches.
        foundShapeOrNot: If a shape corresponds to the chosen OSM object then the value will be True.
                         If it does not, then False is returned. So no empty branches will exist, as False value will be used in their place.
                         -
                         Boolean value (True or False).
        foundObjectNames: Names of the found OSM objects.
        titleOriginPt: Title base point, which can be used to move the "title" geometry with grasshopper's "Move" component.
                       -
                       Connect this output to a Grasshopper's "Point" parameter in order to preview the point in the Rhino scene.
        title: Title geometry with information about "_requiredTag" inputs.
"""

ghenv.Component.Name = "Gismo_OSM Search"
ghenv.Component.NickName = "OSMsearch"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import ghpythonlib.components as ghc
import scriptcontext as sc
import Grasshopper
import System
import random
import Rhino
import math
import time
import gc


def checkInputData(requiredTag, shapes, keys, values, threeDeeShapes, threeDeeValues, createFootprints):
    
    # get unitConversionFactor
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    
    # check _requiredTag input, get requiredKey, requiredValues, OSMobjectNameL
    if (len(requiredTag.Branches) == 0)  or  (len(requiredTag.Branches) == 1) and (requiredTag.Branches[0][0] == None):
        # this happens when nothing is supplied to the "_requiredTag" input,  OR  when "requiredTag" ouput of "OSM tag" component is supplied to the "_requiredTag" input, but the "OSM tag" component has not been ran
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_requiredTag\" input.\n" + \
                   " \n" + \
                   "Use the \"OSM tag\" component to generate this input."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    else:
        # deconstruct "_requiredTag" input to requiredKey, requiredValues
        requiredKeyL = []
        requiredValuesLL = []
        requiredTagLL = requiredTag.Branches
        for branchIndex, branchL in enumerate(requiredTag.Branches):
            if (branchIndex % 2 == 0):
                # branches with odd branchIndex are keys
                requiredKeyL.append(branchL[0])
            elif (branchIndex % 2 != 0):
                # branches with even branchIndex are values
                requiredValuesLL.append(list(branchL))
        
        for index, requiredValues in enumerate(requiredValuesLL):
            if len(requiredValues) == 0:
                requiredValuesLL[index] = ["^"]  # returning changed "requiredValues = ["^"]" in "OSM tag" component
        
        # try finding "OSMobjectName" if _requiredTag has been generated with already defined requiredKey and requiredValues
        requiredKeyRequiredValue_dict = gismo_osm.requiredTag_dictionary()
        requiredKeyRequiredValue_dict_keys = requiredKeyRequiredValue_dict.keys()
        
        OSMobjectNameL = []
        for requiredKeyIndex, requiredKey in enumerate(requiredKeyL):
            for potential_OSMobjectName in requiredKeyRequiredValue_dict_keys:
                potential_requiredKey, potential_requiredValues = requiredKeyRequiredValue_dict[potential_OSMobjectName]
                if (requiredKey == potential_requiredKey) and (requiredValuesLL[requiredKeyIndex] == list(potential_requiredValues)):
                    # "OSMobjectName" CAN be found in gismo_osm.requiredTag_dictionary()
                    OSMobjectName = potential_OSMobjectName
                    OSMobjectNameL.append(OSMobjectName)
                    break
            
            else:
                # "OSMobjectName" can not be found in gismo_osm.requiredTag_dictionary(). Create it from: requiredKey and requiredValues
                OSMobjectName_incomplete = "requiredKey=" + requiredKeyL[requiredKeyIndex] + "_requiredValues="
                
                requiredValuesL_joinedString = ""
                for index, requiredValue in enumerate(requiredValuesLL[requiredKeyIndex]):
                    if (index == 0):
                        requiredValuesL_joinedString += requiredValue
                    elif (index > 0):
                        requiredValuesL_joinedString += "," + requiredValue
                
                OSMobjectName = OSMobjectName_incomplete + requiredValuesL_joinedString
            
                OSMobjectNameL.append(OSMobjectName)
        
        del requiredKeyRequiredValue_dict
        # leave these three lines below for testing
        #print "OSMobjectNameL: ", OSMobjectNameL
        #print "requiredKeyL: ", requiredKeyL
        #print "requiredValuesLL: ", requiredValuesLL
    
    
    # check _shapes, _keys, _values inputs
    if (shapes.DataCount == 0):
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "Please connect the \"shapes\" output from Gismo \"OSM shapes\" component to this component's \"_shapes\" input."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    
    elif (len(shapes.Branches) == 1) and (shapes.Branches[0][0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_shapes\" input.\n" + \
                   " \n" + \
                   "Please connect the \"shapes\" output from Gismo \"OSM shapes\" component to this component's \"_shapes\" input.\n" + \
                   "And make sure that you set the \"OSM shapes\" \"_runIt\" input to \"True\"."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    
    
    if (len(keys) == 0):
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "Please connect the \"keys\" output from Gismo \"OSM shapes\" component to this component's \"_keys\" input."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    elif (len(keys) == 1) and (keys[0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_keys\" input.\n" + \
                   " \n" + \
                   "Please connect the \"keys\" output from Gismo \"OSM shapes\" component to this component's \"_keys\" input.\n" + \
                   "And make sure that you set the \"OSM shapes\" \"_runIt\" input to \"True\"."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    
    
    if (values.DataCount == 0):
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "Please connect the \"values\" output from Gismo \"OSM shapes\" component to this component's \"_values\" input."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    
    elif (len(values.Branches) == 1) and (values.Branches[0][0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_values\" input.\n" + \
                   " \n" + \
                   "Please connect the \"values\" output from Gismo \"OSM shapes\" component to this component's \"_values\" input.\n" + \
                   "And make sure that you set the \"OSM shapes\" \"_runIt\" input to \"True\"."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    
    
    if len(shapes.Paths) != len(values.Paths):
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "The number of tree branches inputted to the \"_shapes\" and \"_values\" inputs do not match.\n" + \
                   " \n" + \
                   "Make sure that you connected:\n" + \
                   "\"shapes\" output from Gismo \"OSM shapes\" component to this component's \"_shapes\" input. And:\n" + \
                   "\"values\" output from Gismo \"OSM shapes\" component to this component's \"_values\" input."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    
    
    
    # check threeDeeShapes_, threeDeeValues_ inputs
    validThreeDeeShapes = False  # initial value
    validThreeDeeValues = False  # initial value
    valid_threeDeeShapes_vs_threeDeeValues = False  # initial value
    perform_searchThreeDeeShapes = False  # initial value
    
    if (len(threeDeeShapes.Branches) == 1) and (threeDeeShapes.Branches[0][0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_threeDeeShapes\" input.\n" + \
                   " \n" + \
                   "Please connect the \"threeDeeShapes\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeShapes\" input.\n" + \
                   "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    elif (threeDeeShapes.DataCount != 0):
        validThreeDeeShapes = True
    
    
    if (len(threeDeeValues.Branches) == 1) and (threeDeeValues.Branches[0][0] == None):
        # this happens when "OSM shapes" component's "_runIt" input is set to "False"
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_threeDeeValues\" input.\n" + \
                   " \n" + \
                   "Please connect the \"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeValues\" input.\n" + \
                   "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    elif (threeDeeValues.DataCount != 0):
        validThreeDeeValues = True
    
    
    if len(threeDeeShapes.Paths) != len(threeDeeValues.Paths):
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "The number of tree branches inputted to the \"threeDeeShapes_\" and \"threeDeeValues_\" inputs do not match.\n" + \
                   " \n" + \
                   "Make sure that you connected:\n" + \
                   "\"threeDeeShapes\" output from Gismo \"OSM 3D\" component to this component's \"threeDeeShapes_\" input. And:\n" + \
                   "\"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"threeDeeValues_\" input."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    else:
        valid_threeDeeShapes_vs_threeDeeValues = True
    
    if (validThreeDeeShapes == True) and (validThreeDeeValues == True) and (valid_threeDeeShapes_vs_threeDeeValues == True):
        perform_searchThreeDeeShapes = True
    
    
    if (createFootprints == None):
        createFootprints = True  # default
    
    polylineWidth_rhinoUnits = 3  # dummy value until implemented
    if (polylineWidth_rhinoUnits == None):
        polylineWidth_rhinoUnits = 3/unitConversionFactor  # default: 3 meters, 300 centimeters, 9.84 feet, 118 inches ...
    
    
    # check the "shapeType_" input value set in the "OSM shapes" component.
    shapeType = gismo_preparation.checkShapeType(shapes.Branches)
    if (perform_searchThreeDeeShapes == True)  and  ((shapeType == 1) or (shapeType == 2)):
        OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
        validInputData = False
        printMsg = "This component can be used to find only 3D shapes for \"shapeType_ == 0\" set in \"OSM shapes\" component.\n" + \
                   " \n" + \
                   "For any other \"shapeType_\" value (1 and 2), just unplug the data from the \"threeDeeShapes_\" and \"threeDeeValues_\" inputs of this component.\n" + \
                   "In this way, 2D shapes will be successfully searched."
        return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    elif (perform_searchThreeDeeShapes == True)  and  (shapeType == 0):
        # everything is ok, as this component can be used to find only 3d shapes for shapeType == 0, which currently is the case.
        pass
    
    """
    if (shapeType == 1) and (createFootprints == True):
        # if shapeType == 1, and createFootprints_ == True: check if check if "clipper_x.dll" file is located in "gismo_install_folder\libraries". If not download it
        gismoFolder = sc.sticky["gismo_gismoFolder"]
        clipper_library_dll_filePath, validClipperLibrary, printMsg = gismo_clipper.checkClipperLibrary(gismoFolder)
        if (validClipperLibrary == False):
            OSMobjectNameL = requiredKeyL = requiredValuesLL = createFootprints = polylineWidth_rhinoUnits = perform_searchThreeDeeShapes = shapeType = None
            validInputData = False
            return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg
    """
    
    del shapes; del keys; del values; del threeDeeShapes; del threeDeeValues  # delete local variables
    validInputData = True
    printMsg = "ok"
    
    return OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg


def searchShapes(requiredKeyL, requiredValuesLL, shapesDataTree, keys, valuesDataTree, threeDeeShapesDataTree, threeDeeValuesDataTree, createFootprints, polylineWidth_rhinoUnits, groundTerrain, shapeType, perform_searchThreeDeeShapes):
    
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    projectionDirection = Rhino.Geometry.Vector3d(0,0,1)  # it can be projectionDirection = Rhino.Geometry.Vector3d(0,0,-1) as well, does not matter
    
    if groundTerrain:
        # something inputted to the "groundTerrain_"
        groundBrep_singleBrepFace = groundTerrain.Faces[0].DuplicateFace(False)  # in case inputted "groundTerrain_" has a thickness
        accurate = False
        bb_volume, bb_centroid, bb_length, bb_depth, bb_height, bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner = gismo_preparation.boundingBox_properties([groundTerrain], accurate)
        if bb_height == 0:  # the terrain is comletely flat
            bb_height = 10
        shapeExtrudeHeight = 3 * bb_height  # "3" is due to safety
        
        groundTerrain_edges = groundTerrain.DuplicateEdgeCurves()
        
        if (len(groundTerrain_edges) == 1):
            # circular groundTerrain without NO "standThickness_" (Terrain Generator 2 component)
            groundTerrain_outterEdge = Rhino.Geometry.Curve.JoinCurves([groundTerrain_edges[0]], tol)[0]
        elif (len(groundTerrain_edges) == 3):
            # circular groundTerrain_ with "standThickness_" (Terrain Generator 2 components)
            groundTerrain_outterEdge = Rhino.Geometry.Curve.JoinCurves([groundTerrain_edges[0]], tol)[0]
        elif (len(groundTerrain_edges) == 4):
            # rectangular groundTerrain_ with NO "standThickness_" (Terrain Generator or Terrain Generator 2 component)
            groundTerrain_outterEdge = Rhino.Geometry.Curve.JoinCurves(groundTerrain_edges, tol)[0]
        elif (len(groundTerrain_edges) == 9) or (len(groundTerrain_edges) == 12):
            # rectangular groundTerrain_ with "standThickness_" (Terrain Generator 2 component)
            groundTerrain_outterEdge = Rhino.Geometry.Curve.JoinCurves(groundTerrain_edges[:4], tol)[0]
        
        extrudeVector = Rhino.Geometry.Vector3d(0,0,bb_height)
        groundTerrain_outerEdge_extrusion = Rhino.Geometry.Surface.CreateExtrusion(groundTerrain_outterEdge, extrudeVector).ToBrep()
        
        
    else:
        # nothing inputted to the "groundTerrain_"
        groundBrep_singleBrepFace = None
        shapeExtrudeHeight = None  # dummy value
        bb_height = 30  # dummy value
        groundTerrain_outerEdge_extrusion = None  # dummy value
    
    """
    # option 1
    # compare "OSM shapes" and "Terrain Generator" component's "origin_" inputs. Their Z coordinate needs to be equal or 
    OSMshapesComp_origin = sc.sticky["gismo_OSMshapesComp_origin"]
    if sc.sticky.has_key("gismo_terrainGeneratorComp_origin"):
        #print "__Gismo Terrain Generator component ran !!"
        # groundTerrain_ inputted from Gismo "Terrain Generator"
        terrainGeneratorComp_origin = sc.sticky["gismo_terrainGeneratorComp_origin"]
        if OSMshapesComp_origin.Z >= terrainGeneratorComp_origin.Z:
            # if origin_ from "OSM shapes" component is on equal or above height than origin_ from "Terrain Generator" component
            liftingOSMshapesHeight = 30  # dummy value
        elif OSMshapesComp_origin.Z < terrainGeneratorComp_origin.Z:
            # if origin_ height from "OSM shapes" component is lower than origin_ height from "Terrain Generator" component.
            liftingOSMshapesHeight = abs((terrainGeneratorComp_origin.Z - OSMshapesComp_origin.Z) + 30)  # 30 is dummy value
    else:
        #print "__Ladybug Terrain Generator component ran !!"
        # groundTerrain_ inputted from Ladybug "Terrain Generator"
        liftingOSMshapesHeight = 8848  # dummy (high) value
    """
    # option 2
    if groundTerrain:
        liftingOSMshapesHeight = gismo_preparation.LiftingOSMshapesHeight(shapesDataTree, shapeType, bb_height, bb_bottomLeftCorner)
    else:
        # nothing inputted to the "groundTerrain_"
        liftingOSMshapesHeight = 0
    
    
    if (shapeType == 0):
        # shift the paths in "shapes" and "values" data trees by -1, to create closed surfaces with holes
        shapes_shiftedPaths_DataTree = gismo_preparation.datatree_shiftPaths(shapesDataTree)
        values_shiftedPaths_DataTree = gismo_preparation.datatree_shiftPaths(valuesDataTree)
    elif (shapeType != 0):
        # no shifting of paths should be done for shapeType == 1,2
        shapes_shiftedPaths_DataTree = shapesDataTree
        values_shiftedPaths_DataTree = valuesDataTree
    
    shapes_shiftedPaths_Paths = shapes_shiftedPaths_DataTree.Paths
    shapes_shiftedPaths_LL = shapes_shiftedPaths_DataTree.Branches
    values_shiftedPaths_LL = values_shiftedPaths_DataTree.Branches
    
    foundShapes_flattened = []  # for 3D, or offset polylines
    foundOSMobjectNames_flattened = []  # for 3D
    foundShapesDataTree = Grasshopper.DataTree[object]()
    foundValuesDataTree = Grasshopper.DataTree[object]()
    foundShapeOrNotDataTree = Grasshopper.DataTree[object]()
    foundOSMobjectNamesDataTree = Grasshopper.DataTree[object]()
    paths = shapes_shiftedPaths_DataTree.Paths
    
    for branchIndex,shapesL in enumerate(shapes_shiftedPaths_LL):
        if len(shapesL) == 0:
            # some shape may have been removed with the "OSM ids" component
            foundShapesL = []
            values = []
            foundShapeOrNotL = [False]
            OSMobjectNameBranchL = []
        else:
            foundShapesSwitch, value, OSMobjectNameBranchL = gismo_gis.tagEqual_to_requiredTag(branchIndex, keys, values_shiftedPaths_LL, requiredKeyL, requiredValuesLL, OSMobjectNameL)
            
            if foundShapesSwitch == True:
                if (len(shapesL) == 0):
                    # for some unknown reason "shapesL" is empty
                    foundShapesL = []
                    values = []
                    foundShapeOrNotL = [False]
                    OSMobjectNameBranchL = []
                elif (len(shapesL) > 0):
                    # set "values" and "foundShapeOrNotL" at the very start. Now find the "foundShapesL"
                    values = values_shiftedPaths_LL[branchIndex]
                    foundShapeOrNotL = [True]
                
                
                if (shapeType == 2):
                    # 1) shapeType_ == 2 (points)
                    if (groundBrep_singleBrepFace == None):
                        # 1) NOTHING inputted into "terrainGround_"
                        foundShapesL = shapesL
                    elif (groundBrep_singleBrepFace != None):
                        # b) terrain inputted into "terrainGround_"
                        shapesL_point3d = [shapesL[0].Location]  # converting the "Point" to "Point3d" type
                        foundShapesL = Rhino.Geometry.Intersect.Intersection.ProjectPointsToBreps([groundBrep_singleBrepFace], shapesL_point3d, projectionDirection, tol)  # foundShapesL will be empty is a point is out of the groundTerrain_ boundaries
                
                
                elif (shapeType == 0) or (shapeType == 1):
                    # 2) 3) shapeType_ == 0 and shapeType_ == 1 (polygons and polylines)
                    
                    
                    # collect all "foundShapesL" in a single flattened list so that they can all be offsetted on line 550?
                    if (shapeType == 1) and (createFootprints == True):
                        foundShapes_flattened.extend(shapesL)
                    
                    
                    # else if (shapeType != 1) AND (createFootprints != True)
                    if (groundBrep_singleBrepFace == None):
                        # a) NOTHING inputted into "terrainGround_"
                        if (createFootprints == False):
                            foundShapesL = shapesL
                        elif (createFootprints == True):
                            try:
                                # closed shapesL (shapeType == 0)
                                foundShapesL = [Rhino.Geometry.Brep.CreatePlanarBreps(shapesL)[0]]
                            except:
                                # opened shapesL (shapeType == 1)
                                foundShapesL = shapesL
                    
                    elif (groundBrep_singleBrepFace != None):
                        # b) terrain inputted into "terrainGround_"
                        if (createFootprints == False):
                            projectedShapesL = Rhino.Geometry.Curve.ProjectToBrep(shapesL, [groundBrep_singleBrepFace], projectionDirection, 0.01)
                            if len(projectedShapesL) > 0:
                                foundShapesL = projectedShapesL
                            else:
                                foundShapesL = []
                                values = []
                                foundShapeOrNotL = [False]
                                OSMobjectNameBranchL = []
                        
                        elif (createFootprints == True):
                            if (not shapesL[0].IsClosed):  # it is assumed that all shapes in "shapesL" are closed or open
                                # the shapesL[0] is not closed (this will happen with shapeType == 1)
                                projectedShapesL = Rhino.Geometry.Curve.ProjectToBrep(shapesL, [groundBrep_singleBrepFace], projectionDirection, 0.01)
                                if len(projectedShapesL) > 0:
                                    foundShapesL = projectedShapesL
                                elif len(projectedShapesL) == 0:
                                    # shapesL is outside of groundTerrain_ bounding box
                                    foundShapesL = []
                                    values = []
                                    foundShapeOrNotL = [False]
                                    OSMobjectNameBranchL = []
                            
                            elif (shapesL[0].IsClosed):
                                # move _shapes above so that intersection with groundTerrain_ is fullfiled successfully
                                moveMatrix = Rhino.Geometry.Transform.Translation(0,0,liftingOSMshapesHeight)
                                for shapeIndex, shape in enumerate(shapesL):
                                    shape.Transform(moveMatrix)
                                
                                planarBrep = Rhino.Geometry.Brep.CreatePlanarBreps(shapesL)[0]
                                shapeStartPt = shapesL[0].PointAtStart  # if there are more shapes in shapesL, they will all have the same Z coordinates (on the same height)
                                extrudePathCurve = Rhino.Geometry.Line(shapeStartPt, Rhino.Geometry.Point3d(shapeStartPt.X, shapeStartPt.Y, shapeStartPt.Z - (liftingOSMshapesHeight+(2 * bb_height)) )).ToNurbsCurve()
                                cap = True
                                extrudedShapeBrep = planarBrep.Faces[0].CreateExtrusion(extrudePathCurve, cap)
                                splittedBreps = Rhino.Geometry.Brep.Split(groundBrep_singleBrepFace, extrudedShapeBrep, tol)
                                
                                if len(splittedBreps) > 0:
                                    # the shapesL are inside of groundTerrain_ bounding box (a) or the interesect with it (b)
                                    # determine which one of these two is the case
                                    intersectionYes, intersectCrvs, intersectPts = Rhino.Geometry.Intersect.Intersection.BrepBrep(groundTerrain_outerEdge_extrusion, extrudedShapeBrep, tol)
                                    
                                    if (len(intersectCrvs) > 0):
                                        # shapeL planar srf intersects with groundTerrrain_
                                        foundShapesL = [splittedBreps[0]]
                                        foundShapesL[0].Faces.ShrinkFaces()  # shrink the cutted foundShapesL
                                    elif (len(intersectCrvs) == 0):
                                        # shapeL planar srf is inside groundTerrain_ and does not intersect it
                                        foundShapesL = [splittedBreps[len(splittedBreps)-1]]
                                        foundShapesL[0].Faces.ShrinkFaces()  # shrink the cutted foundShapesL
                                    
                                else:
                                    # shapesL is outside of groundTerrain_ bounding box
                                    foundShapesL = []
                                    values = []
                                    foundShapeOrNotL = [False]
                                    OSMobjectNameBranchL = []
                                
                                del splittedBreps
                                del extrudedShapeBrep
            
            
            else:
                # the required value is not found. There for the OSM object sought through "_requiredTag" is not found. Try changing the "shapeType_" at "OSM shapes" component
                foundShapesL = []
                values = []
                foundShapeOrNotL = [False]
                OSMobjectNameBranchL = []
        
        if (len(foundShapesL) != 0):  # the object has been found so the "foundShapesL" list is not empty
            foundShapes_flattened.extend(foundShapesL)  # for 3D foundShapes only
            foundOSMobjectNames_flattened.extend(OSMobjectNameBranchL)
        foundShapesDataTree.AddRange(foundShapesL, shapes_shiftedPaths_Paths[branchIndex])
        foundValuesDataTree.AddRange(values, shapes_shiftedPaths_Paths[branchIndex])
        foundShapeOrNotDataTree.AddRange(foundShapeOrNotL, shapes_shiftedPaths_Paths[branchIndex])
        foundOSMobjectNamesDataTree.AddRange(OSMobjectNameBranchL, shapes_shiftedPaths_Paths[branchIndex])
    
    
    
    # 3D (foundThreeDeeShapesDataTree, foundThreeDeeValuesDataTree, foundThreeDeeShapeOrNotDataTree if "threeDeeShapes_" and "threeDeeValues_" are inputted)
    foundThreeDeeShapesDataTree = Grasshopper.DataTree[object]()
    foundThreeDeeValuesDataTree = Grasshopper.DataTree[object]()
    foundThreeDeeShapeOrNotDataTree = Grasshopper.DataTree[object]()
    foundThreeDeeOSMobjectNamesDataTree = Grasshopper.DataTree[object]()
    if (perform_searchThreeDeeShapes == True):
        threeDeeShapes_LL = threeDeeShapesDataTree.Branches
        threeDeeValues_LL = threeDeeValuesDataTree.Branches
        threeDeePaths = threeDeeShapesDataTree.Paths
        for branchIndex,threeDeeShapesL in enumerate(threeDeeShapes_LL):
            if (len(threeDeeShapesL) != 0):
                upperFace = threeDeeShapesL[0].Faces[0]
                upperFaceCentroid = Rhino.Geometry.AreaMassProperties.Compute(upperFace).Centroid
                for foundShapeIndex, foundShape in enumerate(foundShapes_flattened):
                    upperFaceCentroid_projected = Rhino.Geometry.Intersect.Intersection.ProjectPointsToBreps([foundShape], [upperFaceCentroid], projectionDirection, tol)
                    if len(upperFaceCentroid_projected) == 0:
                        continue
                    else:
                        foundThreeDeeShapesL = threeDeeShapesL
                        foundThreeDeeValuesL = threeDeeValues_LL[branchIndex]
                        foundThreeDeeShapeOrNotL = [True]
                        OSMobjectNameBranchL = [foundOSMobjectNames_flattened[foundShapeIndex]]
                        break
                else:
                    foundThreeDeeShapesL = []
                    foundThreeDeeValuesL = []
                    foundThreeDeeShapeOrNotL = [False]
                    OSMobjectNameBranchL = []
            else:
                # the 3d shape was not created from some particular shape
                foundThreeDeeShapesL = []
                foundThreeDeeValuesL = []
                foundThreeDeeShapeOrNotL = [False]
                OSMobjectNameBranchL = []
            
            foundThreeDeeShapesDataTree.AddRange(foundThreeDeeShapesL, threeDeePaths[branchIndex])
            foundThreeDeeValuesDataTree.AddRange(foundThreeDeeValuesL, threeDeePaths[branchIndex])
            foundThreeDeeShapeOrNotDataTree.AddRange(foundThreeDeeShapeOrNotL, threeDeePaths[branchIndex])
            foundThreeDeeOSMobjectNamesDataTree.AddRange(OSMobjectNameBranchL, threeDeePaths[branchIndex])
    
    
    """
    # special case for (shapeType == 1) and (createFootprints == True):
    if (shapeType == 1) and (createFootprints == True):
        tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        halfStreetWidth = polylineWidth_rhinoUnits/2  # in rhino units
        
        # convert all crvs from "foundShapes_flattened" to polylines and explode them to their segments
        explodePolyline = True
        exploded_roadShapesLL_flattened = []
        #for crv in foundShapes_flattened2:  # "foundShapes_flattened2" is this component's input used for testing
        for crv in foundShapes_flattened:
            explodedLines = gismo_geometry.convertCrvToPolyline(crv, explodePolyline)
            exploded_roadShapesLL_flattened.extend(explodedLines)
        
        # everything is fine with both "clipper_x.dll" file and calling methods from it
        try:
            offsettedPolylines = gismo_clipper.offsetCurves(exploded_roadShapesLL_flattened, halfStreetWidth)
        except Exception, e:
            print "e: ", e
            if (str(e).strip() == "Instance is read-only."):
                printMsg = "The component failed to offset searched \"_shapes\".\n" + \
                           "This can happen in cases when there is a complex network of \"_shapes\" polylines. Component then fails to offset all of them.\n" + \
                           "Try decreasing/increasing the \"polylineWidth_\" input to try fixing this issue."
            else:
                printMsg = "The component failed to run due to the following error message:\n\n" + \
                           "%s" % e
            foundShapesDataTree = foundValuesDataTree = foundShapeOrNotDataTree = foundOSMobjectNamesDataTree = None
            validInputs = False
            return foundShapesDataTree, foundValuesDataTree, foundShapeOrNotDataTree, foundOSMobjectNamesDataTree, validInputs, printMsg
        
        
        #global offsettedPlanarShapes
        # rebuild or simplify offsettedPolylines
        offsettedPlanarShapes = []
        for polyline in offsettedPolylines:
            nurbsCrv = polyline.ToNurbsCurve()
            if (nurbsCrv.IsClosed):
                areaMassProperties = Rhino.Geometry.AreaMassProperties.Compute(nurbsCrv, tol)
                if (areaMassProperties.Area > 1):  # do not include any closed curves which are smaller than 1 area of square rhino units
                    
                    # try to avoid self-intersection parts by culling the close polyline pts
                    polyline_withCulled_closePts = gismo_geometry.cullClosePolylinePts(polyline)
                    
                    # simplify the "nurbsCrv2"
                    deviationTol = 0.7  # the best one!
                    #deviationTol = 2.0
                    angleTol = 1
                    nurbsCrv2 = polyline_withCulled_closePts.ToNurbsCurve()
                    simplifiedCrv, simplifiedCrv_Success = ghc.SimplifyCurve(nurbsCrv2, deviationTol, angleTol)
                    if (simplifiedCrv_Success == True):
                        # ghc.SimplifyCurve component successfully simplified the "nurbsCrv2"
                        simplifiedCrv2 = simplifiedCrv
                    elif (simplifiedCrv_Success == False):
                        # ghc.SimplifyCurve component failed to simplify the "nurbsCrv2". Use "nurbsCrv2" as simplified curve
                        simplifiedCrv2 = nurbsCrv2
                    
                    # check if after culling of close polyline points, and simplification the "simplifiedCrv2" intersects itself. If it does, try increasing/decreasing the "streetWidth_" input
                    intersectionEvents = Rhino.Geometry.Intersect.Intersection.CurveSelf(simplifiedCrv2, tol)
                    if len(intersectionEvents) == 0:
                        # "nurbsCrv2" does NOT intersects itself. everything is fine
                        offsettedPlanarShapes.append(simplifiedCrv2)
                    elif len(intersectionEvents) > 0:
                        # "nurbsCrv2" intersects itself
                        foundShapesDataTree = foundValuesDataTree = foundShapeOrNotDataTree = foundOSMobjectNamesDataTree = None
                        validInputs = False
                        printMsg = "Due to complex combination of \"_shapes\" input, if \"createFootprints\" is set to True, it may happen that sometimes the road footprint edges overlap itself.\n" + \
                                   "To solve this issue, try changing the \"streetWidth_\" input slightly. For example, try increasing it by 1.0 or similar value."
                        return foundShapesDataTree, foundValuesDataTree, foundShapeOrNotDataTree, foundOSMobjectNamesDataTree, validInputs, printMsg
        
        #roadSrfProjectedOnTerrainL, validGroundTerrain, printMsg = gismo_geometry.projectPlanarClosedCrvsToTerrain(offsettedPlanarShapes, groundBrep_singleBrepFace, groundTerrain_outerEdge_extrusion)
        #global extrudedShapeBrepL
        roadSrfProjectedOnTerrainL, extrudedShapeBrepL, validGroundTerrain, printMsg = gismo_geometry.projectPlanarClosedCrvsToTerrain(offsettedPlanarShapes, groundBrep_singleBrepFace, groundTerrain_outerEdge_extrusion)
        #roadSrfProjectedOnTerrainL = [Rhino.Geometry.Sphere(Rhino.Geometry.Point3d(0,0,4), 5).ToBrep()]; validGroundTerrain = False; printMsg = "something is wrong. testing"
        
        # clear the output data trees
        foundShapesDataTree.Clear(); foundValuesDataTree.Clear()
        
        outputMsg = "This output is not accessible due to \"groundTerrain_\" input set to True. This means that all polyline \"_shapes\" are joined into a single or more surfaces, there for their individual values are now merged as well."
        foundShapesDataTree.AddRange(roadSrfProjectedOnTerrainL, Grasshopper.Kernel.Data.GH_Path(0))
        foundValuesDataTree.AddRange([outputMsg], Grasshopper.Kernel.Data.GH_Path(0))
    """
    
    
    # deleting
    del shapesDataTree; del shapes_shiftedPaths_Paths; del shapes_shiftedPaths_LL; del valuesDataTree; del values_shiftedPaths_LL; del keys  # delete local variables
    del groundBrep_singleBrepFace; #del groundTerrain_outerEdge_extrusion
    gc.collect()
    
    
    if (foundShapesDataTree.DataCount == 0):
        # 2D OSM search
        foundShapesDataTree = foundValuesDataTree = foundShapeOrNotDataTree = foundOSMobjectNamesDataTree = None
        validInputs = False
        printMsg = "No OSM object can be found for the given _keys and _values.\n\n" + \
                   "These can be due to the following few reasons:\n" + \
                   "-\n" + \
                   "1) The simplest one: there really isn't that kind of OSM object at that \"_location\" and for that \"_radius\".\n" + \
                   "-\n" + \
                   "2) You might be searching in incorrect \"shapeType_\" input.\n" + \
                   "_keys and _values are affected by \"shapeType_\" input of the \"OSM shapes\" component. For example, trees will always be located (if they exist at that location) for shapeType_ = 2 (points). They can not be found in shapeType_ = 0 (polygons).\n" + \
                   "-\n" + \
                   "3) OSM object is basically found by matching certain _keys with _values. It can be that you haven't initially defined a list of specific _keys so that this component would find the OSM object based on them.\n" + \
                   "To solve this problem define the \"requiredKeys_\" input of the \"OSM shapes\" component by using the \"OSM keys\" component. Generate the keys in \"OSM keys\" component by using the same OSM object for which you are performing a search in this component."
        return foundShapesDataTree, foundValuesDataTree, foundShapeOrNotDataTree, foundOSMobjectNamesDataTree, validInputs, printMsg
    
    if (foundThreeDeeShapesDataTree.DataCount == 0) and (threeDeeShapes_.DataCount != 0) and (threeDeeValues_.DataCount != 0):
        # 3D OSM search
        foundThreeDeeShapesDataTree = foundThreeDeeValuesDataTree = foundThreeDeeShapeOrNotDataTree = foundThreeDeeOSMobjectNamesDataTree = None
        validInputs = False
        printMsg = "No 3D OSM object can be found through _requiredTag for the given _shapes, _keys, _values and threeDeeShapes_, threeDeeValues_ data."
        return foundThreeDeeShapesDataTree, foundThreeDeeValuesDataTree, foundThreeDeeShapeOrNotDataTree, foundThreeDeeOSMobjectNamesDataTree, validInputs, printMsg
    
    
    validInputs = True
    printMsg = "ok"
    if (perform_searchThreeDeeShapes == True):
        # 3D OSM search
        return foundThreeDeeShapesDataTree, foundThreeDeeValuesDataTree, foundThreeDeeShapeOrNotDataTree, foundThreeDeeOSMobjectNamesDataTree, validInputs, printMsg
    elif (perform_searchThreeDeeShapes == False):
        # 2D OSM search
        return foundShapesDataTree, foundValuesDataTree, foundShapeOrNotDataTree, foundOSMobjectNamesDataTree, validInputs, printMsg


def titleAndBaking(OSMobjectNameL, foundShapesDataTree, foundObjectNamesDataTree, shapeType):
    
    # title
    
    # "groundTerrain_" NOT inputted:
    foundShapesFlattenedList = []
    ptcloud = Rhino.Geometry.PointCloud()  # use it for shapeType = 2 (because Point3d class does not contain the "GetBoundingBox" method)
    for subL in foundShapesDataTree.Branches:
        if len(subL) > 0:
            for shape in subL:
                if shapeType == 2:
                    # points (shapeType = 2)
                    if (type(shape) == Rhino.Geometry.Point3d):
                        ptcloud.Add(shape)
                    elif (type(shape) == Rhino.Geometry.Point):
                        ptcloud.Add(shape.Location)
                else:
                    try:
                        # polygons, polyline (shapeType = 0, 1)
                        curve = shape.ToNurbsCurve()
                        foundShapesFlattenedList.append(curve)
                    except:
                        # 3d buildings (shapeType = 0)
                        foundShapesFlattenedList.append(shape)
    
    
    # generate "OSMobjectNames_found_joinedString" from "foundObjectNamesDataTree":
    OSMobjectNameL_found = []
    for foundObjectNamesL in foundObjectNamesDataTree.Branches:
        if len(foundObjectNamesL) > 0:
            if foundObjectNamesL[0] in OSMobjectNameL:
                if foundObjectNamesL[0] not in OSMobjectNameL_found:  # do not add the OSMobjectName if it has already been added to "OSMobjectNameL_found"
                    OSMobjectNameL_found.append(foundObjectNamesL[0])
    
    OSMobjectNames_found_joinedString = ""
    for index, OSMobjectName in enumerate(OSMobjectNameL_found):
        if (index == 0):
            OSMobjectNames_found_joinedString += OSMobjectName
        elif (index > 0):
            OSMobjectNames_found_joinedString += "," + OSMobjectName
    
    
    titleLabelText = "Found OSM shapes for:\n%s" % OSMobjectNames_found_joinedString
    if groundTerrain_:
        # "groundTerrain_" inputted:
        shrinkSuccess = groundTerrain_.Faces.ShrinkFaces()  # in case for some unknown reason created groundTerrain_ does not have at least one of its faces shrank
        titleLabelMesh, titleStartPt, titleTextSize = gismo_preparation.createTitle("mesh", [groundTerrain_], [titleLabelText])
    else:
        if shapeType == 2:
            titleLabelMesh, titleStartPt, titleTextSize = gismo_preparation.createTitle("mesh", [ptcloud], [titleLabelText])
        else:
            titleLabelMesh, titleStartPt, titleTextSize = gismo_preparation.createTitle("mesh", foundShapesFlattenedList, [titleLabelText])
    del ptcloud
    
    
    # baking
    if bakeIt_:
        
        layerName = OSMobjectNames_found_joinedString[:50].upper()  # limit the layerName to 50 characters of "OSMobjectNames_found_joinedString" string
        
        layParentName = "GISMO"; laySubName = "OSM"; layerCategoryName = "SEARCHED_SHAPES"
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # green
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor) 
        
        foundShapesFlattened = [shape  for foundShapesL in foundShapesDataTree.Branches  for shape in foundShapesL]
        geometryIds = gismo_preparation.bakeGeometry(foundShapesFlattened, layerIndex)
        geometryIds2 = gismo_preparation.bakeGeometry([titleLabelMesh], layerIndex)
        
        # grouping
        groupIndex = gismo_preparation.groupGeometry("OSM_FOUND_SHAPES" + "_" + layerName + "_shapesOnly", geometryIds)
        groupIndex2 = gismo_preparation.groupGeometry("OSM_FOUND_SHAPES" + "_" + layerName + "_shapesAndTitle", geometryIds2)
        del geometryIds; del geometryIds2
    
    
    # hide titleOriginPt
    ghenv.Component.Params.Output[7].Hidden = True
    
    # deleting
    del foundShapesDataTree; del foundShapesFlattenedList; del foundObjectNamesDataTree
    
    return titleLabelMesh, titleStartPt


def printOutput(requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits):
    
    #requiredTagLL = [list(item)  for item in requiredTag.Branches]
    #if requiredValues == ["^"]: requiredValues = []
    
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    
    if groundTerrain_:
        groundTerrainInputted = "yes"
    else:
        groundTerrainInputted = "no"
    
    resultsCompletedMsg = "OSM search component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

requiredTag: 
keys: %s
values: %s

Ground terrain inputted: %s
    """ % (requiredKeyL, requiredValuesLL, groundTerrainInputted)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_geometry = sc.sticky["gismo_CreateGeometry"]()
        gismo_gis = sc.sticky["gismo_GIS"]()
        gismo_osm = sc.sticky["gismo_OSM"]()
        
        OSMobjectNameL, requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits, perform_searchThreeDeeShapes, shapeType, validInputData, printMsg = checkInputData(_requiredTag, _shapes, _keys, _values, threeDeeShapes_, threeDeeValues_, createFootprints_)
        if validInputData:
            if _runIt:
                if (not perform_searchThreeDeeShapes):
                    # 2D
                    foundShapes, foundValues, foundShapeOrNot, foundObjectNames, validInputs, printMsg = searchShapes(requiredKeyL, requiredValuesLL, _shapes, _keys, _values, threeDeeShapes_, threeDeeValues_, createFootprints, polylineWidth_rhinoUnits, groundTerrain_, shapeType, perform_searchThreeDeeShapes)
                elif perform_searchThreeDeeShapes:
                    # 3D
                    createFootprints = True
                    foundShapes, foundValues, foundShapeOrNot, foundObjectNames, validInputs, printMsg = searchShapes(requiredKeyL, requiredValuesLL, _shapes, _keys, _values, threeDeeShapes_, threeDeeValues_, createFootprints, polylineWidth_rhinoUnits, groundTerrain_, shapeType, perform_searchThreeDeeShapes)
                if validInputs:
                    title, titleOriginPt = titleAndBaking(OSMobjectNameL, foundShapes, foundObjectNames, shapeType)
                    printOutput(requiredKeyL, requiredValuesLL, createFootprints, polylineWidth_rhinoUnits)
                    foundKeys = _keys
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the OSM search component"
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
