# horizon angles
#
# Gismo is a plugin for GIS Environmental Analysis (GPL) started by Djordje Spasic.
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
Use this component to create a horizon file (.hor) and visualize horizon angles.
-
Component based on:

"Solmetric SunEye 210 User’s Guide", Solmetric Corporation, 2011
http://resources.solmetric.com/get/Solmetric%20SunEye%20200%20Series%20Users%20Guide_en.pdf
"PVsyst 6 Help", PVsyst SA
http://files.pvsyst.com/help/index.html?horizon_import.htm
-
Provided by Gismo 0.0.1
    
    input:
        _location: The output from the "importEPW" or "constructLocation" component.  This is essentially a list of text summarizing a location on the Earth.
                   -
                   "timeZone" and "elevation" data from the location, are not important for this component.
        _analysisGeometry: Input surface(a) or point(b) (a single one or more of them).
                           -
                           a) Input planar Surface (not polysurface) on which the PV modules/Solar water heating collectors will be applied.
                           If you have a polysurface, explode it (using "Deconstruct Brep" component) and then feed its Faces(F) output to _analysisGeometry. Surface normal should be faced towards the sun.
                           -
                           b) You can also supply point(s).
                           For example the "originPt" output from "Terrain shading mask" component.
        _context: Input the "terrainShadingMask" output from "Terrain shading mask" component.
                  You can additionally input other opaque obstacles surrounding your location: houses, buildings etc.
                  Do not input trees, as they are not opaque obstacles and should not be taken into account when analysing the horizon angles.
        north_: Input a vector to be used as a true North direction, or a number between 0 and 360 that represents the clockwise degrees off from the Y-axis.
                -
                If not supplied, default North direction will be set to the Y-axis (0 degrees).
        scale_: Scale of the overall geometry (horizonAnglesRose mesh, compassCrvs, title, legend).
                -
                If not supplied, default value of 1 will be used.
        legendBakePar_: Optional legend bake parameters from the Gismo "Legend Parameters" component.
                        -
                        Use this input to change the color of the "horizonAnglesRose" output, or edit the "legend" and "title" outputs.
        outputGeometryIndex_: An index of the surface or point inputted into "_analysisGeometry" if "_analysisGeometry" would be flattened..
                              It determines the surface or point for which output geometry will be generated.
                              -
                              If not supplied, geometry for the first surface (index: 0) will be generated as a default.
        workingFolder_: Folder path where .hor files will be created (exported)
                        -
                        If not supplied, the following default Gismo folder path will be used: "C:\gismo\horizon_files".
        horizonFileType_: The following .hor file types are supported:
                          -
                          0 - Meteonorm
                          1 - PV*SOL
                          2 - PVsyst 5 and PVsyst 6
                          3 - PVsyst 4
                          -
                          If software you intend to use your .hor file to, is not listed above, it's the best to use the horizonFileType 0 (Meteonorm). This type is universal and supported with most sun related applications. Though, it does lack the data about the location, coordinates, altitude etc.
                          This type is also mandatory for both Meteonorm 6 and Meteonorm 7.
                          -
                          If not supplied 0 (Meteonorm 6 and Meteonorm 7) will be used by default.
        exportHorizon_: Set to "True" to bake export(create) a .hor file.
                        -
                        If not supplied default value "False" will be used.
        bakeIt_: Set to "True" to bake the Horizon angles rose into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        azimuths: Azimuth angles (directions) in range from 0 to 360 measured clockwise from true North.
                  -
                  In degrees.
        horizonAngles: Horizon (sky view) angles which correspond to each azimuth.
                       -
                       In degrees.
        maximalAzimuth: Direction which corresponds to the maximalHorizonAngle below.
                        -
                        In degrees.
        maximalHorizonAngle: Maximal horizon angle.
                             -
                             In degrees.
        horizonAnglesRose: A mesh representing horizon angles for each azimuth.
        compassCrvs: Compass azimuth labels and curves.
        originPt: The origin (center) point of the inputted "_context" geometry.
                  It's basically equal to the "_origin" input.
                  -
                  Use this point to move "horizonAnglesRose", "compassCrvs" and "title" geometry around in the Rhino scene with grasshopper's "Move" component.
        title: Title geometry with information about location.
        legend: Legend of the horizonAnglesRose.
        legendPlane: Legend's starting plane, which can be used to move the "legend" geometry with grasshopper's "Move" component.
                     -
                     Connect this output to a Grasshopper's "Plane" parameter in order to preview the point in the Rhino scene.
"""

ghenv.Component.Name = "Gismo_Horizon Angles"
ghenv.Component.NickName = "HorizonAngles"
ghenv.Component.Message = "VER 0.0.1\nJAN_29_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "2 | Terrain"
#compatibleGismoVersion = VER 0.0.1\nJAN_29_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import datetime
import System
import Rhino
import time
import math
import os


def checkInputData(analysisGeometry, contextMeshes, north, scale, outputGeometryIndex, workingFolderPath, horizonFileType):
    
    pathsAnalysisGeometry = analysisGeometry.Paths
    analysisGeometryBranchesLists = analysisGeometry.Branches
    
    srfCornerPtsLL = []
    srfCentroidL = []
    selfShadingAnalysisGeometry = []  # self shading will not be applied, even though this list is created
    
    for branchIndex,branchList in enumerate(analysisGeometryBranchesLists):  # all branches have a single item in its list
        if len(branchList) > 0:  # branch list is not empty
            id = list(branchList)[0]
            obj = rs.coercegeometry(id)
            # input is a point
            if isinstance(obj, Rhino.Geometry.Point):
                srfCornerPts = [obj.Location]
                srfCentroid = obj.Location
            # input is brep
            elif isinstance(obj, Rhino.Geometry.Brep):
                selfShadingAnalysisGeometry.append(obj)
                facesCount = obj.Faces.Count
                if facesCount > 1:
                    # inputted polysurface
                    srfCornerPts = []
                    srfCentroid = None
                    printMsg = "One or more of the breps you supplied to \"_analysisGeometry\" is a polysurface. Please supply a surface instead."
                    level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
                    ghenv.Component.AddRuntimeMessage(level, printMsg)
                    print printMsg
                else:
                    # inputted brep with a single surface
                    srfCornerPts = obj.DuplicateVertices()
                    srfCentroid = Rhino.Geometry.AreaMassProperties.Compute(obj).Centroid
            else:
                # any other geometry than surface and point
                srfCornerPts = []
                srfCentroid = None
                printMsg = "One or more of the geometry you supplied to \"_analysisGeometry\" is not a surface nor a point, which is what \"_analysisGeometry\" requires as an input."
                level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
                ghenv.Component.AddRuntimeMessage(level, printMsg)
                print printMsg
        
        elif len(branchList) == 0:  # empty branches
            srfCornerPts = []
        
        srfCornerPtsLL.append(srfCornerPts)
        srfCentroidL.append(srfCentroid)
    
    # check if _analysisGeometry input contains only "None" values
    NoneItemsIn_srfCentroidL = 0
    for item in srfCentroidL:
        if item == None:
            NoneItemsIn_srfCentroidL += 1
    if len(srfCentroidL) == NoneItemsIn_srfCentroidL:
        srfCornerPtsLL = srfCentroidL = srfCentroid = contextMeshJoined = northRad = northVec = scale = outputGeometryIndex = workingSubFolderPath = horizonFileType = horizonFileTypeLabel = unitConversionFactor = None
        validInputData = False
        printMsg = "The value(s) you supplied to the \"_analysisGeometry\" input are neither points nor surfaces.\n" + \
                   "Please input one of these."
        return srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg
    
    
    # check if something inputted into "context_" input
    if len(contextMeshes) == 0:
        srfCornerPtsLL = srfCentroidL = srfCentroid = contextMeshJoined = northRad = northVec = scale = outputGeometryIndex = workingSubFolderPath = horizonFileType = horizonFileTypeLabel = unitConversionFactor = None
        validInputData = False
        printMsg = "Input the \"terrainShadingMask\" output from \"Terrain shading mask\" component.\n" + \
                   "You can additionally input other opaque obstacles surrounding your location: houses, buildings etc.\n" + \
                   "Do not input trees, as they are not opaque obstacles and should not be taken into account when analysing the horizon angles."
        return srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg
    else:
        # remove "None" from context_
        contextMeshesFiltered = []
        for mesh in contextMeshes:
            if mesh != None:
                contextMeshesFiltered.append(mesh)
        
        contextMeshJoined = Rhino.Geometry.Mesh()
        for filteredContextMesh in contextMeshesFiltered:
            contextMeshJoined.Append(filteredContextMesh)
    
    
    if (north == None):
        northRad = 0  # default, in radians
        northVec = Rhino.Geometry.Vector3d(0,1,0)
    else:
        try:  # check if it's a number
            north = float(north)
            if north < 0 or north > 360:
                srfCornerPtsLL = srfCentroidL = srfCentroid = contextMeshJoined = northRad = northVec = scale = outputGeometryIndex = workingSubFolderPath = horizonFileType = horizonFileTypeLabel = unitConversionFactor = None
                validInputData = False
                printMsg = "Please input north angle value from 0 to 360."
                return srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg
        except Exception, e:  # check if it's a vector
            north.Unitize()
        
        northRad, northVec = gismo_preparation.angle2northClockwise(north)
    northVec.Unitize()
    
    
    if (scale == None) or (scale <= 0):
        scale = 1  # default
    
    
    if workingFolderPath == None:
        # nothing inputted to "workingFolder_" input, use default Gismo folder instead (C:\gismo)
        gismoFolder = sc.sticky["gismo_gismoFolder"]  # "gismoFolder_" input of Gismo_Gismo component
        workingSubFolderPath = os.path.join(gismoFolder, "horizon_files")
    else:
        # something inputted to "workingFolder_" input
        workingSubFolderPath = os.path.join(workingFolderPath, "horizon_files")
    folderCreated = gismo_preparation.createFolder(workingSubFolderPath)
    if folderCreated == False:
        srfCornerPtsLL = srfCentroidL = srfCentroid = contextMeshJoined = northRad = northVec = scale = outputGeometryIndex = workingSubFolderPath = horizonFileType = horizonFileTypeLabel = unitConversionFactor = None
        validInputData = False
        printMsg = "workingFolder_ input is invalid.\n" + \
                   "Input the string in the following format (example): C:\someFolder.\n" + \
                   "Or do not input anything, in which case a default Gismo folder will be used instead."
        return srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg
    
    
    if (horizonFileType == None) or (horizonFileType == 0):  # .hor file with no heading (Meteonorm 6 and Meteonorm 7)
        horizonFileType = 0  # default
        horizonFileTypeLabel = ""
    elif (horizonFileType == 1):  # PV*SOL .hor file
        horizonFileType = 1
        horizonFileTypeLabel = "_PVSOL"
    elif (horizonFileType == 2):  # PVsyst 5 and PVsyst 6 .hor file
        horizonFileType = 2
        horizonFileTypeLabel = "_PVsyst5_6"
    elif (horizonFileType == 3):  # PVsyst 4 .hor file
        horizonFileType = 3
        horizonFileTypeLabel = "_PVsyst4"
    elif (horizonFileType < 0) or (horizonFileType > 3):
        horizonFileType = 0  # default Meteonorm
        horizonFileTypeLabel = ""
        print "horizonFileType_ input only supports the following values:\n" + \
              "0 - Meteonorm .hor file.\n" + \
              "1 - PVSOL .hor file,\n" + \
              "2 - PVsyst 5 and PVsyst 6 .hor file,\n" + \
              "3 - PVsyst4 .hor file.\n" + \
              " \n" + \
              "horizonFileType_ input set to 0 (Meteonorm) by default."
    
    
    if (outputGeometryIndex == None) or (outputGeometryIndex < 0):
        outputGeometryIndex = 0  # default
    else:
        if (outputGeometryIndex + 1) > len(pathsAnalysisGeometry):
            srfCornerPtsLL = srfCentroidL = srfCentroid = contextMeshJoined = northRad = northVec = scale = outputGeometryIndex = workingSubFolderPath = horizonFileType = horizonFileTypeLabel = unitConversionFactor = None
            validInputData = False
            printMsg = "The index number inputted into \"outputGeometryIndex_\" is higher than number of inputted objects into \"_analysisGeometry\". Please choose an input for \"outputGeometryIndex_\" from 0 to %s." % str(len(analysisGeometryBranchesLists)-1)
            return srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg
        elif srfCentroidL[outputGeometryIndex] == None:
            srfCornerPtsLL = srfCentroidL = srfCentroid = contextMeshJoined = northRad = northVec = scale = outputGeometryIndex = workingSubFolderPath = horizonFileType = horizonFileTypeLabel = unitConversionFactor = None
            validInputData = False
            printMsg = "The %s supplied to the \"outputGeometryIndex_\" input, points to the %s. item in the \"_analysisGeometry\" input. This item is neither a surface, nor a point, therefor it's invalid.\n" % (outputGeometryIndex, outputGeometryIndex) + \
                       "Remove that item from your \"_analysisGeometry\" input, or change the value supplied to the \"outputGeometryIndex_\" so that it points to some other valid \"_analysisGeometry\" item."
            outputGeometryIndex  = None  # set bellow the "printMsg" variable, so that it does not confront with it
            return srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg
    
    
    srfCentroid = srfCentroidL[outputGeometryIndex]
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()  # factor to convert Rhino document units to meters.
    
    validInputData = True
    printMsg = "ok"
    
    return srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg


def calculateHorizonAngles(contextMeshJoined, origin, northRad, unitConversionFactor):
    
    originLifted = Rhino.Geometry.Point3d(origin.X, origin.Y, origin.Z + 0.01)  # fix for rays intersection, if user inputted a ground surface to "_contex" input
    
    # create skyDome
    skyDomeRadius = 200 / unitConversionFactor  # in meters
    skyDomeSphere = Rhino.Geometry.Sphere(originLifted, skyDomeRadius)
    skyDomeSrf = skyDomeSphere.ToBrep().Faces[0]
    
    # small number of rays (for example: precisionU = 30, precisionV = 10) can result in rays missing the contextMeshJoined, thererfor the shadingMaskSrf will not be created
    precisionU = 3600  # rays shot per 0.1 degrees (10th of a degree)
    precisionV = 1200  # rays shot per 0.075 degrees - more denser than precisionU
    #precisionU = 140
    #precisionV = 40
    
    halvedSkyDomeSrf = skyDomeSrf.Trim(Rhino.Geometry.Interval(skyDomeSrf.Domain(0)[0], skyDomeSrf.Domain(0)[1]), Rhino.Geometry.Interval(0, skyDomeSrf.Domain(1)[1])) # split the skyDome sphere in half
    halvedSkyDomeSrf.SetDomain(1, Rhino.Geometry.Interval(0, halvedSkyDomeSrf.Domain(1)[1]))  # shrink the halvedSkyDomeSrf V start domain
    
    clockwise = True
    if clockwise == True:
        # reverse the U domain (from counter-clockwise to clockwise)
        uStart,uEnd = halvedSkyDomeSrf.Domain(0)
        interval0 = Rhino.Geometry.Interval(-uEnd, -uStart)
        halvedSkyDomeSrf.SetDomain(0,interval0)
        halvedSkyDomeSrf = halvedSkyDomeSrf.Reverse(0)
    else:
        pass
    
    # rotate the halvedSkyDomeSrf by 90 degrees so that it starts at 0 degrees (+Y axis)
    transformMatrixRotate1 = Rhino.Geometry.Transform.Rotation(math.radians(90), Rhino.Geometry.Vector3d(0,0,1), originLifted)
    halvedSkyDomeSrf.Transform(transformMatrixRotate1)
    
    # rotation due to north angle position
    #transformMatrixRotate2 = Rhino.Geometry.Transform.Rotation(-northRad, Rhino.Geometry.Vector3d(0,0,1), originLifted)  # counter-clockwise
    transformMatrixRotate2 = Rhino.Geometry.Transform.Rotation(northRad, Rhino.Geometry.Vector3d(0,0,1), originLifted)  # clockwise
    halvedSkyDomeSrf.Transform(transformMatrixRotate2)
    
    skyDomeDomainUmin, skyDomeDomainUmax = halvedSkyDomeSrf.Domain(0)
    skyDomeDomainVmin, skyDomeDomainVmax = halvedSkyDomeSrf.Domain(1)
    stepU = (skyDomeDomainUmax - skyDomeDomainUmin)/precisionU
    stepV = (skyDomeDomainVmax - skyDomeDomainVmin)/precisionV
    
    
    # check for intersection between the contextMeshJoined and rays
    horizonAnglesRoseMeshPts = []
    lastRowPoints = []
    
    hitted = False  # initial switch
    for i in xrange(0,precisionU):
        u = skyDomeDomainUmin + stepU*i
        if (i % 10 == 0):
            horizonAnglesRoseMeshPts.append(originLifted)
            firstRowPt = halvedSkyDomeSrf.PointAt(u,0)
            horizonAnglesRoseMeshPts.append(firstRowPt)
        for k in xrange(0,precisionV):
            v = skyDomeDomainVmin + stepV*k
            skyDomePt = halvedSkyDomeSrf.PointAt(u,v)
            rayVector = skyDomePt-originLifted
            ray = Rhino.Geometry.Ray3d(originLifted, rayVector)
            rayIntersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(contextMeshJoined,ray)
            if rayIntersectParam >= 0:
                # ray hitted something in that column
                hitted = True
                lastRowPt = skyDomePt
                continue
            else:
                # ray did not hit anything in that column
                pass
        if hitted == False:
            lastRowPt = halvedSkyDomeSrf.PointAt(u,0)
        lastRowPoints.append(lastRowPt)
        hitted = False  # reset the hitted switch
    
    
    # calculate the horizonAngles from lastRowPoints:
    azimuthsD = []  # depends on precisionU and precisionV
    horizonAnglesD = []
    horizonAnglesD_for_colors = []  # made of horizonAnglesD duplicates to account for the origin point of the horizonAnglesRoseMeshPts
    for azimuth,lastRowPt in enumerate(lastRowPoints):
        if (azimuth % 10 == 0):  # only take azimuths 0,10,20,30... 3580,3590
            projectedLastRowPt = Rhino.Geometry.Point3d(lastRowPt.X, lastRowPt.Y, originLifted.Z)
            tangent_horizonAngleR = (lastRowPt.Z - originLifted.Z)/originLifted.DistanceTo(projectedLastRowPt)
            if tangent_horizonAngleR < 0.001:  # fix if horizonAngle = 0
                tangent_horizonAngleR = 0
            horizonAngleR = math.atan(tangent_horizonAngleR)
            horizonAngleD = math.degrees(horizonAngleR)  # .hor files have integer values for horizon angles
            
            horizonAnglesD.append(int(horizonAngleD))
            azimuthsD.append(int(azimuth/10))  # convert the azimuths from 0,10,20,30... 3580,3590 to 0,1,2,3... 358,359
            
            horizonAnglesD_for_colors.append(horizonAngleD)
            horizonAnglesD_for_colors.append(horizonAngleD)
    
    
    # possible future creation of contextShadingMask (more precisely contextShadingMaskUnscaledUnrotated), the same as from "Terrain shading mask" component by its code starting from "    if maskStyle == 0:  # spherical terrain shading mask" (line ?)
    contextShadingMaskUnscaledUnrotated = None
    
    return azimuthsD, horizonAnglesD, originLifted, horizonAnglesRoseMeshPts, horizonAnglesD_for_colors, contextShadingMaskUnscaledUnrotated


def main(contextMeshJoined, srfCentroidL, northRad, outputGeometryIndex, unitConversionFactor):
    
    azimuthsD_dataTree = Grasshopper.DataTree[object]()
    horizonAnglesD_dataTree = Grasshopper.DataTree[object]()
    maximalAzimuthD_dataTree = Grasshopper.DataTree[object]()
    maximalHorizonAngleD_dataTree = Grasshopper.DataTree[object]()
    
    paths = _analysisGeometry.Paths
    for index,srfCentroid in enumerate(srfCentroidL):
        if srfCentroid != None:  # the inputted _analysisGeometry is not a point nor a single faced brep
            azimuthsD, horizonAnglesD, originLifted, horizonAnglesRoseMeshPts_notPicked, horizonAnglesD_for_colors_notPicked, contextShadingMaskUnscaledUnrotated_notPicked = calculateHorizonAngles(contextMeshJoined, srfCentroid, northRad, unitConversionFactor)
            
           # maximualHorizonAngle, maximalAzimuth
            maximalHorizonAngle_maximalAzimuth = []
            for i,azimuth in enumerate(azimuthsD):
                maximalHorizonAngle_maximalAzimuth.append([horizonAnglesD[i], azimuthsD[i]])
            maximalHorizonAngle_maximalAzimuth.sort()
            maximalHorizonAngleD = maximalHorizonAngle_maximalAzimuth[-1][0]
            maximalAzimuthD = maximalHorizonAngle_maximalAzimuth[-1][1]
            
            # extract azimuthsD and horizonAnglesD for geometry outputs (horizonAnglesRose, compassCrvs, title, legend) and for horizon file (.hor)
            if index == outputGeometryIndex:
                azimuthsD_for_horizonFile = azimuthsD
                horizonAnglesD_for_horizonFile = horizonAnglesD
                
                maximalAzimuthD_for_title = maximalAzimuthD
                maximalHorizonAngleD_for_title = maximalHorizonAngleD
                
                horizonAnglesRoseMeshPts = horizonAnglesRoseMeshPts_notPicked
                horizonAnglesD_for_colors = horizonAnglesD_for_colors_notPicked
                contextShadingMaskUnscaledUnrotated = contextShadingMaskUnscaledUnrotated_notPicked  # it's always None, unless in future contextShadingMaskUnscaledUnrotated is created in "calculateHorizonAngles" function
            
            # add the azimuthsD, horizonAnglesD, maximalAzimuthD, maximalHorizonAngleD to data trees
            azimuthsD_dataTree.AddRange(azimuthsD, paths[index])
            horizonAnglesD_dataTree.AddRange(horizonAnglesD, paths[index])
            maximalAzimuthD_dataTree.AddRange([maximalAzimuthD], paths[index])
            maximalHorizonAngleD_dataTree.AddRange([maximalHorizonAngleD], paths[index])
    
    return azimuthsD_dataTree, horizonAnglesD_dataTree, azimuthsD_for_horizonFile, horizonAnglesD_for_horizonFile, maximalAzimuthD_dataTree, maximalHorizonAngleD_dataTree, maximalAzimuthD_for_title, maximalHorizonAngleD_for_title, horizonAnglesRoseMeshPts, horizonAnglesD_for_colors, contextShadingMaskUnscaledUnrotated


def compassCrvs_legend(srfCentroid, horizonAnglesRoseMeshPts, horizonAnglesD_for_colors, maximalAzimuthD_for_title, maximalHorizonAngleD_for_title, unitConversionFactor, legendBakePar):
    
    # extract data from legendBakePar_
    legendStyle, legendStartPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, customLegendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = gismo_preparation.read_legendBakePar(legendBakePar)
    if (len(customColors) == 0):
        # "customColors_" input has not been defined in "Legend Bake Parameters" component. So use black-white default customColors
        #customColors = [System.Drawing.Color.FromArgb(255,255,255), System.Drawing.Color.FromArgb(0,0,0)]
        #legendBakePar = gismo_preparation.modify_dataTree(legendBakePar, 4, customColors)
        pass
    
    # horizonAnglesRoseMesh
    horizonAnglesRoseMeshPts = horizonAnglesRoseMeshPts + [horizonAnglesRoseMeshPts[0], horizonAnglesRoseMeshPts[1]]  # to close the horizonAnglesRoseMesh
    horizonAnglesD_for_colors = horizonAnglesD_for_colors + [horizonAnglesD_for_colors[0], horizonAnglesD_for_colors[1]]  # to close the horizonAnglesRoseMesh
    colors = gismo_preparation.numberToColor(horizonAnglesD_for_colors, customColors, minValue, maxValue)
    
    horizonAnglesRoseMesh = gismo_geometry.meshFromPoints(int(len(horizonAnglesRoseMeshPts)/2), 2, horizonAnglesRoseMeshPts, colors)
    
    # compass curves
    skyDomeRadius = 200 / unitConversionFactor  # in meters
    scaleDummy = 1
    divisionPts, compassCrvs2b, textLabels = gismo_geometry.compassDirections(srfCentroid, skyDomeRadius, scaleDummy, northVec)
    compassCrvs = compassCrvs2b + textLabels
    
    # legend
    legendUnit = "degrees"
    legendMesh, legendStartPlane = gismo_geometry.createLegend(compassCrvs, horizonAnglesD_for_colors, legendBakePar, legendUnit)
    
    # title
    titleLabelText = "Horizon angles\nLocation: %s\nLatitude: %s, Longitude: %s\nMaximum horizon angle: %s deg, at %s deg azimuth" % (locationName, locationLatitudeD, locationLongitudeD, maximalHorizonAngleD_for_title, maximalAzimuthD_for_title)
    titleDescriptionLabelMeshes, titleStartPt, titleTextSize = gismo_preparation.createTitle("mesh", compassCrvs, [titleLabelText], customTitle, textStartPt=None, textSize=fontSize)
    
    
    # hide legendBasePt output
    ghenv.Component.Params.Output[12].Hidden = True
    
    return horizonAnglesRoseMesh, compassCrvs, [titleDescriptionLabelMeshes], [legendMesh], legendStartPlane


def scalingRotating(northRad, scale, srfCentroid, contextShadingMaskUnscaledUnrotated, horizonAnglesRoseMesh, compassCrvs, legend, legendStartPlane, titleDescriptionLabelMeshes):
    
    # scaling
    legendBasePt = legendStartPlane.Origin
    transformMatrixScale = Rhino.Geometry.Transform.Scale(Rhino.Geometry.Plane(srfCentroid, Rhino.Geometry.Vector3d(0,0,1)), scale, scale, scale)
    transformMatrixLegendBasePtScale = Rhino.Geometry.Transform.Scale(Rhino.Geometry.Plane(legendBasePt, Rhino.Geometry.Vector3d(0,0,1)), scale, scale, scale)
    
    geometryList = [contextShadingMaskUnscaledUnrotated] + [horizonAnglesRoseMesh]
    for geometry in geometryList:
        if geometry != None:  # if "contextShadingMaskUnscaledUnrotated" is not created (equals None) (as it is not right now), exclude it
            transfromBoolSuccess = geometry.Transform(transformMatrixScale)
    
    # make a difference if a point is plugged into the "legendLocation_" input of the "Legend Parameters" component
    #lowB, highB, numSeg, customColors, initialLegendBasePt, legendScale, legendFont, legendFontSize, legendBold, decimalPlaces, removeLessThan = lb_preparation.readLegendParameters(legendPar_, False)
    legendStyle, customLegendStartPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, customLegendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = gismo_preparation.read_legendBakePar(legendBakePar_)
    #if (legendStartPlane == None):
        #dummyValues = range(0,100)
        #legendMesh, legendStartPlane = gismo_geometry.createLegend(compassCrvs, dummyValues, legendBakePar_)
    #legendBasePt = legendStartPlane.Origin
    
    if customLegendStartPlane == None:
        geometryList2 = compassCrvs + legend + [legendBasePt] + titleDescriptionLabelMeshes
    else:
        geometryList2 = compassCrvs
        geometryList3 = legend + [legendBasePt] + titleDescriptionLabelMeshes
        for geometry3 in geometryList3:
            transfromBoolSuccess = geometry3.Transform(transformMatrixLegendBasePtScale)
    
    for geometry2 in geometryList2:
        transfromBoolSuccess = geometry2.Transform(transformMatrixScale)
    
    return contextShadingMaskUnscaledUnrotated, horizonAnglesRoseMesh, compassCrvs, legend, Rhino.Geometry.Plane(legendBasePt, legendStartPlane.XAxis, legendStartPlane.YAxis), titleDescriptionLabelMeshes


def createHorFile(locationLatitudeD, locationLongitudeD, locationName, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, azimuthsD, horizonAnglesD):
    
    horFileNamePlusExtension = locationName + "_" + str(locationLatitudeD) + "_" + str(locationLongitudeD) + horizonFileTypeLabel + ".hor"
    horFilePath = os.path.join(workingSubFolderPath, horFileNamePlusExtension)
    
    nowUTC = datetime.datetime.utcnow()  # UTC date and time
    UTCdateTimeString = str(nowUTC.year) + "-" + str(nowUTC.month) + "-" + str(nowUTC.day) + " " + str(nowUTC.hour) + ":" + str(nowUTC.minute) + ":" + str(nowUTC.second)
    
    
    if (horizonFileType == 0):
        # Meteonorm 6 and Meteonorm 7
        correctedAzimuthsD = [dir-180 for dir in azimuthsD]  # correct azimuthsD: -180 to 179 for both PV*SOL and PVsyst 5 and PVsyst 6
        correctedHorizonAnglesD = horizonAnglesD
        horFileList = []
    elif (horizonFileType == 1) or (horizonFileType == 2):
        # PV*SOL and PVsyst 5 and PVsyst 6
        headingString = "# Horizon file created with Gismo plugin\n" + \
                        "# Location: %s, lat: %s, lon: %s\n" % (locationName, locationLatitudeD, locationLongitudeD) + \
                        "# Created on (UTC): %s\n" % UTCdateTimeString
        correctedAzimuthsD = [dir-180 for dir in azimuthsD]  # correct azimuthsD: -180 to 179 for both PV*SOL and PVsyst 5 and PVsyst 6
        correctedHorizonAnglesD = horizonAnglesD
        horFileList = [headingString, " \n"]
    elif (horizonFileType == 3):
        # PVsyst 4
        headingString = "# Horizon file created with Gismo plugin, Location: %s, lat: %s, lon: %s, Created on (UTC): %s\n"  % (locationName, locationLatitudeD, locationLongitudeD, UTCdateTimeString)  # use a single line string for "PVsyst4" .hor type? (2)
        correctedAzimuthsD = []
        correctedHorizonAnglesD = []
        for i,horAngle in enumerate(horizonAnglesD):
            correctedAzimuthD = azimuthsD[i]-180  # correct azimuthsD: -180 to 179 for PVsyst 4
            if (correctedAzimuthD >= -120) and (correctedAzimuthD < 120):
                correctedAzimuthsD.append(correctedAzimuthD)
                correctedHorizonAnglesD.append(horizonAnglesD[i])
        horFileList = [headingString, " \n"]
    
    # create .hor file
    for i in range(len(correctedAzimuthsD)):
        horFileList.append("%s %s\n" % (correctedAzimuthsD[i], correctedHorizonAnglesD[i]))
    
    myFile = open(horFilePath,"w")
    for line in horFileList:
        myFile.write(line)
    myFile.close()
    
    print ".hor file successfully created at: %s\n " % horFilePath


def bakingGrouping(locationName, locationLatitudeD, locationLongitudeD, srfCentroid, terrainShadingMask, horizonAnglesRoseMesh, maximalHorizonAngleD_for_title, compassCrvs, legend, titleDescriptionLabelMeshes):
    
    # baking
    layerName = locationName + "_" + str(locationLatitudeD) + "_" + str(locationLongitudeD) + "_MAX_HORIZONANGLE=" + str(maximalHorizonAngleD_for_title)
    
    layParentName = "GISMO"; laySubName = "PHOTOVOLTAICS"; layerCategoryName = "HORIZON_ANGLES"; newLayerCategory = False
    laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # green
    layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
    
    layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor, legendBakePar_) 
    
    geometryToBakeL = [horizonAnglesRoseMesh] + [Rhino.Geometry.Point(srfCentroid)]
    geometryIds = gismo_preparation.bakeGeometry(geometryToBakeL, layerIndex)
    
    geometryToBakeL2 = compassCrvs
    geometryIds2 = gismo_preparation.bakeGeometry(geometryToBakeL2, layerIndex)
    
    geometryToBakeL3 = titleDescriptionLabelMeshes
    geometryIds3 = gismo_preparation.bakeGeometry(geometryToBakeL3, layerIndex)
    
    geometryToBakeL4 = legend
    geometryIds4 = gismo_preparation.bakeGeometry(geometryToBakeL4, layerIndex)
    
    # grouping of horizonAnglesRoseMesh and compassCrvs
    groupIndex = gismo_preparation.groupGeometry(layerName + "_horizonAnglesRose_compassCrvs", geometryIds + geometryIds2)
    # grouping of title
    groupIndex2 = gismo_preparation.groupGeometry(layerName + "_title", geometryIds2)
    # grouping of legend
    groupIndex2 = gismo_preparation.groupGeometry(layerName + "_legend", geometryIds2)


def printOutput(north, latitude, longitude, locationName, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType):
    
    resultsCompletedMsg = "Horizon angles component results successfully completed!"
    printOutputMsg = \
    """
Input data:

Location (deg.): %s
Latitude (deg.): %s
Longitude (deg.): %s
North (deg.): %s

Scale: %s
Output geometry index: %s
Working folder: %s
Horizon file type: %s
    """ % (locationName, latitude, longitude, north, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_mainComponent = sc.sticky["gismo_mainComponent"]()
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_geometry = sc.sticky["gismo_CreateGeometry"]()
        
        locationName, locationLatitudeD, locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_preparation.checkLocationData(_location)
        if validLocationData:
            srfCornerPtsLL, srfCentroidL, srfCentroid, contextMeshJoined, northRad, northVec, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, unitConversionFactor, validInputData, printMsg = checkInputData(_analysisGeometry, _context, north_, scale_, outputGeometryIndex_, workingFolder_, horizonFileType_)
            if validInputData:
                if _runIt:
                    azimuthsD, horizonAnglesD, azimuthsD_for_horizonFile, horizonAnglesD_for_horizonFile, maximalAzimuthD, maximalHorizonAngleD, maximalAzimuthD_for_title, maximalHorizonAngleD_for_title, horizonAnglesRoseMeshPts, horizonAnglesD_for_colors, contextShadingMaskUnscaledUnrotated = main(contextMeshJoined, srfCentroidL, northRad, outputGeometryIndex, unitConversionFactor)
                    horizonAnglesRoseMeshUnscaledUnrotated, compassCrvsUnscaledUnrotated, titleDescriptionLabelMeshesUnscaledUnrotated, legendUnscaledUnrotated, legendBasePtUnscaledUnrotated = compassCrvs_legend(srfCentroid, horizonAnglesRoseMeshPts, horizonAnglesD_for_colors, maximalAzimuthD_for_title, maximalHorizonAngleD_for_title, unitConversionFactor, legendBakePar_)
                    contextShadingMask, horizonAnglesRoseMesh, compassCrvs, legend, legendPlane, titleDescriptionLabelMeshes = scalingRotating(northRad, scale, srfCentroid, contextShadingMaskUnscaledUnrotated, horizonAnglesRoseMeshUnscaledUnrotated, compassCrvsUnscaledUnrotated, legendUnscaledUnrotated, legendBasePtUnscaledUnrotated, titleDescriptionLabelMeshesUnscaledUnrotated)
                    if exportHorizon_: createHorFile(locationLatitudeD, locationLongitudeD, locationName, workingSubFolderPath, horizonFileType, horizonFileTypeLabel, azimuthsD_for_horizonFile, horizonAnglesD_for_horizonFile)
                    if bakeIt_: bakingGrouping(locationName, locationLatitudeD, locationLongitudeD, srfCentroid, contextShadingMask, horizonAnglesRoseMesh, maximalHorizonAngleD_for_title, compassCrvs, legend, titleDescriptionLabelMeshes)
                    printOutput(north_, locationLatitudeD, locationLongitudeD, locationName, scale, outputGeometryIndex, workingSubFolderPath, horizonFileType)
                    azimuths = azimuthsD; horizonAngles = horizonAnglesD; horizonAnglesRose = horizonAnglesRoseMesh; maximalHorizonAngle = maximalHorizonAngleD; maximalAzimuth = maximalAzimuthD; originPt = srfCentroid; title = titleDescriptionLabelMeshes; 
                else:
                    print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Horizon angles component"
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