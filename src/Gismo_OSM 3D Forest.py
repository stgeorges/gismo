# OSM 3D Forest
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
Use this component to create 3d trees geometry on inputed surfaces.
OSM 3D component can create 3d trees. However, there are areas where trees should be located but they do not exist in openstreetmap database, so OSM 3D component will not create them.
These areas are forests for example. You can find a forest area with the use of "OSM Search" component and add its "foundShapes" ouput to this component's "_forestSrfs" input. Or any other surface you wish to add trees to.
-
Provided by Gismo 0.0.3
    
    input:
        _forestSrfs: Plug in surfaces on which trees will be created.
                     For example these can be forest surfaces from "OSM Search" component and add its "foundShapes" ouput.
        treeType_: There are three tree geometric types:
                   0 - round
                   1 - polygonized
                   2 - random shaped
                   -
                   If nothing supplied, the default type 2 type (random) will be used.
                   -
                   Integer.
        randomHeightRange_: Height range in which trees will be created.
                            For example if you add "5 to 10" to this input, the trees' height will be randomly created from 5 to 10 meters.
                            -
                            If nothing supplied, default value of 10 to 15 meters will be used.
                            -
                            Domain in Rhino document units (meters, feets...).
        deciduousOrConiferous_: Leaf type of the tree. The following ones are used:
                                0 - deciduous trees
                                1 - coniferous trees
                                2 - random (either deciduous or coniferous) trees
                                -
                                If nothing supplied, the default 0 (deciduous trees) will be used.
                                -
                                Integer.
        maxNumOfTrees_: Maximal number of trees on the largest surface added to the _forestSrfs
                        -
                        If nothing supplied, the default value of 20 trees will be used.
        randomSeed_: Random seed for the positon of the trees.
                     -
                     If nothing supplied, the default 0 will be used.
                     -
                     Integer
        bakeIt_: Set to "True" to bake the "threeDeeRoads" geometry into the Rhino scene.
                 The geometry will be grouped. To ungroup it, select it and call the "Ungroup" Rhino command.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        threeDeeTrees:  Generated 3d trees on inputted "_forestSrfs".
        threeDeeTreesOrigin: Bottom origin point of each of upper "threeDeeTrees".
                             -
                             Use grasshopper's "Point" parameter to visualize it.
        treeHeight: Height of each of upper "threeDeeTrees".
"""

ghenv.Component.Name = "Gismo_OSM 3D Forest"
ghenv.Component.NickName = "OSM3Dforest"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass


import ghpythonlib.components as ghc
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import random
import System
import Rhino
import gc


def checkInputData(forestSrfs, treeType, randomHeightRange, deciduousOrConiferous_index, maxNumOfTrees):
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    
    # check inputs
    if (len(forestSrfs) == 0):
        treeType = randomHeightRangeStart = randomHeightRangeEnd = deciduousOrConiferous_index = maxNumOfTrees = unitConversionFactor = None
        validInputData = False
        printMsg = "Please input surfaces on which the trees will be generated.\n" + \
                   "For example: you can find forest area with the use of \"OSM Search\" component and add its \"foundShapes\" ouput. Make sure to set the \"OSM Search\" component's \"createFootprints_\" input to \"True\"."
        return treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, unitConversionFactor, validInputData, printMsg
    
    
    if (treeType == None):
        treeType = 2  # default (random)
    elif (treeType < 0) or (treeType > 2):
        treeType = randomHeightRangeStart = randomHeightRangeEnd = deciduousOrConiferous_index = maxNumOfTrees = unitConversionFactor = None
        validInputData = False
        printMsg = "treeType_ input must can only have one of the following values:\n" + \
                   "0 - round tree\n" + \
                   "1 - polygonized tree\n" + \
                   "2 - random shaped tree\n" + \
                   " \n" + \
                   "Please supply one of these values."
        return treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, unitConversionFactor, validInputData, printMsg
    
    
    # randomHeightRange_ is always in Rhino document units
    if (randomHeightRange == None):
        randomHeightRangeStart = 10/unitConversionFactor;  randomHeightRangeEnd = 15/unitConversionFactor  # default 10 to 15 meters
    else:
        # randomHeightRangeStart can be larger than randomHeightRangeEnd, the random.uniform will still generate a random value between those two numbers.
        # randomHeightRangeStart == randomHeightRangeEnd, the a single value will always be generated (equal to randomHeightRangeStart and randomHeightRangeEnd)
        randomHeightRangeStart = randomHeightRange.T0#/unitConversionFactor
        randomHeightRangeEnd = randomHeightRange.T1#/unitConversionFactor
    
    
    if (deciduousOrConiferous_index == None):
        deciduousOrConiferous_index = 0  # default (deciduous)
    elif (deciduousOrConiferous_index < 0) or (deciduousOrConiferous_index > 2):
        treeType = randomHeightRangeStart = randomHeightRangeEnd = deciduousOrConiferous_index = maxNumOfTrees = unitConversionFactor = None
        validInputData = False
        printMsg = "deciduousOrConiferous_index_ input must can only have one of the following values:\n" + \
                   "0 - deciduous trees\n" + \
                   "1 - coniferous trees\n" + \
                   "2 - random (either deciduous or coniferous) trees\n" + \
                   " \n" + \
                   "Please supply one of these values."
        return treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, unitConversionFactor, validInputData, printMsg
    
    
    if (maxNumOfTrees == None):
        maxNumOfTrees = 20  # default
    elif (maxNumOfTrees <= 0):
        treeType = randomHeightRangeStart = randomHeightRangeEnd = deciduousOrConiferous_index = maxNumOfTrees = unitConversionFactor = None
        validInputData = False
        printMsg = "maxNumOfTrees_ input must be larger than 0.\n" + \
                   "Please supply a value larger than 0."
        return treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, unitConversionFactor, validInputData, printMsg
    
    
    
    # check the "shapeType_" input value set in the "OSM 3D" component.
    forestSrfs_inputAreBreps = False
    for srf in forestSrfs:
        # if branch is not empty
        if isinstance(srf, Rhino.Geometry.Brep):  # there will always be only one 3d building per branch
            forestSrfs_inputAreBreps = True
        else:
            forestSrfs_inputAreBreps = False
            break
    
    if (forestSrfs_inputAreBreps == False):
        # at least one of the srf from forestSrfs is not a brep
        treeType = randomHeightRangeStart = randomHeightRangeEnd = deciduousOrConiferous_index = maxNumOfTrees = unitConversionFactor = None
        validInputData = False
        printMsg = "This component requires surfaces as \"_forestSrfs\" input.\n" + \
                    "If you are using \"OSM Search\" component and add its \"foundShapes\" ouput, make sure to set its component's \"createFootprints_\" input to \"True\"."
        return treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, unitConversionFactor, validInputData, printMsg
    
    
    
    del forestSrfs
    validInputData = True
    printMsg = "ok"
    
    return treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, unitConversionFactor, validInputData, printMsg


def createThreeDeeTrees(forestSrfs, treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, randomSeed, unitConversionFactor):
    
    projectionDirection = Rhino.Geometry.Vector3d(0,0,1)  # it can be direction = Rhino.Geometry.Vector3d(0,0,-1) as well, does not matter
    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
    
    # find the largest area
    areas = []
    maximalArea = -1000000000000 # dummy small value
    for i,srf in enumerate(forestSrfs):
        area = Rhino.Geometry.AreaMassProperties.Compute(srf).Area
        if area > maximalArea:
            maximalArea = area
        areas.append(area)
    
    threeDeeTreesDataTree = Grasshopper.DataTree[object]()
    threeDeeTreesOriginDataTree = Grasshopper.DataTree[object]()
    treeHeightDataTree = Grasshopper.DataTree[object]()
    
    
    for i,srf in enumerate(forestSrfs):
        groundTerrain = srf
        
        srf_brepFace = srf.Faces[0]
        middle_u = (srf_brepFace.Domain(0).T0 + srf_brepFace.Domain(0).T1) / 2
        middle_v = (srf_brepFace.Domain(1).T0 + srf_brepFace.Domain(1).T1) / 2
        normal = srf_brepFace.NormalAt(middle_u, middle_v)
        
        if normal.Z >= 0:
            pass
        elif normal.Z < 0:
            srf.Flip()
        
        # get groundBrep_singleBrepFace
        if (groundTerrain != None):
            groundBrep_singleBrepFace = groundTerrain.Faces[0].DuplicateFace(False)  # always use the top face (the actual terrain) in case inputted groundTerrain_ has been created as a polysurface
            accurate = False
            bb_volume, bb_centroid, bb_length, bb_depth, bb_height, bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner = gismo_preparation.boundingBox_properties([groundTerrain], accurate)
        elif (groundTerrain == None):
            groundBrep_singleBrepFace = None
            bb_height = 10  # dummy value
        bb_height = 3000  # dummy large value (until "Ladybug Terrain Generator" starts support "origin_" input to be on the terrain)
        
        numberOfTrees = int( maxNumOfTrees * (areas[i]/maximalArea) )
        if (numberOfTrees < 1): numberOfTrees = 1
        treeBottom_ptL = ghc.PopulateGeometry(srf, numberOfTrees, randomSeed)
        try:
            # if "ghc.PopulateGeometry" returns a single point, it will not be returned in a list!
            treeBottom_ptL.extend([])  # test if "treeBottom_ptL" is a list
        except:
            treeBottom_ptL = [treeBottom_ptL]
        
        path = Grasshopper.Kernel.Data.GH_Path(i)
        threeDeeTreesL = []
        threeDeeTreesOriginL = []
        heightL = []
        for index, treeBottom_pt in enumerate(treeBottom_ptL):
            
            # 1) try creating 3d trees
            height = round(random.uniform(randomHeightRangeStart, randomHeightRangeEnd),2)  # in Rhino document units
            
            if (deciduousOrConiferous_index == 0):
                deciduousOrConiferous = "deciduous"  # by default, if it can not be identified if a tree is deciduous or coniferous always use the deciduous
            elif (deciduousOrConiferous_index == 1):
                deciduousOrConiferous = "coniferous"
            elif (deciduousOrConiferous_index == 2):
                randomIndex = random.randint(0,1)
                deciduousOrConiferous = ["deciduous", "coniferous"][randomIndex]
            
            numOfTreeHorizontalSegments = 6  # this value is fixed, and should not be changed
            
            # heights and radii
            trunkRadius = height/random.uniform(44, 48)  # lower values (than 44,48) can result in "bottomCrown_brep" not being able to be created
            crownRadius = height/random.uniform(2, 5)
            
            trunkHeight = 0.2*height
            crownHeight = height - trunkHeight
            
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
                    global extrudedShapeBrep
                    extrudedShapeBrep = Rhino.Geometry.Surface.CreateExtrusion(trunkTop_crv, extrusionVector).ToBrep()
                    splittedBreps = Rhino.Geometry.Brep.Split(extrudedShapeBrep, groundTerrain, tol)
                    if (len(splittedBreps) == 0):
                        # treeBottom_pt (origin pt projected on groundBrep_singleBrepFace) lies somewhere close to the edge of the ground Terrain
                        continue
                    else:
                        trunkBrep1 = splittedBreps[0]
                        trunkBrep2 = splittedBreps[1]
                        if trunkBrep1.Vertices[0].Location.Z > trunkBrep2.Vertices[0].Location.Z:
                            trunkBrep = trunkBrep1
                        else:
                            trunkBrep = trunkBrep2
                        shrinkSuccess = trunkBrep.Faces.ShrinkFaces()
                        del splittedBreps;
            
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
            threeDeeTreesL.append(treeJoinedBrep)
            threeDeeTreesOriginL.append(projectedTreeBottom_pt)
            heightL.append(height)
        
        
        threeDeeTreesDataTree.AddRange(threeDeeTreesL, path)
        threeDeeTreesOriginDataTree.AddRange(threeDeeTreesOriginL, path)
        treeHeightDataTree.AddRange(heightL, path)
    
    
    # baking
    if bakeIt_:
        layerName = "treeType=" + str(treeType) + "_randomHeightRange=" + str(randomHeightRangeStart) + "-" + str(randomHeightRangeEnd) + "_deciduousOrConiferous=" + str(deciduousOrConiferous_index) + "_maxNumOfTrees=" + str(maxNumOfTrees) + "_randomSeed" + str(randomSeed)
        
        layParentName = "GISMO"; laySubName = "OSM"; layerCategoryName = "3D_FOREST"
        newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # OSM green
        layerColor = System.Drawing.Color.FromArgb(11,156,50)  # tree green
        
        layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor) 
        
        geometryIds = gismo_preparation.bakeGeometry(threeDeeTreesLL, layerIndex)
        
        # grouping
        groupIndex = gismo_preparation.groupGeometry("3D_OSM_FOREST" + "_" + layerName, geometryIds)
        del geometryIds; del threeDeeTreesLL
    
    
    # hide "threeDeeTreesOrigin" output
    ghenv.Component.Params.Output[2].Hidden = True
    
    # deleting
    del forestSrfs;  # delete local variables
    gc.collect()
    
    validThreeDeeRoadsCreation = True
    printMsg = "ok"
    
    return threeDeeTreesDataTree, threeDeeTreesOriginDataTree, treeHeightDataTree


def printOutput(treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, randomSeed):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    
    resultsCompletedMsg = "OSM 3D Forest component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Tree geometry type: %s
Random height range (rhino doc. units): %s - %s
Deciduous or Coniferous: %s
Maximal number of trees: %s
Seed: %s
    """ % (treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, randomSeed)
    print resultsCompletedMsg
    print printOutputMsg



level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
level_remark = Grasshopper.Kernel.GH_RuntimeMessageLevel.Remark
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, unitConversionFactor, validInputData, printMsg = checkInputData(_forestSrfs, treeType_, randomHeightRange_, deciduousOrConiferous_, maxNumOfTrees_)
        if validInputData:
            if _runIt:
                threeDeeTrees, threeDeeTreesOrigin, treeHeight = createThreeDeeTrees(_forestSrfs, treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, randomSeed_, unitConversionFactor)  # clipper offseted polylines
                printOutput(treeType, randomHeightRangeStart, randomHeightRangeEnd, deciduousOrConiferous_index, maxNumOfTrees, randomSeed_)
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the OSM 3D Forest component"
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
