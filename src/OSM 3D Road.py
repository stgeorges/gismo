# OSM 3D Road
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
Use this component to create 3d roads geometry.
If terrain is used then 3d roads are created for the purpose of visualization. They do not represent the actual terrains roadfilled roads!
-
If you notice some inconsistency in the final 3d road geometry, lower the value of Rhino's tolerance (Tools->Options->Units->Absolute tolerance). Then rerun the grasshopper definition (Solution->Recompute).
-
Provided by Gismo 0.0.3
    
    input:
        _shapes: Plug in the road polylines from the Gismo 'OSM shapes' component's "shapes" output ("shapeType_" input set to 1). You can also add data from "foundShapes" output of the "OSM Search" component."
        roadWidth_: The width of all polylines added to the upper "_shapes" input.
                    -
                    If nothing supplied, the default value of 3 meters (approx. 10 feets) per level will be used.
                    -
                    In Rhino document units (meters, feets...).
        roadThickness_: Height for which road surface will be extruded from the ground.
                        -
                        Positive road thickness value will extrude the road upwards.
                        Negative road thickness value will extrude road downwards.
                        -
                        If nothing supplied, the default value of 0.25 meters (approx. 0.8 feets) per level will be used.
                        -
                        In Rhino document units (meters, feets...).
        groundTerrain_: The ground terrain surface on which the "threeDeeRoads" will be laid onto.
                        Supply it by using "terrain" output of the Ladybug "Terrain Generator" (type_ = 1) or Gismo "Terrain Generator" (type_ = 2 or type_ = 3) components.
                        -
                        ATTENTION!!! Depening on the number of road polylines added to the _shapes input, calculation time may be a bit longer when using terrain.
                        -
                        If nothing supplied, the "threeDeeRoads" will always be laid flat onto a horizontal plane corresponding to the plane of the "_shapes" polylines.
        bakeIt_: Set to "True" to bake the "threeDeeRoads" geometry into the Rhino scene.
                 The geometry will be grouped. To ungroup it, select it and call the "Ungroup" Rhino command.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        threeDeeRoads:  Generated 3d shapes roads from the inputted "_shapes".
                        -
                        If you notice some inconsistency in 3d road geometry, lower the value Rhino's tolerance (Tools->Options->Units->Absolute tolerance). Then rerun the grasshopper definition (Solution->Recompute).
"""

ghenv.Component.Name = "Gismo_OSM 3D Road"
ghenv.Component.NickName = "OSM3Droad"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
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
import Rhino
import math
import time
import clr
import gc
import os


def clipperDll_check():
    """
    check if Clipper.dll file is present and unblocked
    """
    
    # check if there is a "MapWinGIS" folder present in some well known places
    clipper_dll_folderPathLL = [
    "c:\\gismo\\libraries"]
    #"%appdata%\\Grasshopper\\UserObjects"]
    
    clipper_dll_fileName = "Clipper.dll"
    
    clipperDll_present = False
    for clipper_dll_folderPath in clipper_dll_folderPathLL:
        clipper_dll_filePath = os.path.join(clipper_dll_folderPath, clipper_dll_fileName)
        clipperDll_present = os.path.isfile(clipper_dll_filePath)
        if clipperDll_present != False:
            # "Clipper.dll" file found in some folder folder
            break
    else:
        # "Clipper.dll" file was NOT found in the "clipper_dll_folderPathLL" folders
        printMsg = "This component requires the \"Clipper.dll\" library in order to work.\n" + \
                   "The component could not find this file in its expected location:\n" + \
                   "c:\\gismo\\libraries\n" + \
                   " \n" + \
                   "1) Download the \"Clipper.dll\" file from the following link:\n" + \
                   "https://github.com/stgeorges/gismo/blob/master/resources/libraries/Clipper.dll?raw=true\n\n" + \
                   "2) Once the .dll file is downloadeded, check if it has been blocked: right click on it, and choose \"Properties\". If there is an \"Unblock\" button click on it, and then click on \"OK\". If there is no \"Unblock\" button, just click on \"OK\".\n" + \
                   "3) Create the following folder (if not created):\n" + \
                   "c:\\gismo\\libraries\n" + \
                   "4) Copy the upper .dll to this folder.\n" + \
                   "5) Rerun this .gh file (Solution->Recompute)."
        
        clipper_dll_folderPath = None
        validInputData = False
        return clipper_dll_folderPath, validInputData, printMsg
    
    
    try:
        clr.AddReferenceToFileAndPath(clipper_dll_filePath)
    except:
        pass
    
    clipper_dll_loaded_Success = "clipper_library" in [assembly.GetName().Name for assembly in clr.References]
    
    
    if (clipper_dll_loaded_Success == False):
        # Clipper.dll file is in one of "clipper_dll_folderPathLL" folders, but it is blocked. It needs to be unblocked
        validInputData = False
        printMsg = "\"Clipper.dll\" file is blocked.\n" + \
                   "1) Go to the following folder: %s\n" % clipper_dll_folderPath + \
                   "2) Right click on the \"Clipper.dll\" file, and choose \"Properties\". Click on \"Unblock\" button, and then click on \"OK\".\n" + \
                   "3) Close Grasshopper and Rhino. And Run them again."
        
        clipper_dll_folderPath = None
        
        return clipper_dll_folderPath, validInputData, printMsg
    
    
    if (clipper_dll_loaded_Success == True):
        try:
            global ClipperLib
            import ClipperLib
            # test
            scale = 1024.0
            intPt_dummy = ClipperLib.IntPoint(0, 10 * scale)
            
            validInputData = True
            printMsg = "ok"
            
            return clipper_dll_folderPath, validInputData, printMsg
            
        except Exception, e:
            clipper_dll_folderPath = None
            validInputData = False
            printMsg = "The following error has been raised:\n" + \
                       "%s\n" % e + \
                       " \n \n" + \
                       "Post a question about this issue, along with a screenshot and attached .gh file at:\n" + \
                       "http://www.grasshopper3d.com/group/gismo/forum\n"
            
            return clipper_dll_folderPath, validInputData, printMsg


def checkInputData(shapes, roadWidth, roadThickness):
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    
    # check inputs
    if (len(shapes) == 0):
        roadWidth = offsetDistance = roadThickness = shapeType = unitConversionFactor = None
        validInputData = False
        printMsg = "Please connect the \"shapes\" output from Gismo \"OSM shapes\" component to this component's \"_shapes\" input.\n" + \
                   "Set the \"shapeType_\" to 1 (polylines).\n\n" + \
                   "You can also add data from \"foundShapes\" output of the \"OSM Search\" component."
        return roadWidth, offsetDistance, roadThickness, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    if (roadWidth == None):
        roadWidth = 3/unitConversionFactor  # 3 meters (10 feet)
    elif (roadWidth <= 0):
        roadWidth = offsetDistance = roadThickness = shapeType = unitConversionFactor = None
        validInputData = False
        printMsg = "roadWidth_ input must be larger than 0.\n" + \
                   "Please supply a value larger than 0."
        return roadWidth, offsetDistance, roadThickness, shapeType, unitConversionFactor, validInputData, printMsg
    
    offsetDistance = roadWidth/2  # clipper offset is half of the road widt in any rhino unit
    
    
    if (roadThickness == None):
        roadThickness = 0.25/unitConversionFactor  # 0.25 meters (0.82 feet)
    
    """
    # check the "shapeType_" input value set in the "OSM 3D" component.
    atLeastOnePolylineIsNotClosed = False
    for shape in shapes:
        # if branch is not empty
        if isinstance(shape, Rhino.Geometry.Curve):  # there will always be only one 3d building per branch
            if (shape.IsClosed == False):  # "all "shapeType_ = 0" from "OSM shapes" need to be closed
                atLeastOnePolylineIsNotClosed = True
                shapeType = 1
                break
    if (atLeastOnePolylineIsNotClosed == False):
        # shapeType_ is 0 or 2 (closed polygons or points)
        roadWidth = offsetDistance = roadThickness = shapeType = unitConversionFactor = None
        validInputData = False
        printMsg = "This component supports only creation of 3d roads from polylines. So \"shapeType_\" input of \"OSM Shapes\" component needs to be set to 1."
        return roadWidth, offsetDistance, roadThickness, shapeType, unitConversionFactor, validInputData, printMsg
    """
    shapeType = 1
    
    
    # check if StraightSkeletonNet.dll file is present and unblocked
    clipper_dll_folderPath, validInputData, printMsg = clipperDll_check()
    if (validInputData == False):
        roadWidth = offsetDistance = roadThickness = shapeType = unitConversionFactor = None
        return roadWidth, offsetDistance, roadThickness, shapeType, unitConversionFactor, validInputData, printMsg
    
    
    
    del shapes
    validInputData = True
    printMsg = "ok"
    
    return roadWidth, offsetDistance, roadThickness, shapeType, unitConversionFactor, validInputData, printMsg


def isNumber(string):
    """
    check if a string can be converted to a number
    """
    try:
        number = float(string)
        return True
    except:
        return False


def convertClosedToOpenCrvs(shapes):
    """
    if a polyline from "_shapes" input is closed, clipper offset will not create an inner polyline offset curve.
    But only the other one. This is why all closed polylines need to be "opened" by cutting a tiny little part of them (between "t" 0.01 and 0.015 - taken for example)
    """
    splittedShapes = []
    for shape in shapes:
        if (shape.IsClosed == False):
            # do not splitt the polyline. It is already splitted
            splittedShapes.append(shape)
        elif (shape.IsClosed == True):
            # set the curve domain from 0 to 1
            domain_0_1 = Rhino.Geometry.Interval(0,1)
            shape.Domain = domain_0_1
            # split the curve from "0.01, 0.015"
            splitteCrvs = shape.Split([0.01, 0.015])
            shape1_length = splitteCrvs[0].GetLength()
            shape2_length = splitteCrvs[1].GetLength()
            
            if shape1_length > shape2_length:
                splittedShapes.append(splitteCrvs[0])
            else:
                splittedShapes.append(splitteCrvs[1])
    
    return splittedShapes


def clipper_offset(crvs, offsetDistance):
    
    # convert crvs to planar clipper paths
    scale = 1024.0
    clipperOffset = ClipperLib.ClipperOffset()
    
    listsWithEachPolylinePtsLL = []
    listsWithEachPolylinePts_dotNET_LL = List[List[ClipperLib.IntPoint]]()
    for crv in crvs:
        convertSuccess, polyline = crv.TryGetPolyline()
        if convertSuccess and polyline:
            polylinePts = list(polyline)
            gotPlaneSuccess, crvPlane = crv.TryGetPlane()
            if (crvPlane.ZAxis == Rhino.Geometry.Vector3d(0,0,-1)):
                # polyline pts are Clockwise
                polylinePts.reverse()
            elif (crvPlane.ZAxis == Rhino.Geometry.Vector3d(0,0,1)):
                # polyline pts are Counter-Clockwise
                pass
            polylineIntPts = [ClipperLib.IntPoint(pt.X * scale, pt.Y * scale)  for pt in polylinePts]
            eachPolylinePts_dotNET_L = List[ClipperLib.IntPoint](polylineIntPts)
            listsWithEachPolylinePts_dotNET_LL.Add(eachPolylinePts_dotNET_L)
            joinType = ClipperLib.JoinType.jtSquare
            if crv.IsClosed:
                endType = ClipperLib.EndType.etClosedPolygon
            else:
                endType = ClipperLib.EndType.etOpenRound
            clipperOffset.AddPath(eachPolylinePts_dotNET_L, joinType, endType)
    
    
    # perform clipper offset
    pts = []
    clipperOffsettedPolylines = []
    
    listsWithEachOffsettedPolylinePtsLL = []
    listsWithEachOffsettedPolylinePts_dotNET_LL = List[List[ClipperLib.IntPoint]](listsWithEachOffsettedPolylinePtsLL)
    clipperOffset.Execute(listsWithEachOffsettedPolylinePts_dotNET_LL, offsetDistance * scale)
    
    # convert results into rhino polylines
    for subList in list(listsWithEachOffsettedPolylinePts_dotNET_LL):
        intPts_perPolyline = []
        for intPt in subList:
            pt = Rhino.Geometry.Point3d(float(intPt.X)/scale, float(intPt.Y)/scale, 0)
            pts.append(pt)
            intPts_perPolyline.append(pt)
        polyline = Rhino.Geometry.Polyline(intPts_perPolyline + [intPts_perPolyline[0]])
        clipperOffsettedPolylines.append(polyline)
    
    return clipperOffsettedPolylines


def moveCrvSeam_to_middleOfTheLongestEdge(polyline):
    
    # duplicate the polyline
    crv_duplicate = polyline.ToNurbsCurve().Duplicate()
    
    explodedCrvs = polyline.ToNurbsCurve().DuplicateSegments()  # rs.ExplodeCurves
    
    explodedCrvs_lengthIndex_LL = []
    for i,crv in enumerate(explodedCrvs):
        length = polyline.Length
        explodedCrvs_lengthIndex_LL.append( [length, i] )
    explodedCrvs_lengthIndex_LL.sort()
    
    longestEdge_index = explodedCrvs_lengthIndex_LL[-1][1]
    longestEdge = explodedCrvs[longestEdge_index]
    
    longestEdge_middle_t = (longestEdge.Domain.T0 + longestEdge.Domain.T1)/2
    longestEdge_middlePt = longestEdge.PointAt(longestEdge_middle_t)
    
    success_closestT, seam_t = crv_duplicate.ClosestPoint(longestEdge_middlePt)
    
    success_changeSeam = crv_duplicate.ChangeClosedCurveSeam(seam_t)
    
    return crv_duplicate


def removeSelfOverlappingParts_fromCrv(crv):
    """
    clipper library for some reason creates sometimes creates self overlapping corners
    this function tries to remove those parts from the crv
    """
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    
    intersectEvents = Rhino.Geometry.Intersect.Intersection.CurveSelf(crv, tol)
    if (intersectEvents.Count == 0):
        # there are NO self overlapping parts
        return [crv]
    
    elif (intersectEvents.Count > 0):
        # there ARE self overlapping parts
        
        interesection_tL = []
        if intersectEvents:
            events = []
            for i in xrange(intersectEvents.Count):
                overlapA_t = intersectEvents[i].OverlapA
                overlapB_t = intersectEvents[i].OverlapB
                #print "overlapA_t[0]: ", overlapA_t[0]
                #print "overlapA_t[0]: ", overlapA_t[0]
                interesection_tL.append(overlapA_t[0])
                interesection_tL.append(overlapB_t[0])
    
    
    splittedCrvs = crv.Split(interesection_tL)  # split the crv at the locations where it intersects itself
    
    crv_withoutOverlappingPartsL = []
    if ((crv.IsClosed == True) and (len(splittedCrvs) > 2))  or  (crv.IsClosed == False):
        # case when initial polyline is closed and has more than one overlapping part,  or the initial polyline is closed (and has what ever number of overlapping parts)
        for splittedCrv in splittedCrvs:
            if splittedCrv.IsClosed:
                # this curve is the overlapping part (overlapping parts are always closed - unless the starting "crv" has a starting pt at the overlapping parts intersection pt), ingore her.
                pass
            else:
                crv_withoutOverlappingPartsL.append(splittedCrv)
        crv_withoutOverlappingParts = Rhino.Geometry.Curve.JoinCurves(crv_withoutOverlappingPartsL, tol)
    
    
    elif ((crv.IsClosed == True) and (len(splittedCrvs) == 2)):
        # case when initial polyline is closed, but only has one overlapping part
        for splittedCrv in splittedCrvs:
            if splittedCrv.IsClosed:
                crv_withoutOverlappingPartsL.append(splittedCrv)
            else:
                pass
        crv_withoutOverlappingParts = Rhino.Geometry.Curve.JoinCurves(crv_withoutOverlappingPartsL, tol)
    
    return crv_withoutOverlappingParts


def projectPlanarClosedCrvsToTerrain2(planarCrvsL, groundTerrainBrep, groundTerrain_outerEdge_extrusion, bb_height):
    """
    project planar closed curves to a single face brep and make their footprints on terrain
    """
    # get unitConversionFactor
    #gismo_preparation = Preparation()
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    
    
    if (groundTerrainBrep == None):
        planarSrfs = Rhino.Geometry.Brep.CreatePlanarBreps(planarCrvsL)  # returns a list!
        
        validGroundTerrain = True
        printMsg = "ok"
        return planarSrfs, [], validGroundTerrain, printMsg
    
    elif (groundTerrainBrep != None):
        # extract Faces[0] from "groundTerrain_",
        # shrink the upper terrain brepface in case it is not shrinked (for example: the terrain surface inputted to _terrain input is not created by Gismo "Terrain Generator" component)
        groundTerrainBrepFaces = groundTerrainBrep.Faces
        groundTerrainBrepFaces.ShrinkFaces()
        duplicateMeshes = False
        groundBrep_singleBrepFace = groundTerrainBrepFaces[0].DuplicateFace(duplicateMeshes)
        
        tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        # move _roadShapes above so that intersection with groundTerrain_ is fullfiled successfully
        #####liftingOSMshapesHeight = 8848/unitConversionFactor  # "8848" dummy value
        liftingOSMshapesHeight = 260/unitConversionFactor
        #bb_height = 100/unitConversionFactor  # "100" dummy value
        moveMatrix = Rhino.Geometry.Transform.Translation(0,0,liftingOSMshapesHeight)
        for planarOffsetRoadsCrv in planarCrvsL:
            planarOffsetRoadsCrv.Transform(moveMatrix)
        
        extrudedShapeBrepL = []
        srfProjectedOnTerainL = []
        planarBreps = Rhino.Geometry.Brep.CreatePlanarBreps(planarCrvsL)
        for planarBrep in planarBreps:
            shapeStartPt = planarOffsetRoadsCrv.PointAtStart
            extrudePathCurve = Rhino.Geometry.Line(shapeStartPt, Rhino.Geometry.Point3d(shapeStartPt.X, shapeStartPt.Y, shapeStartPt.Z - (liftingOSMshapesHeight+(2 * bb_height)) )).ToNurbsCurve()
            cap = True
            extrudedShapeBrep = planarBrep.Faces[0].CreateExtrusion(extrudePathCurve, cap)
            extrudedShapeBrepL.append(extrudedShapeBrep)
            splittedBreps = Rhino.Geometry.Brep.Split(groundBrep_singleBrepFace, extrudedShapeBrep, tol)
            
            if len(splittedBreps) > 0:
                # the planarOffsetRoadsCrv is inside of groundTerrain_ bounding box (a) or it interesect with it (b)
                # determine which one of these two is the case
                intersectionYes, intersectCrvs, intersectPts = Rhino.Geometry.Intersect.Intersection.BrepBrep(groundTerrain_outerEdge_extrusion, extrudedShapeBrep, tol)
                if (len(intersectCrvs) > 0):
                    #print "terrain edges intersect with road srf"
                    # planarOffsetRoadsCrv planar srf intersects with groundTerrrain_
                    
                    # check the planarOffsetRoadsCrv oriention to determine the brep face index in "splittedBreps"
                    upDirection = Rhino.Geometry.Vector3d(0,0,1)
                    srfProjectedOnTerrain = splittedBreps[len(splittedBreps)-1]  # works!
                    #srfProjectedOnTerrain = splittedBreps[0]
                    #print "len(splittedBreps): ", len(splittedBreps)
                    
                    gotPlane_success, plane = planarOffsetRoadsCrv.TryGetPlane()
                    
                    if (planarOffsetRoadsCrv.ClosedCurveOrientation(upDirection) == Rhino.Geometry.CurveOrientation.Clockwise):
                        srfProjectedOnTerrain = splittedBreps[len(splittedBreps)-1]  # works?
                        #srfProjectedOnTerrain = splittedBreps[0]
                        ####print "clockwise"
                        pass
                    elif (planarOffsetRoadsCrv.ClosedCurveOrientation(upDirection) == Rhino.Geometry.CurveOrientation.CounterClockwise):
                        srfProjectedOnTerrain = splittedBreps[0]
                        ####print "counter clockwise"
                        pass
                    
                    
                    srfProjectedOnTerrain.Faces.ShrinkFaces()  # shrink the cutted srfProjectedOnTerrain
                    srfProjectedOnTerainL.append(srfProjectedOnTerrain)
                    
                elif (len(intersectCrvs) == 0):
                    ####print "terrain edges DO NOT intersect with road srf."
                    # planarOffsetRoadsCrv planar srf is inside groundTerrain_ and does not intersect it
                    srfProjectedOnTerrain = splittedBreps[len(splittedBreps)-1]
                    srfProjectedOnTerrain.Faces.ShrinkFaces()  # shrink the cutted srfProjectedOnTerrain
                    srfProjectedOnTerainL.append(srfProjectedOnTerrain)
            
            else:
                # planarOffsetRoadsCrv is outside of groundTerrain_ bounding box, do not add it to the "srfProjectedOnTerainL" list
                pass
            
            del planarBrep; del extrudePathCurve; del splittedBreps; del extrudedShapeBrepL; extrudedShapeBrepL = []
        
        
        # create a single mesh from all surfaces in the "" list
        if (len(srfProjectedOnTerainL) == 0):
            # the "groundTerrain_" is either too small (has very small radius) or it does not have the same origin as "_roadShapes", meaning the "_roadShapes" can not be projected to "groundBrep_singleBrepFace".
            validGroundTerrain = False
            printMsg = "Something is wrong with your \"groundTerrain_\" input.\n" + \
                       "Make sure that when you look at it in Rhino's \"Top\" view, it covers (encapsulates) the whole \"_roadShapes\" geometry or at least some of its parts."
            
            return srfProjectedOnTerainL, extrudedShapeBrepL, validGroundTerrain, printMsg
        elif (len(srfProjectedOnTerainL) > 0):
            # everything is fine
            validGroundTerrain = True
            printMsg = "ok"
            
            return srfProjectedOnTerainL, extrudedShapeBrepL, validGroundTerrain, printMsg


def createThreeDeeRoads(offsetPolylines_withoutOverlap, groundTerrain, roadWidth, roadThickness):
    
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    
    # get groundBrep_singleBrepFace
    if (groundTerrain != None):
        groundBrep_singleBrepFace = groundTerrain.Faces[0].DuplicateFace(False)  # always use the top face (the actual terrain) in case inputted groundTerrain_ has been created as a polysurface
        accurate = False
        bb_volume, bb_centroid, bb_length, bb_depth, bb_height, bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner = gismo_preparation.boundingBox_properties([groundTerrain], accurate)
    elif (groundTerrain == None):
        #groundBrep_singleBrepFace = None
        pass
    
    if (groundTerrain == None):
        extrusionVec = Rhino.Geometry.Vector3d(0,0,-roadThickness)
    elif(groundTerrain != None):
        shapeExtrudeHeight = roadThickness + 2 * bb_height  # "2" is due to safety
        extrusionVec = Rhino.Geometry.Vector3d(0,0,-shapeExtrudeHeight)
    
    
    
    # create planar breps from offset polylines
    if (Rhino.RhinoApp.Version.Major == 6):
        road_srfs = Rhino.Geometry.Brep.CreatePlanarBreps(offsetPolylines_withoutOverlap, tol)
    elif (Rhino.RhinoApp.Version.Major == 5):
        road_srfs = Rhino.Geometry.Brep.CreatePlanarBreps(offsetPolylines_withoutOverlap)
    
    # extrude roads to 3d
    road_srfs_flipped = []
    for road_brep in road_srfs:
        
        # a) lift the brep road
        if (groundTerrain == None):
            # move the road_brep upwards to accommodate for the extrusion thickness downwards
            moveVec = Rhino.Geometry.Vector3d(0,0,roadThickness)
        elif (groundTerrain != None):
            # move the roads just to be above the terrain. Regardless of the precise position. So that when extruded they cut the terrain
            terrainHeight = bb_topRightCorner.Z - bb_bottomRightCorner.Z
            terrainTopPt_Zcoord = bb_bottomRightCorner.Z + bb_height
            road_brep_Zcoord = road_brep.Vertices[0].Location.Z
            road_brep_Zcoord_desired = terrainTopPt_Zcoord + bb_height/2  # for security reasons we lift the road planar srfs for a half of the terrain height above the terrain's heighest point
            moveVec = Rhino.Geometry.Vector3d(0,0,road_brep_Zcoord_desired) - Rhino.Geometry.Vector3d(0,0,road_brep_Zcoord)
        
        moveMatrix = Rhino.Geometry.Transform.Translation(moveVec)
        road_brep.Transform(moveMatrix)
        
        # b) check the road_brep normal
        road_srf = road_brep.Faces[0]
        middle_u = (road_srf.Domain(0).T0 + road_srf.Domain(0).T1) / 2
        middle_v = (road_srf.Domain(1).T0 + road_srf.Domain(1).T1) / 2
        normal_at_middle_u_v = road_srf.NormalAt( middle_u, middle_v )
        if (normal_at_middle_u_v.Z < 0):
            # for some reason the upper 'road_srfs' normal is pointed downwards
            road_brep.Flip()
        else:
            # normal is upwards. No flipping
            pass
        road_srfs_flipped.append(road_brep)
    
    
    # create 3d roads
    threeDeeRoads = []
    for road_brep in road_srfs_flipped:
        road_brep_vertex = road_brep.Vertices[0].Location  # if topCrvs has more shapes than 1, the others will also be on the same height
        extrudeCrv = Rhino.Geometry.Line(road_brep_vertex, road_brep_vertex + extrusionVec).ToNurbsCurve()
        road_brepFace = road_brep.Faces[0]
        cap = True
        extrudedShape = Rhino.Geometry.BrepFace.CreateExtrusion(road_brepFace, extrudeCrv, cap)
        
        if (groundTerrain == None):
            # nothing inputted into the "groundTerrain_" input
            threeDeeRoads.append(extrudedShape)
        elif (groundTerrain != None):
            # something inputted into the "groundTerrain_" input
            road_brep_edgeCrvs = road_brep.DuplicateEdgeCurves(nakedOnly=False)
            
            # create edge curve extrusion with dummy height (slower version)
            ####groundBrep_singleBrepFace_edgeCrvs = groundBrep_singleBrepFace.DuplicateEdgeCurves(nakedOnly=True)
            ####groundBrep_singleBrepFace_edgeCrvsJoined = Rhino.Geometry.Curve.JoinCurves(groundBrep_singleBrepFace_edgeCrvs, tol)
            
            # create edge curve extrusion with dummy height (faster version)
            terrain_bb_bottomFaceOuterEdgeCrv = Rhino.Geometry.Polyline([bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner, bb_bottomLeftCorner]).ToNurbsCurve()
            extrudeCrv_for_terrainEdge = Rhino.Geometry.Line( bb_bottomLeftCorner, Rhino.Geometry.Point3d(bb_bottomLeftCorner.X, bb_bottomLeftCorner.Y, bb_bottomLeftCorner.Z + bb_height) ).ToNurbsCurve()
            groundTerrain_outerEdge_extrusion = Rhino.Geometry.SumSurface.Create(terrain_bb_bottomFaceOuterEdgeCrv, extrudeCrv_for_terrainEdge).ToBrep()
            #srfProjectedOnTerrainL, extrudedShapeBrepL_notNeeded, validGroundTerrain, printMsg2 = gismo_geometry.projectPlanarClosedCrvsToTerrain(road_brep_edgeCrvs, groundBrep_singleBrepFace, groundTerrain_outerEdge_extrusion)
            srfProjectedOnTerrainL, extrudedShapeBrepL_notNeeded, validGroundTerrain, printMsg2 = projectPlanarClosedCrvsToTerrain2(road_brep_edgeCrvs, groundBrep_singleBrepFace, groundTerrain_outerEdge_extrusion, bb_height)
            del extrudedShapeBrepL_notNeeded
            
            if (validGroundTerrain == False):
                del srfProjectedOnTerrainL
                continue
                """
                threeDeeRoads = validThreeDeeRoadsCreation = None
                return threeDeeRoads, validThreeDeeRoadsCreation, printMsg2
                """
            
            if (validGroundTerrain == True):
                
                # lift the "srfProjectedOnTerrainL" (which represents the surface intersected between the extudedRoad and terrain)
                moveVec = Rhino.Geometry.Vector3d(0,0,roadThickness)
                
                if (roadThickness >= 0):
                    moveVec = Rhino.Geometry.Vector3d(0,0,roadThickness)
                elif (roadThickness < 0):
                    # if "roadThickness" is negative, then do not lift the roads top srf
                    moveVec = Rhino.Geometry.Vector3d(0,0,0)
                
                moveMatrix = Rhino.Geometry.Transform.Translation(moveVec)
                for srf in srfProjectedOnTerrainL:
                    srf.Transform(moveMatrix)
                    threeDeeRoads.append(srf)  # add the road's top srf
                    
                    # extrude its edges downwards (to show the roads "thickness")
                    road_brep_projected_edgeCrvs = srf.DuplicateEdgeCurves(nakedOnly=False)
                    road_brep_projected_edgeCrvs_joined = Rhino.Geometry.Curve.JoinCurves(road_brep_projected_edgeCrvs, tol)
                    extrudeCrv_startPt = road_brep_projected_edgeCrvs_joined[0].PointAtStart  # pick any first pt regardless of its height
                    if (roadThickness >= 0):
                        extrudeCrv_endPt = Rhino.Geometry.Point3d( extrudeCrv_startPt.X, extrudeCrv_startPt.Y, extrudeCrv_startPt.Z - roadThickness)
                    elif (roadThickness < 0):
                        # if "roadThickness" is negative, then extrude the edges downwards
                        extrudeCrv_endPt = Rhino.Geometry.Point3d( extrudeCrv_startPt.X, extrudeCrv_startPt.Y, extrudeCrv_startPt.Z + roadThickness)
                    extrudeCrv = Rhino.Geometry.Line( extrudeCrv_startPt, extrudeCrv_endPt ).ToNurbsCurve()
                    for crv in road_brep_projected_edgeCrvs_joined:
                        road_brep_outerEdge_extrusion = Rhino.Geometry.SumSurface.Create(crv, extrudeCrv).ToBrep() 
                        threeDeeRoads.append(road_brep_outerEdge_extrusion)
    
    
    # baking
    if bakeIt_:
        layerName = "roadWidth=" + str(roadWidth) + "_" + "roadThickness" + str(roadThickness)
        
        layParentName = "GISMO"; laySubName = "OSM"; layerCategoryName = "3D_ROAD"
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(0,0,0)  # black
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor) 
        
        geometryIds = gismo_preparation.bakeGeometry(threeDeeRoads, layerIndex)
        
        # grouping
        groupIndex = gismo_preparation.groupGeometry("3D_OSM_ROAD" + "_" + layerName, geometryIds)
        del geometryIds
    
    
    # deleting
    del road_srfs; del road_srfs_flipped;  # delete local variables
    gc.collect()
    
    validThreeDeeRoadsCreation = True
    printMsg = "ok"
    
    return threeDeeRoads, validThreeDeeRoadsCreation, printMsg


def printOutput(roadWidth, roadThickness):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    
    resultsCompletedMsg = "OSM 3D Road component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Road width (rhino doc. units): %s
Road thickness (rhino doc. units): %s
    """ % (roadWidth, roadThickness)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
level_remark = Grasshopper.Kernel.GH_RuntimeMessageLevel.Remark
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_geometry = sc.sticky["gismo_CreateGeometry"]()
        
        roadWidth, offsetDistance, roadThickness, shapeType, unitConversionFactor, validInputData, printMsg = checkInputData(_shapes, roadWidth_, roadThickness_)
        if validInputData:
            if _runIt:
                splittedShapes = convertClosedToOpenCrvs(_shapes)
                offsetPolylines = clipper_offset(splittedShapes, offsetDistance)  # clipper offseted polylines
                # remove self overlapping parts of the crv created by clipper library:
                offsetPolylines_movedSeam = [moveCrvSeam_to_middleOfTheLongestEdge(polyline)  for polyline in offsetPolylines]
                offsetPolylines_withoutOverlap = []
                for polyline2 in offsetPolylines_movedSeam:
                    cleanedPolyline = removeSelfOverlappingParts_fromCrv(polyline2)
                    offsetPolylines_withoutOverlap.extend(cleanedPolyline)
                # create 3d roads
                threeDeeRoads, validThreeDeeRoadsCreation, printMsg = createThreeDeeRoads(offsetPolylines_withoutOverlap, groundTerrain_, roadWidth, roadThickness)
                if validThreeDeeRoadsCreation:
                    printOutput(roadWidth, roadThickness)
                else:
                    print printMsg
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the OSM 3D Road component"
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
