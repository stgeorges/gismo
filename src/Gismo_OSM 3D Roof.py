# OSM 3D Roof
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2021, Djordje Spasic <djordjedspasic@gmail.com>
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
Use this component to create 3d roofs geometry.
They can be created in two ways:
1) If there is a valid value (not equal to "") for the "roof:shape=hipped" and "roof:angle" key, then the 3d roof will be created according to this angle.
2) If this value is lacking (equal to ""), then pitched, hipped roof can be created with random angle. Or parapet wall for flat roof, with random height. This requires a domain to be added to the "randomRange_" input.
If neither of these two ways are fulfilled, then no creation of 3d roof will be performed.
-
Component is experimental! In some cases the pitched roof may fail to be created, or it may create an invalid roof geometry!
-
Provided by Gismo 0.0.3
    
    input:
        _threeDeeShapes: Plug in the shapes from the Gismo OSM 3D "threeDeeShapes" output
        _threeDeeKeys: Plug in the keys from the Gismo OSM 3D "threeDeeKeys" output.
        _threeDeeValues: Plug in the values from the Gismo OSM 3D "threeDeeValues" output.
        randomRange_: This input can be useful if supplied "_threeDeeShapes" do not contain valid values for "roof:shape" and "roof:angle" keys.
                      If they still contain any "building" key with valid value, then the input be used to create a 3d roof, by using a random value.
                      So to randomly create 3d roof shapes, just supply the "Construct Domain" to the randomRange_ input. For example, input the "Construct Domain" component by using "20" and "30" as its starting and ending domain values.
                      The shape of the random roof will depend on the value defined in "roofType_" input.
                      If "roofType_" = 0, then this input would threat the values as height in Rhino document units.
                      If "roofType_" = 1, then this input would threat the values as degrees.
                      -
                      If nothing supplied, no random 3d roofs will be applied.
                      -
                      Domain in degrees or Rhino document units (meters, feets...).
        roofType_: There are two roof geometric types:
                   0 - flat, parapet wall
                   1 - pitched, hipped roof
                   -
                   If nothing supplied, the default type 1 type (pitched, hipped roof) will be used.
                   -
                   Integer.
        bakeIt_: Set to "True" to bake the 3d roof geometry into the Rhino scene.
                 The geometry will be grouped. To ungroup it, select it and call the "Ungroup" Rhino command.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        threeDeeRoof: Generated 3d roofs from the inputted "_threeDeeRoof".
                      -
                      This output is experimental! In some cases the pitched roof may fail to be created, or it may create an invalid roof geometry!
        threeDeeRoofKeys: A list of keys. This output is the same as "keys" output of "OSM 3D" component.
        threeDeeRoofValues: Values corresponding to each shape in "threeDeeRoof" output.
        angleOrHeight: The angle or height of each 3d roof from the "threeDeeRoof" output.
                       -
                       In Rhino document units (meters, feets...) or degrees.
"""

ghenv.Component.Name = "Gismo_OSM 3D Roof"
ghenv.Component.NickName = "OSM3Droof"
ghenv.Component.Message = "VER 0.0.3\nMAY_05_2021"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

from System.Collections.Generic import List
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import random
import Rhino
import math
import clr
import os
import gc


def straightSkeletonDll_check():
    """
    check if StraightSkeletonNet.dll file is present and unblocked
    """
    
    # check if there is a "MapWinGIS" folder present in some well known places
    straightSkeleton_dll_folderPathLL = [
    "c:\\gismo\\libraries"]
    
    straightSkeleton_dll_fileName = "StraightSkeletonNet.dll"
    
    straightSkeletonDll_present = False
    for straightSkeleton_dll_folderPath in straightSkeleton_dll_folderPathLL:
        straightSkeleton_dll_filePath = os.path.join(straightSkeleton_dll_folderPath, straightSkeleton_dll_fileName)
        straightSkeletonDll_present = os.path.isfile(straightSkeleton_dll_filePath)
        if straightSkeletonDll_present != False:
            # "StraightSkeletonNet.dll" file found in some folder folder
            break
    else:
        # "StraightSkeletonNet.dll" file was NOT found in the "straightSkeleton_dll_folderPathLL" folders
        printMsg = "This component requires the \"StraightSkeletonNet.dll\" library in order to work.\n" + \
                   "The component could not find this file in its expected location:\n" + \
                   "c:\\gismo\\libraries\n" + \
                   " \n" + \
                   "1) Download the \"StraightSkeletonNet.dll\" file from the following link:\n" + \
                   "https://github.com/stgeorges/gismo/blob/master/resources/libraries/StraightSkeletonNet.dll?raw=true\n\n" + \
                   "2) Once the .dll file is downloadeded, check if it has been blocked: right click on it, and choose \"Properties\". If there is an \"Unblock\" button click on it, and then click on \"OK\". If there is no \"Unblock\" button, just click on \"OK\".\n" + \
                   "3) Create the following folder (if not created):\n" + \
                   "c:\\gismo\\libraries\n" + \
                   "4) Copy the upper .dll to this folder.\n" + \
                   "5) Rerun this .gh file (Solution->Recompute)."
        
        straightSkeleton_dll_folderPath = None
        validInputData = False
        return straightSkeleton_dll_folderPath, validInputData, printMsg
    
    
    try:
        clr.AddReferenceToFileAndPath(straightSkeleton_dll_filePath)
    except:
        pass
    
    straightSkeleton_dll_loaded_Success = "StraightSkeletonNet" in [assembly.GetName().Name for assembly in clr.References]
    
    
    if (straightSkeleton_dll_loaded_Success == False):
        # StraightSkeletonNet.dll file is in one of "straightSkeleton_dll_folderPathLL" folders, but it is blocked. It needs to be unblocked
        validInputData = False
        printMsg = "\"StraightSkeletonNet.dll\" file is blocked.\n" + \
                   "1) Go to the following folder: %s\n" % straightSkeleton_dll_folderPath + \
                   "2) Right click on the \"StraightSkeletonNet.dll\" file, and choose \"Properties\". Click on \"Unblock\" button, and then click on \"OK\".\n" + \
                   "3) Close Grasshopper and Rhino. And Run them again."
        
        straightSkeleton_dll_folderPath = None
        
        return straightSkeleton_dll_folderPath, validInputData, printMsg
    
    
    if (straightSkeleton_dll_loaded_Success == True):
        try:
            global StraightSkeletonNet
            import StraightSkeletonNet
            # test
            ssVec_dummy = StraightSkeletonNet.Primitives.Vector2d(0, 10)
            
            validInputData = True
            printMsg = "ok"
            
            return straightSkeleton_dll_folderPath, validInputData, printMsg
            
        except Exception, e:
            straightSkeleton_dll_folderPath = None
            validInputData = False
            printMsg = "The following error has been raised:\n" + \
                       "%s\n" % e + \
                       " \n \n" + \
                       "Post a question about this issue, along with a screenshot and attached .gh file at:\n" + \
                       "http://www.grasshopper3d.com/group/gismo/forum\n"
            
            return straightSkeleton_dll_folderPath, validInputData, printMsg


def checkInputData(threeDeeShapes, threeDeeKeys, threeDeeValues, randomRange, roofType):
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    
    # check inputs
    if (threeDeeShapes.DataCount == 0):
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "Please connect the \"threeDeeShapes\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeShapes\" input."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    elif (len(threeDeeShapes.Branches) == 1) and (threeDeeShapes.Branches[0][0] == None):
        # this happens when "OSM 3D" component's "_runIt" input is set to "False"
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_threeDeeShapes\" input.\n" + \
                   " \n" + \
                   "Please connect the \"threeDeeShapes\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeShapes\" input.\n" + \
                   "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    if (len(threeDeeKeys) == 0):
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "Please connect the \"threeDeeKeys\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeKeys\" input."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    elif (len(threeDeeKeys) == 1) and (threeDeeKeys[0] == None):
        # this happens when "OSM 3D" component's "_runIt" input is set to "False"
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_threeDeeKeys\" input.\n" + \
                   " \n" + \
                   "Please connect the \"threeDeeKeys\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeKeys\" input.\n" + \
                   "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    if (threeDeeValues.DataCount == 0):
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "Please connect the \"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeValues\" input."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    elif (len(threeDeeValues.Branches) == 1) and (threeDeeValues.Branches[0][0] == None):
        # this happens when "OSM 3D" component's "_runIt" input is set to "False"
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "There is no data supplied to the \"_threeDeeValues\" input.\n" + \
                   " \n" + \
                   "Please connect the \"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeValues\" input.\n" + \
                   "And make sure that you set the \"OSM 3D\" \"_runIt\" input to \"True\"."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    if len(threeDeeShapes.Paths) != len(threeDeeValues.Paths):
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "The number of tree branches inputted to the \"_threeDeeShapes\" and \"_threeDeeValues\" inputs do not match.\n" + \
                   " \n" + \
                   "Make sure that you connected:\n" + \
                   "\"threeDeeKeys\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeKeys\" input. And:\n" + \
                   "\"threeDeeValues\" output from Gismo \"OSM 3D\" component to this component's \"_threeDeeValues\" input."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    # randomRange_ is always in degrees (if it is angle)
    if (randomRange == None):
        randomRangeStart = randomRangeEnd = None  # dummy values, will not be used
    else:
        # randomRangeStart can be larger than randomRangeEnd, the random.uniform will still generate a random value between those two numbers.
        # randomRangeStart == randomRangeEnd, the a single value will always be generated (equal to randomRangeStart and randomRangeEnd)
        randomRangeStart = randomRange.T0/unitConversionFactor
        randomRangeEnd = randomRange.T1/unitConversionFactor
    
    
    if (roofType == None):
        roofType = 1  # default (pitched, hipped roof)
        roofType_str = "pitchedRoof"
    elif (roofType == 0):
        roofType_str = "flatRoof"
    elif (roofType == 1):
        roofType_str = "pitchedRoof"
    elif (roofType < 0) or (roofType > 1):
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "roofType_ input must can only have one of two values:\n" + \
                   "0 - flat, parapet wall\n" + \
                   "1 - pitched, hipped roof\n" + \
                   " \n" + \
                   "Please supply one of these values."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    # check the "shapeType_" input value set in the "OSM 3D" component.
    # a point (shapeType = 2) can be tagged as "building=yes" as well. Do not use points, nor polylines, just solid buildings (shapeType == 0)
    for shapesL in threeDeeShapes.Branches:
        if (len(shapesL) != 0):
            # if branch is not empty
            if isinstance(shapesL[0], Rhino.Geometry.Brep):  # there will always be only one 3d building per branch
                shapeType = 0
            else:
                shapeType = "1 or 2"  # polylines or points
    if (shapeType == "1 or 2"):
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        validInputData = False
        printMsg = "This component supports only creation of roofs on 3d buildings. So \"shapeType_\" input of \"OSM 3D\" component needs to be set to 0."
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    
    # check if StraightSkeletonNet.dll file is present and unblocked
    straightSkeleton_dll_folderPath, validInputData, printMsg = straightSkeletonDll_check()
    if (validInputData == False):
        randomRange = randomRangeStart = randomRangeEnd = roofType = roofType_str = shapeType = None
        return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    
    del threeDeeShapes; del threeDeeKeys; del threeDeeValues  # delete local variables
    validInputData = True
    printMsg = "ok"
    
    return randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg


def isNumber(string):
    """
    check if a string can be converted to a number
    """
    try:
        number = float(string)
        return True
    except:
        return False


def flatRoof_parapetWall(building_topSrf_brep, _extrusionHeight, unitConversionFactor):
    
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    
    parapetWallThickness_M = 0.25  # 25cm fixed value!
    parapetWallThickness_RhinoUnits = parapetWallThickness_M/unitConversionFactor  
    
    
    # a) extract outer and inner (if existent) loops from 'building_topSrf_brep'
    outerCrvs  = []
    innerCrvsLL = []
    innerCrvsPresent = False
    for loop in building_topSrf_brep.Loops:
        # extract loop as a polyline
        loopCrv = loop.To3dCurve()
        loopPolyline_strongBox = clr.StrongBox[Rhino.Geometry.Polyline]()
        success = loopCrv.TryGetPolyline(loopPolyline_strongBox)
        loopCrv = loopPolyline_strongBox.ToNurbsCurve()
        
        offsetPlane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,1))
        cornerStyle = Rhino.Geometry.CurveOffsetCornerStyle.Sharp
        
        # determine if it is inside or outside loop
        if (loop.LoopType == Rhino.Geometry.BrepLoopType.Outer):
            polylines_offset = Rhino.Geometry.Curve.Offset(loopCrv, offsetPlane, -parapetWallThickness_RhinoUnits, tol, cornerStyle)
            if (polylines_offset == None):
                # offset of the curve failed. This happens when the "parapetWallThickness_RhinoUnits" is larger than the width or height of building's top surface
                return []
            elif (polylines_offset != None):
                # offset successful
                outerCrvs.extend(polylines_offset)
                outerCrvs.extend([loopCrv])
        else:
            polylines_offset = Rhino.Geometry.Curve.Offset(loopCrv, offsetPlane, -parapetWallThickness_RhinoUnits, tol, cornerStyle)
            innerCrvsLL.append( [loopCrv] + list(polylines_offset) )
    
    
    # create bottom srfs of parapet wals
    extrusionVec = Rhino.Geometry.Vector3d(0,0,_extrusionHeight)
    
    parapetWallBase_outerL = Rhino.Geometry.Brep.CreatePlanarBreps(outerCrvs)
    extrusionCrv = Rhino.Geometry.Line(Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Point3d(0,0,_extrusionHeight)).ToNurbsCurve()
    outer3d_parapetWall = parapetWallBase_outerL[0].Faces[0].CreateExtrusion(extrusionCrv, cap=True)
    
    
    inner3d_parapetWallL = []
    if len(innerCrvsLL) > 0:
        # there is an inner loop(s) (hole) for this buildings top srf
        for innerCrvsL in innerCrvsLL:
            parapetWallBase_innerL = Rhino.Geometry.Brep.CreatePlanarBreps(innerCrvsL)[0]
            inner3d_parapetWall = parapetWallBase_innerL.Faces[0].CreateExtrusion(extrusionCrv, cap=True)
            inner3d_parapetWallL.append(inner3d_parapetWall)
    
    return [outer3d_parapetWall] + inner3d_parapetWallL


def convertPolyline_to_polylineControlPts(polyline):
    controlPts = []
    for i in range(polyline.Count):
        pt = polyline.Item[i]
        controlPts.append(pt)
    
    return controlPts


def straightSkeleton_2DroofFaces(building_topSrf_brep):
    # based on: https://discourse.mcneel.com/t/straight-skeleton-implementation/63814/21
    
    brepZ_coord = building_topSrf_brep.Vertices[0].Location.Z  # breps are always planar so Z coordinate of all of them are the same
    
    # a) extract outer and inner (if existent) loops from 'building_topSrf_brep'
    building_topSrf_outerPolylines = []
    building_topSrf_innerPolylines = []
    for loop in building_topSrf_brep.Loops:
        # extract loop as a polyline
        loopCrv = loop.To3dCurve()
        loopPolyline_strongBox = clr.StrongBox[Rhino.Geometry.Polyline]()
        success = loopCrv.TryGetPolyline(loopPolyline_strongBox)
        polylineControlPts = convertPolyline_to_polylineControlPts(loopPolyline_strongBox)
        
        # determine if it is inside or outside loop
        if (loop.LoopType == Rhino.Geometry.BrepLoopType.Outer):
            building_topSrf_outerPolylines.extend(polylineControlPts[:-1])  # "[:-1]" always remove the last pt (equal to starting pt)
        else:
            building_topSrf_innerPolylines.append(polylineControlPts[:-1])  # "[:-1]" always remove the last pt (equal to starting pt)
    
    
    # b) convert outer and inner loops into ssVec 
    ssOuterLoop_VecL = []
    for controlPt in building_topSrf_outerPolylines:
        ssVec1 = StraightSkeletonNet.Primitives.Vector2d(controlPt.X, controlPt.Y)
        ssOuterLoop_VecL.append(ssVec1)
    
    ssInnerLoop_VecLL = List[List[StraightSkeletonNet.Primitives.Vector2d]]()
    for controlPtL in building_topSrf_innerPolylines:
        ssInnerLoop_VecL = List[StraightSkeletonNet.Primitives.Vector2d]()
        for controlPt in controlPtL:
            ssVec2 = StraightSkeletonNet.Primitives.Vector2d(controlPt.X, controlPt.Y)
            ssInnerLoop_VecL.Add(ssVec2)
        ssInnerLoop_VecLL.Add( ssInnerLoop_VecL )
    
    
    # c) create roof face polygons
    ssOuterLoop_VecL_dotNET = List[StraightSkeletonNet.Primitives.Vector2d](ssOuterLoop_VecL)
    ssInnerLoop_VecLL_dotNET = List[List[StraightSkeletonNet.Primitives.Vector2d]](ssInnerLoop_VecLL)
    try:
        sk = StraightSkeletonNet.SkeletonBuilder.Build(ssOuterLoop_VecL_dotNET, ssInnerLoop_VecLL_dotNET)
    except:
        return "sskeleton failed"
    
    
    # d) convert created roof face polygons into rhino polylines
    roof2DFacePolylines = []
    for edgeResult in sk.Edges:
        controlPts = edgeResult.Polygon
        polylinePts = []
        for vector2d in controlPts:
            pt = Rhino.Geometry.Point3d(vector2d.X, vector2d.Y, brepZ_coord)
            polylinePts.append(pt)
        
        # the outer loop polylines are closed. Therefore their first and last points coincide
        if (polylinePts[0].X == polylinePts[-1].X) and (polylinePts[0].X == polylinePts[-1].Y) and (polylinePts[0].X == polylinePts[-1].Z):
            # outer loop polyline
            polyline = Rhino.Geometry.Polyline(polylinePts)
        else:
            # inner loop polyline. they are never closed! Close them
            polyline = Rhino.Geometry.Polyline(polylinePts + [polylinePts[0]])
        
        roof2DFacePolylines.append(polyline)
    
    return roof2DFacePolylines


def checkIfEdgeIs_outer_or_inner(osmShapeCrvs, brepEdge_crv, brepEdge_index):
    """
    straight skeleton .dll for some reason creates closed polylines which are very close to each
    this results in inner brep edges being sometimes threated as naked edges
    This function tries to fix this issue and cull all these inner brep edges - it checks if brepEdge's 
    middlePt coincide's with any of the "osmShapeCrvs" exploded middlePts.
    """
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    
    middle_t1 = (brepEdge_crv.Domain.T0 + brepEdge_crv.Domain.T1)/2
    #global brepEdge_middlePt  # for testing
    brepEdge_middlePt = brepEdge_crv.PointAt(middle_t1)
    
    #global exploded_osmShapeCrvs_middlePt  # for testing
    exploded_osmShapeCrvs_middlePt = []
    for osmShapeCrv in osmShapeCrvs:
        osmShapeCrv_explodedL = osmShapeCrv.DuplicateSegments()  # explode "osmShapeCrv"
        for osmShapeCrv in osmShapeCrv_explodedL:
            middle_t2 = (osmShapeCrv.Domain.T0 + osmShapeCrv.Domain.T1)/2
            osmShapeCrv_middle_pt = osmShapeCrv.PointAt(middle_t2)
            exploded_osmShapeCrvs_middlePt.append(osmShapeCrv_middle_pt)
            
            if brepEdge_middlePt.EpsilonEquals(osmShapeCrv_middle_pt, tol):
                # brepEdge_crv coincides with one of the outer or inner crvs
                return True
    
    else:
        # brepEdge_crv DOES NOT coincide with one of the outer or inner crvs
        return False


def roof3d_straightSkel_polylines(osmShapeCrvs, roof2d_straightSkel_polylines, roofAngleD):
    """
    lift the roof2d_straightSkel_polylines vertices to make "roof3d_straightSkel_polylines"
    """
    
    tol = 0.001  # do not change!!! tolerance set low on purpose! 
    roofAngleR = math.radians(roofAngleD)
    
    brepEdge_planes = []  # for testing
    roof3d_straightSkel_polylineL = []
    
    for sSPolyline_index, sSPolyline in enumerate(roof2d_straightSkel_polylines):
        sSPolylines_exploded = sSPolyline.DuplicateSegments()
        for brepEdge in sSPolylines_exploded:
            brepEdge_index_dummy = 123456789
            if (checkIfEdgeIs_outer_or_inner(osmShapeCrvs, brepEdge, brepEdge_index_dummy) == True):
                brepEdge_vec = brepEdge.PointAtEnd - brepEdge.PointAtStart
                brepEdge_plane = Rhino.Geometry.Plane( brepEdge.PointAtStart, brepEdge_vec, Rhino.Geometry.Vector3d(0,0,1) )
                brepEdge_planes.append( brepEdge_plane )  # for testing
                
                # calculate the distance between polyline roof vertices and the plane. Those that do not lie on the plane, need to be lifted
            
                # in order to recreate the roof polyline (with lifted polyline points) the polyline points need to be sorted (one after the other)
                brepFaceBrep_outterEdge = sSPolyline
                continuityType = 2  # C1 - Continuous first derivative
                brepFace_vertices_sorted = [brepFaceBrep_outterEdge.PointAtStart] + rs.CurveDiscontinuity(brepFaceBrep_outterEdge, continuityType)  # rs.CurveDiscontinuity function never includes the first start point!!
                
                new_brepFace_vertices = []
                for brepFace_vertex in brepFace_vertices_sorted:
                    brepFace_vertex = brepFace_vertex
                    distance = abs( brepEdge_plane.DistanceTo(brepFace_vertex) )  # a distance from a plane can be negative if the point is 'behind' the plane's Z axis
                    #print "distance: ", distance
                    if (distance > tol):  # only vertices which do not lie on the brepEdge
                        brepFace_vertex_Z = math.tan(roofAngleR) * distance
                        new_brepFace_vertex = Rhino.Geometry.Point3d( brepFace_vertex.X, brepFace_vertex.Y, brepFace_vertex.Z + brepFace_vertex_Z)
                    elif (distance <= tol):  # the vertex lies on the brepEdge. Do not change its Z coordinate
                        new_brepFace_vertex = brepFace_vertex
                    
                    new_brepFace_vertices.append(new_brepFace_vertex)
                
                
                roof3d_straightSkel_polyline = Rhino.Geometry.Polyline(new_brepFace_vertices + [new_brepFace_vertices[0]])
                roof3d_straightSkel_polylineL.append( roof3d_straightSkel_polyline )
    
    
    # create planar breps from "roof3d_straightSkel_polylineL"
    tol2 = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    # create planar breps from planar closed polylines
    roof3d_straightSkel_srfL = []
    for polyline in roof3d_straightSkel_polylineL:
        polylineCrv = polyline.ToNurbsCurve()
        if (polylineCrv.IsClosed):
            if (Rhino.RhinoApp.ExeVersion == 5):
                breps = Rhino.Geometry.Brep.CreatePlanarBreps(polylineCrv)
            elif (Rhino.RhinoApp.ExeVersion >= 6):
                breps = Rhino.Geometry.Brep.CreatePlanarBreps(polylineCrv, tol)
            if (breps != None):
                roof3d_straightSkel_srfL.extend(breps)
    
    """
    # join all these breps into a single brep - commented out to save the running time of the entire component
    tol3 = 10  # 10 meters tolerance. Do not change it! (intentionally large in order for JoinBreps to succeed!)
    roof3d_joined = Rhino.Geometry.Brep.JoinBreps(roof3d_straightSkel_srfL, 10)
    """
    return roof3d_straightSkel_srfL


def align_outerEdge_to_Xaxis(building_topSrf_brep):
    
    # extract the outer edge crv from top building srf
    for loop in building_topSrf_brep.Loops:
        # extract loop as a polyline
        loopCrv = loop.To3dCurve()
        loopPolyline_strongBox = clr.StrongBox[Rhino.Geometry.Polyline]()
        success = loopCrv.TryGetPolyline(loopPolyline_strongBox)
        polylineControlPts = convertPolyline_to_polylineControlPts(loopPolyline_strongBox)
        polyline = Rhino.Geometry.Polyline(polylineControlPts)
        
        # determine if it is inside or outside loop
        if (loop.LoopType == Rhino.Geometry.BrepLoopType.Outer):
            building_topSrf_outerPolyline = polyline.ToNurbsCurve()
    
    
    # explode the top outer edge
    explodedCrv_ids = rs.ExplodeCurves(building_topSrf_outerPolyline)
    explodedCrvs = [rs.coercegeometry(id)  for id in explodedCrv_ids]
    
    # find the edge with the longest edge (in order to align the whole outer edge with that edge being parallel to X axis)
    explodedCrvs_Length_Index_LL = []
    for i,explodedCrv in enumerate(explodedCrvs):
        explodedCrvs_Length_Index_LL.append( [explodedCrv.GetLength(), i] )
    explodedCrvs_Length_Index_LL.sort()
    
    longestEdge_index = explodedCrvs_Length_Index_LL[-1][1]
    longestEdge = explodedCrvs[longestEdge_index]
    
    # calculate the angle between longestEdge and X axis
    xVec = Rhino.Geometry.Vector3d(1,0,0)
    
    longestEdge_vec = longestEdge.PointAtEnd - longestEdge.PointAtStart
    xyPlane = Rhino.Geometry.Plane( Rhino.Geometry.Point3d(0,0,0), Rhino.Geometry.Vector3d(0,0,1) )  # include XY plane in vector angle method to result in 0 to 360 angles
    angleR = Rhino.Geometry.Vector3d.VectorAngle(xVec, longestEdge_vec, xyPlane)
    angleD = math.degrees(angleR)
    
    # Rotation(angleRadians: float, rotationAxis: Vector3d, rotationCenter: Point3d) -> Transform
    rotationAxis = Rhino.Geometry.Vector3d(0,0,1)
    rotationCenter = longestEdge.PointAtStart
    alignToXaxis_matrix = Rhino.Geometry.Transform.Rotation(-angleR, rotationAxis, rotationCenter)
    rotate_success = building_topSrf_brep.Transform(alignToXaxis_matrix)
    
    unalignToXaxis_matrix = Rhino.Geometry.Transform.Rotation(angleR, rotationAxis, rotationCenter)
    #rotate_success = building_topSrf_brep.Transform(unalignToXaxis_matrix)
    
    return building_topSrf_brep, unalignToXaxis_matrix


def cut_sticking_rood3d_srf(roof3dL):
    """
    cut all roof3d_srf which abnormally stick out. This functions tries to soften the issues created with straight skeleton's long 2d polylines
    """
    
    # find the average roof Z coordinate
    vertex_ZcoordL = []
    for roof3d_srf in roof3dL:
        vertices = roof3d_srf.Vertices
        for vertex in vertices:
            vertex_Zcoord = vertex.Location.Z
            vertex_ZcoordL.append(vertex_Zcoord)
    
    average_vertex_Zcoord = sum(vertex_ZcoordL)/len(vertex_ZcoordL)
    
    # select only roof3d faces which have the heighest Z coord 3 times larger than the "average_vertex_Zcoord"
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    
    heightFactor = 2  # "2" is set approximatelly.
    
    cutted_rood3d = []
    for roof3d_srf in roof3dL:
        vertices = roof3d_srf.Vertices
        roof3d_heighest_Zcoord = -1000000 # dummy small value
        for vertex in vertices:
            vertex_Zcoord = vertex.Location.Z
            if (vertex_Zcoord > roof3d_heighest_Zcoord):
                roof3d_heighest_Zcoord = vertex_Zcoord
        
        if (heightFactor * average_vertex_Zcoord < roof3d_heighest_Zcoord):
            # CUT the "rood3d_srf"
            
            heightestCorrect_Zcoord_XYplane = Rhino.Geometry.Plane( Rhino.Geometry.Point3d(0,0,average_vertex_Zcoord), Rhino.Geometry.Vector3d(0,0,1)  )
            cutted_roof3d_srfs = roof3d_srf.Trim(heightestCorrect_Zcoord_XYplane, tol)
            cutted_rood3d.extend(cutted_roof3d_srfs)
        elif (heightFactor * average_vertex_Zcoord >= roof3d_heighest_Zcoord):
            # do not cut the "rood3d_srf"
            cutted_rood3d.append(roof3d_srf)
    
    return cutted_rood3d


def createThreeDeeRoofs(threeDeeShapes_dataTree, threeDeeKeys, threeDeeValues_dataTree, randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, unitConversionFactor):
    
    
    roofAngleD = None  # initial dummy value
    roofShape_and_roofAngle_values_present = False  # initial dummy value
    
    threeDeeShapesLL = threeDeeShapes_dataTree.Branches
    threeDeeValuesLL = threeDeeValues_dataTree.Branches
    threeDeeShapes_Paths = threeDeeShapes_dataTree.Paths
    
    # initialize output data trees
    threeDeeRoof_dataTree = Grasshopper.DataTree[object]()
    threeDeeRoofValues_dataTree = Grasshopper.DataTree[object]()
    height_dataTree = Grasshopper.DataTree[object]()
    
    
    building_keyIndex = None
    buildingPart_keyIndex = None
    buildingLevels_keyIndex = None
    
    for keyIndex,key in enumerate(threeDeeKeys):
        if (key == "roof:shape"):  # "roof_shape"
            roofShape_keyIndex = keyIndex
        elif (key == "roof:angle"):  # "roof_angle"
            roofAngle_keyIndex = keyIndex
        
        elif (key == "building"):
            building_keyIndex = keyIndex
        elif (key == "building:part"):  # "building_p"
            buildingPart_keyIndex = keyIndex
        elif (key == "building:levels"):  # "building_l"
            buildingLevels_keyIndex = keyIndex
        elif (key == "building:min_level"): # "building_m"
            buildingMinLevel_keyIndex = keyIndex
    
    valueRoofShape = ""  # dummy value in case "roof:shape" key does not exist
    valueRoofAngle = ""  # dummy value in case "roof:angle" key does not exist
    valueBuilding = ""  # dummy value in case "building" key does not exist
    valueBuildingPart = ""  # dummy value in case "building:part" key does not exist
    valueBuildingLevels = ""  # dummy value in case "building:levels" key does not exist
    valueBuildingMinLevel = ""  # dummy value in case "building:levels" key does not exist
    
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    for branchIndex,shapesL in enumerate(threeDeeShapesLL):
        if len(shapesL) != 0:  # some shape may have been removed with the "OSM ids" component
            valueRoofShape = threeDeeValuesLL[branchIndex][roofShape_keyIndex]
            valueRoofAngle = threeDeeValuesLL[branchIndex][roofAngle_keyIndex]
            valueBuilding = threeDeeValuesLL[branchIndex][building_keyIndex]
            valueBuildingPart = threeDeeValuesLL[branchIndex][buildingPart_keyIndex]
            valueBuildingLevels = threeDeeValuesLL[branchIndex][buildingLevels_keyIndex]
            valueBuildingMinLevel = threeDeeValuesLL[branchIndex][buildingMinLevel_keyIndex]
            
            threeDeeShapes_Path = threeDeeShapes_Paths[branchIndex]
            
            # first check if there are "roof:shape=hipped" roofs containing information about their angle ("roof:angle='some number')
            if ((valueRoofShape == "hipped") and (isNumber(valueRoofAngle) == True)):
                roofShape_and_roofAngle_values_present = True
                roofAngleD = float(valueRoofAngle)
            
            # at least one values of the four keys ("building", "building:part", "building:levels") is valid (not equal to <empty>). So that "shapesL:" belongs to a building. Put a roof on it
            if (randomRange != None)   and   ((valueBuilding != "") or (valueBuildingPart != "") or (valueBuildingLevels != "") or (valueBuildingMinLevel != "")):
                roofShape_and_roofAngle_values_present = False
                roofAngleD = round(random.uniform(randomRangeStart, randomRangeEnd),2)  # in Rhino document units
            
            if roofAngleD:
                # extract the top face of the building. This is always the first brepFace in the brep (brepFace index: 0)
                building_3d = shapesL[0] # "_threeDeeShapes" input always have a single brep per branch
                building_topSrf_brep = building_3d.Faces[0].DuplicateFace(duplicateMeshes=False)
                shrinkFaces_success = building_topSrf_brep.Faces.ShrinkFaces()
                
                if (roofType == 0):
                    roof3d = flatRoof_parapetWall(building_topSrf_brep, roofAngleD, unitConversionFactor)
                    # add 3d roof values
                    threeDeeRoof_dataTree.AddRange(roof3d, threeDeeShapes_Path)
                    threeDeeRoofValues_dataTree.AddRange(threeDeeValuesLL[branchIndex], threeDeeShapes_Path)
                    height_dataTree.AddRange([roofAngleD], threeDeeShapes_Path)
                
                elif (roofType == 1):
                    
                    # 1) scale up the initial brep to avoid straight skeleten failing
                    duplicate = building_topSrf_brep.DuplicateBrep()
                    vertices = building_topSrf_brep.DuplicateVertices()
                    vector = Rhino.Geometry.Vector3d(Rhino.Geometry.BoundingBox(vertices).Center)
                    
                    translateFromOrigin = Rhino.Geometry.Transform.Translation(vector)
                    vector.Reverse()
                    translateToOrigin = Rhino.Geometry.Transform.Translation(vector)
                    
                    duplicate.Transform(translateToOrigin)
                    
                    duplicate, unalignToXaxis_matrix = align_outerEdge_to_Xaxis(duplicate)  # aligned duplicate
                    
                    scaleFactor = 1e4  # large scale number
                    origin_0_0_0 = Rhino.Geometry.Point3d(0,0,0)
                    scaleUp = Rhino.Geometry.Transform.Scale(origin_0_0_0, scaleFactor)
                    scaleDown = Rhino.Geometry.Transform.Scale(origin_0_0_0, 1/scaleFactor)
                    duplicate.Transform(scaleUp)
                    
                    
                    # try to create roof face polylines
                    roof2d_straightSkel_polylines = straightSkeleton_2DroofFaces(duplicate)
                    if (roof2d_straightSkel_polylines != "sskeleton failed"):
                        print "_Straight Skeleton first success %s" % threeDeeShapes_Path
                        # straight skeleton succeeded
                        for polyline in roof2d_straightSkel_polylines:
                            #polyline_rhino_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddPolyline(polyline)  # for testing
                            polyline.Transform(scaleDown)
                            polyline.Transform(unalignToXaxis_matrix)
                            polyline.Transform(translateFromOrigin)
                            pass
                    
                    elif (roof2d_straightSkel_polylines == "sskeleton failed"):
                        # 2) straight skeleton failed the first time. move the brep slightly and try again
                        print "_Straight Skeleton first Fail %s" % threeDeeShapes_Path
                        for i in range(100):
                            duplicate2 = building_topSrf_brep.DuplicateBrep()
                            randomMove_vec = Rhino.Geometry.Vector3d(random.randint(-100,100), random.randint(-100,100), 0)
                            #randomMove_vec = Rhino.Geometry.Vector3d(random.randint(0,10), random.randint(0,10), 0)
                            randomMoveMatrix = Rhino.Geometry.Transform.Translation(randomMove_vec)
                            duplicate2.Transform(translateToOrigin)
                            duplicate2.Transform(randomMoveMatrix)
                            roof2d_straightSkel_polylines = straightSkeleton_2DroofFaces(duplicate2)
                            
                            if (roof2d_straightSkel_polylines != "sskeleton failed"):
                                print "_Straight Skeleton second Fail %s" % threeDeeShapes_Path
                                randomMove_vec.Reverse()
                                revertMatrix = Rhino.Geometry.Transform.Translation(randomMove_vec)
                                
                                for polyline in roof2d_straightSkel_polylines:
                                    polyline.Transform(translateFromOrigin)
                                    polyline.Transform(revertMatrix)
                                
                                print "_last success RANDOM index: ", i
                                break
                            
                            elif (roof2d_straightSkel_polylines == "sskeleton failed"):
                                # 3) straight skeleton failed again. do another moving of the original brep, and try again
                                continue
                        print "last Fail random index: ", i
                    
                    
                    print "------------"
                    # convert "roof2d_straightSkel_polylines" to roof3d
                    if (roof2d_straightSkel_polylines == "sskeleton failed"):
                        # "sskeleton failed after all upper tries (scalling and moving)
                        cutted_rood3d = []
                    elif (roof2d_straightSkel_polylines != "sskeleton failed"):
                        # create roof3d faces from initial "roof2d_straightSkel_polylines"
                        # get the outer and inner crvs of the "building_topSrf_brep". They will be used to determine which parts of the "roof2d_straightSkel_polylines" lie on these outer edges (these parts will not be lifted)
                        building_topSrf_outer_and_inner_crvs_exploded = building_topSrf_brep.DuplicateEdgeCurves(nakedOnly=True)
                        building_topSrf_outer_and_inner_crvs_joined = Rhino.Geometry.Curve.JoinCurves(building_topSrf_outer_and_inner_crvs_exploded, tol)
                        
                        # convert polylines to crvs
                        roof2d_straightSkel_crvs = [polyline.ToNurbsCurve()  for polyline in roof2d_straightSkel_polylines]
                        roof3d = roof3d_straightSkel_polylines(building_topSrf_outer_and_inner_crvs_joined, roof2d_straightSkel_crvs, roofAngleD)
                        cutted_rood3d = cut_sticking_rood3d_srf(roof3d)
                    
                    
                    # add 3d roof values
                    threeDeeRoof_dataTree.AddRange(cutted_rood3d, threeDeeShapes_Path)
                    threeDeeRoofValues_dataTree.AddRange(threeDeeValuesLL[branchIndex], threeDeeShapes_Path)
                    height_dataTree.AddRange([roofAngleD], threeDeeShapes_Path)
                
            else:
                # shapesL[0] does not contain a valid "building" value
                pass
    
    del threeDeeShapesLL
    del threeDeeValuesLL
    valid_keysAndValues = True  # initial value
    printMsg = "ok"
    
    
    # check if at least one 3d roof has been created
    if (threeDeeRoof_dataTree.DataCount == 0):
        if (roofShape_and_roofAngle_values_present == False):
            valid_keysAndValues = False
            printMsg = "Supplied _threeDeeValues and _threeDeeKeys do not contain neither \"roof:shape\" nor \"roof:angle\" keys which are essential for creation of 3d roofs.\n" + \
                       " \n" + \
                       "You can allow the component to create them with random roof angles with the use of \"randomRange_\" input. Supply some domain to this input (for example: \"20 to 30\") to generate the 3d pitched roof shapes with random angles from 20 to 30 degrees."
        
        elif (roofShape_and_roofAngle_values_present == True):
            valid_keysAndValues = False
            printMsg = "No 3D roof could be created for the given _threeDeeKeys and _threeDeeValues.\n\n" + \
                       "These can be due to the following few reasons:\n" + \
                       "-\n" + \
                       "1) The simplest one: there really isn't any building at that \"_location\" and for that \"_radius\".\n" + \
                       "-\n" + \
                       "2) You might be searching in incorrect \"shapeType_\" input.\n" + \
                       "This component requires the \"shapeType_\" input of the \"OSM 3D\" component to always be set to 0, in order to create 3d building, and therefor 3d roofs for them."
    
    
    # baking
    if bakeIt_:
        layerName = roofType_str + "_" + "randomRange=" + str(randomRangeStart) + "-" + str(randomRangeEnd)
        
        layParentName = "GISMO"; laySubName = "OSM"; layerCategoryName = "3D_ROOF"
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # OSM green (do not change)
        layerColor = System.Drawing.Color.FromArgb(255,58,58)  # red
        
        layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor) 
        
        threeDeeShapesFlattened = [shape  for threeDeeShapeL in threeDeeRoof_dataTree.Branches  for shape in threeDeeShapeL]
        geometryIds = gismo_preparation.bakeGeometry(threeDeeShapesFlattened, layerIndex)
        
        # grouping
        groupIndex = gismo_preparation.groupGeometry("3D_OSM_ROOF" + "_" + layerName, geometryIds)
        del threeDeeShapesFlattened
        del geometryIds
    
    
    # deleting
    del threeDeeShapes_dataTree; del threeDeeKeys; del threeDeeValues_dataTree  # delete local variables
    gc.collect()
    
    
    
    return threeDeeRoof_dataTree, threeDeeRoofValues_dataTree, height_dataTree, valid_keysAndValues, printMsg


def printOutput(randomRangeStart, randomRangeEnd, roofType):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    
    resultsCompletedMsg = "OSM 3D Roof component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Random height range (rhino doc. units): %s - %s
Tree geometry type: %s
    """ % (randomRangeStart, randomRangeEnd, roofType)
    print resultsCompletedMsg
    print printOutputMsg



level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
level_remark = Grasshopper.Kernel.GH_RuntimeMessageLevel.Remark
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, shapeType, unitConversionFactor, validInputData, printMsg = checkInputData(_threeDeeShapes, _threeDeeKeys, _threeDeeValues, randomRange_, roofType_)
        if validInputData:
            if _runIt:
                if (rs.UnitSystem() == 4):
                    threeDeeRoof, threeDeeRoofValues, angleOrHeight, valid_keysAndValues, printMsg = createThreeDeeRoofs(_threeDeeShapes, _threeDeeKeys, _threeDeeValues, randomRange, randomRangeStart, randomRangeEnd, roofType, roofType_str, unitConversionFactor)
                    if valid_keysAndValues:
                        #printOutput(randomRangeStart, randomRangeEnd, roofType)
                        threeDeeRoofKeys = _threeDeeKeys
                    else:
                        print printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
                else:
                    printMsg = "This is the only Gismo component which may experience issues if pitched 3d roof is not created in Meter units.\n" + \
                               "Set your Rhino units to \"Meters\", rerun this component, then bake the results and copy paste them into the Rhino file with your desired units. The roof geometry will be automatically scalled."
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the OSM 3D Roof component"
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
