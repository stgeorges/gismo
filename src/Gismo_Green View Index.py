# green view index
#
# Gismo is a plugin for GIS Environmental Analysis (GPL) started by Djordje Spasic.
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
Use this component to calculate Green View Index.
GVI is a quantitative indicator to evaluate visual greenery from pedestrian’s perspective.
-
Provided by Gismo 0.0.3
    
    input:
        _treesAndGreenAreas: Polysurface/mesh 3D trees from 'OSM 3D' component, or park/green areas from 'OSM search' component or any other (for example manually created) polysurface/mesh geometry which represents trees and green areas.
        context_: Polysurface/mesh objects of anything else which is not trees or park/green areas. For example: 3D buildings from 'OSM 3D' component,
        _analysisGeo: - A planar surface, on which the results of GVI analysis will be layed on. Use this kind of input to analize smaller areas, like plazas, squares for example.
                        OR
                      - A point or list of points where GVI analysis will be performed. Use this kind of input to analize larger areas, like city block or city blocks.
        gridSize_: if '_analysisGeo' input is a brep, then this input is:   mesh edge length of '_analysisGeo' input.
                   OR
                   if '_analysisGeo' input is a point(s), then this input is:   the radius of the analysis area at each '_analysisGeo' point.
                   -
                   By default it is 10.
        offsetDist_: the distance or which the input '_analysisGeo' will be moved vertically. It should generally be 1.63 meters, which corresponds to the eyesight height of the 1.75 meter tall average human height.
        vertFOVangles_: a list of two values: vertical upper and lower Field Of View angles. By default they are 25 and 30 degrees, which corresponds to average person's vertical FOV angles within the boundaries of the color discrimination.
        precision_: Overall analysis precision. Ranges from 1-100. It represents the square root number of shading analysis points per visibility cone surface segment.
                    Example - precision of 20 would be 400 shading analysis points per single visibility cone surface segment.
                    CAUTION!!! Higher precision numbers (50 >) require stronger performance PCs. Start with lower numbers (like 10, or 20), and then try increasing them. Once the final 'GVIvaluesAvr' does not significantly change, you can use that 'precision_' input.
                    -
                    If not supplied, default value of 10 will be used.
        legendBakePar_: Optional legend bake parameters from the Gismo "Legend Parameters" component.
                        -
                        Use this input to change the color of the "GVI" output, or edit the "legend" and "title" outputs.
        bakeIt_: Set to "True" to bake the output geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        GVI: results mesh from input '_analysisGeo'
        GVIvalues: Green View Index value for each mesh vertex of GVI output mesh. In percent.
                   GVI larger than 30% brings mental and psychological comfort to people.
                   source: Aoki, Y. Trends of Researches on Visual Geenery since 1974 in Japan. Environmental 480Information Science 2006, 34, 46-49
        GVIvaluesAvr: average value of 'GVIvalues'
        title: Title mesh
        titleOriginPt: Starting point of 'title' mesh.
        legend: Legend of the horizonAnglesRose.
        legendPlane: Legend's starting plane, which can be used to move the "legend" geometry with grasshopper's "Move" component.
                     -
                     Connect this output to a Grasshopper's "Plane" parameter in order to preview the point in the Rhino scene.
"""

ghenv.Component.Name = "Gismo_Green View Index"
ghenv.Component.NickName = "GreenViewIndex"
ghenv.Component.Message = "VER 0.0.3\nDEC_18_2020"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nDEC_18_2020
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext as sc
import Grasshopper
import System
import Rhino
import math
import clr
import gc


tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
globalZup_vec = Rhino.Geometry.Vector3d(0,0,1)



def XY_pln(pt = rg.Point3d(0,0,0)):
    """create XY pln with 'pt' as its origin"""
    if (type(pt) != rg.Point3d):
        pt = ToPt3d(pt)
    
    return rg.Plane( pt, rg.Vector3d(1,0,0), rg.Vector3d(0,1,0) )


def checkInputData(treesAndGreenAreas, context, analysisGeo_id_L, gridSize, offsetDist, vertFOVangles, precision):
    
    # check inputs
    
    # _treesAndGreenAreas
    if (len(treesAndGreenAreas) == 0):
        analysisMesh_lifted = analysisGeo_inputType = vertUpFOVAngleD = vertDownFOVAngleD = None
        validInputData = False
        printMsg = "\"_treesAndGreenAreas\" input is empty. Add to it 3D trees from 'OSM 3D' component, or park/green areas from 'OSM search' component or any other polysurface/mesh geometry which represents trees and green areas."
        return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
    
    
    # _analysisGeo
    if (len(analysisGeo_id_L) == 0) or ((analysisGeo_id_L[0]) == None):
        analysisMesh_lifted = analysisGeo_inputType = vertUpFOVAngleD = vertDownFOVAngleD = None
        validInputData = False
        printMsg = "\"_analysisGeo\" input is empty. Add to it planar surface or a list of points, on which the results of GVI analysis will be layed on."
        return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
    else:
        # input type check
        analysisGeo1 = rs.coercegeometry(analysisGeo_id_L[0])
        if (type(analysisGeo1) == rg.Curve) or (type(analysisGeo1) == rg.PolyCurve) or (type(analysisGeo1) == rg.PolyCurve) or (type(analysisGeo1) == rg.NurbsCurve) or (type(analysisGeo1) == rg.Extrusion) or (type(analysisGeo1) == rg.Mesh) or (type(analysisGeo1) == rg.Mesh):
            analysisMesh_lifted = analysisGeo_inputType = vertUpFOVAngleD = vertDownFOVAngleD = None
            validInputData = False
            printMsg = "\"_analysisGeo\" input should be either a point(s) or a planar srf. Currently it has an object."
            return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
        elif (type(analysisGeo1) == rg.Brep):
            analysisGeo_inputType = "brep"
            
            # allowed case1: '_analysisGeo' is a single brep
            if (len(analysisGeo_id_L) > 1):
                # if '_analysisGeo' input is a brep, only one brep is allowed! This is how component works
                analysisMesh_lifted = vertUpFOVAngleD = vertDownFOVAngleD = None
                validInputData = False
                printMsg = "\"_analysisGeo\" input should be either a point(s) or a planar srf. Currently it has more than one srf."
                return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
            elif (len(analysisGeo_id_L) == 1):
                # continue further below which checking of 'gridSize_' input
                pass
                
        
        elif (type(analysisGeo1) == rg.Point):
            # allowed case2: '_analysisGeo' is a single pt3d or a list of pt3d
            analysisGeo_inputType = "pt"
            analysisGeo_L = [rs.coercegeometry(id)    for id in analysisGeo_id_L]
    
    
    
    # gridSize_
    if (gridSize == None):
        analysisMesh_lifted = vertUpFOVAngleD = vertDownFOVAngleD = None
        validInputData = False
        printMsg = "\"gridSize_\" input is empty. It defines the mesh edge length of the '_analysisGeo' input. Set it to few meters for a start (for example: 5 meters/5000 milimeters/16 feet...). And them lower or increase depending on desired result of the 'GVI' output."
        return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
    
    
    # offsetDist_
    if (offsetDist == None):
        analysisMesh_lifted = vertUpFOVAngleD = vertDownFOVAngleD = None
        validInputData = False
        printMsg = "\"offsetDist_\" input is empty. It defines the distance for which '_analysisGeo' input will be moved vertically. By default it should be 1.63 meters, which corresponds to average height man's eyesight."
        return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
    
    
    # vertFOVangles_
    if (len(vertFOVangles) == 0) or (len(vertFOVangles) != 2):
        analysisMesh_lifted = vertUpFOVAngleD = vertDownFOVAngleD = None
        validInputData = False
        printMsg = "\"vertFOVangles_\" input needs to have two values: the first one is upper vertical, and the second is lower vertical field FieldOfView angle in degrees. If unsure, use the default values: 25, 30 degrees."
        return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
    elif (len(vertFOVangles) == 2):
        """
        # default values
        # based on:  https://www.researchgate.net/figure/Vertical-Field-of-View_fig4_257809591
        vertUpFOVAngleD = 25
        vertDownFOVAngleD = 30
        """
        vertUpFOVAngleD = vertFOVangles[0]
        vertDownFOVAngleD = vertFOVangles[1]
    
    
    # Udiv, Vdiv (divisions of each visiblity cone srf)
    if (precision < 1) or (precision > 100):
        analysisMesh_lifted = vertUpFOVAngleD = vertDownFOVAngleD = None
        validInputData = False
        printMsg = "\"precision_\" input needs to be between 1-100. Set it to any of these values. The higher the number, the more precise the result."
        return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg
    else:
        """
        Udiv = precision
        Vdiv = int(Udiv * 0.50813)
        ## FIX ##
        # '0.50813' comes by baking the 'srf_L' and checking one of theirs height and width. Because 'srf' always has bigger height (that's U) than width (that's V)
        # we wanted to have the size of UV grid equal in both U and V directions. So '0.50813' is 'srf' width/height
        ## FIX ##
        """
        pass
    
    
    
    
    if (analysisGeo_inputType == "brep"):
        # analysisMesh_lifted
        analysisMesh = gismo_prep.toMesh(analysisGeo1, minEdgeLength=gridSize, maxEdgeLength=gridSize)
        analysisMesh_lifted = gXform.move(analysisMesh, globalZup_vec * offsetDist)
    
    elif (analysisGeo_inputType == "pt"):
        
        polygonNumOfSides = 24  # to resemeble the circle
        
        
        analysisMesh_lifted = rg.Mesh()
        
        for id in analysisGeo_id_L:
            pt = rs.coerce3dpoint(id)
            pt_lifted = gXform.move(pt, globalZup_vec * offsetDist)
            polygonCrv = gismo_geo.polygonCrv( XY_pln(pt_lifted), gridSize, polygonNumOfSides)  # the radius will be 'gridSize'
            polygonBrep = rg.Brep.CreatePlanarBreps(polygonCrv, tol)[0]
            analysisMesh2 = gismo_prep.toMesh(polygonBrep)
            analysisMesh_lifted.Append( analysisMesh2 )
    
    
    
    validInputData = True
    printMsg = "ok"
    
    return analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg


def XY_pln(pt = rg.Point3d(0,0,0)):
    """create XY pln with 'pt' as its origin"""
    if (type(pt) != rg.Point3d):
        pt = ToPt3d(pt)
    
    return rg.Plane( pt, rg.Vector3d(1,0,0), rg.Vector3d(0,1,0) )


def main(treesAndGreenAreas, context,  analysisMesh_lifted, analysisGeo_inputType, analysisHeight, vertUpFOVAngleD, vertDownFOVAngleD, legendBakePar):
    # calculate GVI
    
    
    # default
    radius = 10  # approx. not relevant, because 'rg.Intersect.Intersection.MeshRay' shoots infinite rays
    numOfSeg = 12  # this means that there will be one 'srf' per 30 degree of 360 degrees
    componentIndex = 0  # for testing (represents the index of 'originPt') This number can be changed/
    
    
    # basic
    vertUpFOVAngleR = math.radians(vertUpFOVAngleD)
    vertDownFOVAngleR = math.radians(vertDownFOVAngleD)
    
    
    
    # a) convert to meshes and color them
    
    # '_treesAndGreenAreas' input
    treeGreenArea_mesh_L = []
    for id in treesAndGreenAreas:
        obj = rs.coercegeometry(id)
        if (type(obj) == rg.Mesh):
            pass
        else:
            obj = gismo_prep.toMesh(obj)
        
        # color mesh
        color_L = [System.Drawing.Color.FromArgb(181,230,29)    for i in xrange(obj.Vertices.Count)]  # '(181,230,29)' is a nuance of green. It could have been any other color, as it is only important that contex is (0,0,0) color
        colored_mesh = gismo_geo.colorMeshVertices(obj, color_L)
        
        treeGreenArea_mesh_L.append( colored_mesh ) 
    
    
    # 'context_' input
    context_mesh_L = []
    for id in context:
        obj = rs.coercegeometry(id)
        if (type(obj) == rg.Mesh):
            pass
        else:
            obj = gismo_prep.toMesh(obj)
        
        # color mesh
        color_L2 = [System.Drawing.Color.FromArgb(0,0,0)    for i in xrange(obj.Vertices.Count)]  # (0,0,0) is black color
        colored_mesh2 = gismo_geo.colorMeshVertices(obj, color_L2)
        
        context_mesh_L.append( colored_mesh2 ) 
    
    
    
    # b) join all meshes (buildings, trees and green areas)
    allMeshesJoined = gismo_prep.joinMeshes( context_mesh_L + treeGreenArea_mesh_L)
    allMeshesJoined_MVC_L = allMeshesJoined.VertexColors  # needed later
    
    
    
    
    # c) create visibility lofted srf at (0,0,0) pt, and get its divPt on each of srfs. Then move those divPt to each of 'originPt_L'. We do this to speed up the calculation
    pt_0_0_0 = rg.Point3d(0,0,0)
    
    pt_0_0_0_moved = gXform.move(pt_0_0_0, globalZup_vec * analysisHeight)
    
    visibSph_midCrv = gismo_geo.polygonCrv(XY_pln(pt_0_0_0_moved), radius, numOfSeg)
    
    moveDist_up = math.sin(vertUpFOVAngleR) * radius
    moveDist_down = math.sin(vertDownFOVAngleR) * radius
    
    
    # scaleFac
    radius_top = math.cos(vertUpFOVAngleR) * radius
    radius_bot = math.cos(vertDownFOVAngleR) * radius
    
    scaleFac_top = radius_top / radius
    scaleFac_bot = radius_bot / radius
    
    visibSph_topCrv_unscalled = gXform.move(visibSph_midCrv, globalZup_vec * moveDist_up)
    visibSph_botCrv_unscalled = gXform.move(visibSph_midCrv, globalZup_vec * -moveDist_down)
    
    visibSph_topCrv_cenPt = gXform.move(pt_0_0_0_moved, globalZup_vec * moveDist_up)
    visibSph_botCrv_cenPt = gXform.move(pt_0_0_0_moved, globalZup_vec * -moveDist_down)
    
    scale_pln1 = XY_pln(visibSph_topCrv_cenPt)
    scale_pln2 = XY_pln(visibSph_botCrv_cenPt)
    
    visibSph_topCrv = gXform.scale(visibSph_topCrv_unscalled, scale_pln1, scaleFac_top)
    visibSph_botCrv = gXform.scale(visibSph_botCrv_unscalled, scale_pln2, scaleFac_bot)
    
    
    
    # proba
    vertLineOfSight_ln2 = rg.Line( pt_0_0_0_moved, visibSph_topCrv.PointAtStart)
    vertLineOfSight_ln1 = rg.Line( pt_0_0_0_moved, visibSph_midCrv.PointAtStart)
    vertLineOfSight_ln3 = rg.Line( pt_0_0_0_moved, visibSph_botCrv.PointAtStart)
    vertLineOfSightLn_L = [vertLineOfSight_ln1, vertLineOfSight_ln2, vertLineOfSight_ln3]
    
    
    
    visibSph_botCrv_EC_L = gismo_geo.explodeCrv(visibSph_botCrv)
    visibSph_midCrv_EC_L = gismo_geo.explodeCrv(visibSph_midCrv)
    visibSph_topCrv_EC_L = gismo_geo.explodeCrv(visibSph_topCrv)
    
    
    srf_L = []
    srf_divPt_L_at_0_0_0 = []
    for g in xrange(visibSph_botCrv_EC_L.Count):
        
        # c)2) solution with two 'srf' per 60 degrees angle (slower obviously, because there are in total not 12 but 24 srf)
        bot_EC = visibSph_botCrv_EC_L[g]
        mid_EC = visibSph_midCrv_EC_L[g]
        top_EC = visibSph_topCrv_EC_L[g]
        
        
        #srf1 = gismo_geo.srfLoft([bot_EC, mid_EC], 2)[0]
        srf1_id = rs.AddLoftSrf([bot_EC, mid_EC], loft_type=2)  # 'rs.AddLoftSrf' func returns and id.
        srf1 = rs.coercegeometry(srf1_id)  # we are getting brep obj from that id
        srf_L.append( srf1 )
        
        #srf2 = gismo_geo.srfLoft([mid_EC, top_EC], 2)[0]
        srf2_id = rs.AddLoftSrf([mid_EC, top_EC], loft_type=2)  # 'rs.AddLoftSrf' func returns and id.
        srf2 = rs.coercegeometry(srf2_id)  # we are getting brep obj from that id
        srf_L.append( srf2 )
        
        
        # bot U, V divisions
        def caculateV(botOrTop_EC, mid_EC):
            """calcualte Vdiv, based on its ratio of 'srf' width/height"""
            srf1_height_crv = rg.Line(botOrTop_EC.PointAtStart, mid_EC.PointAtStart)
            
            srf_width_height_ratio = mid_EC.GetLength() / srf1_height_crv.Length
            V = int(  precision_ * srf_width_height_ratio  )
            return V
        
        U = precision_  # for both bot and top 'srf'
        Vbot= caculateV(bot_EC, mid_EC)
        Vtop= caculateV(top_EC, mid_EC)
        
        BF1 = srf1.Faces[0]
        srf_divPt_L_, divPtNormal_L_dumm, UV_LL_dumm = gismo_geo.srfDivide(BF1, U, Vbot)
        srf_divPt_L_at_0_0_0.extend( srf_divPt_L_ )
        
        BF2 = srf2.Faces[0]
        srf_divPt_L_, divPtNormal_L_dumm, UV_LL_dumm = gismo_geo.srfDivide(BF2, U, Vtop)
        srf_divPt_L_at_0_0_0.extend( srf_divPt_L_ )
    
    
    
    
    
    # d) take all 'analysisMesh_lifted' mesh vertics as centroids of the future visibility cones
    if (analysisGeo_inputType == "brep"):
        analysisMesh_lifted_MV_L = analysisMesh_lifted.Vertices
        
        originPt_L = [rg.Point3d(analysisMesh_lifted_MV_L[n].X, analysisMesh_lifted_MV_L[n].Y, analysisMesh_lifted_MV_L[n].Z)    for n in xrange(analysisMesh_lifted_MV_L.Count)]
    
    elif (analysisGeo_inputType == "pt"):
        # explode the mesh back to separate circle meshes.
        analysisMesh_lifted_exploded_L = gismo_geo.explodeMesh(analysisMesh_lifted)
        
        # find its cenPts. This will be 'originPt_L'
        originPt_L = []
        for circle_mesh in analysisMesh_lifted_exploded_L:
            cenPt = rg.AreaMassProperties.Compute(circle_mesh).Centroid
            originPt_L.append( cenPt )
    
    
    
    
    # e) start analysis
    GVI_L = [None] * len(originPt_L)
    greenJoinedMesh_all_interscLn_L = []
    greenJoinedMesh_all_NotInterscLn_L = []
    
    for l in xrange(originPt_L.Count):
        
        originPt = originPt_L[l]
        
        # f) move the upper divPt per each 'srf' from (0,0,0) pt to 'originPt'
        moveVec = originPt - pt_0_0_0_moved
        
        srf_moved_L = [gXform.move(srf, moveVec)    for srf in srf_L]
        srf_divPt_L = [gXform.move(srf_divPt_L_at_0_0_0[j], moveVec)    for j in xrange(srf_divPt_L_at_0_0_0.Count)]
        vertLineOfSightLn_moved_L = [gXform.move(ln, moveVec)     for ln in vertLineOfSightLn_L]
        
        
        # g) shoot rays from each moved 'srf_divPt_L'
        GVI_per_originPt_srf_L = []
        
        numOfGreenJoinedMeshHits = 0
        for k in xrange(srf_divPt_L.Count):
            
            divPt = srf_divPt_L[k]
            ray_vec = divPt - originPt
            ray = rg.Ray3d(originPt, ray_vec)
            ray_ln = rg.Line(originPt, divPt)
            
            hitMFI_arr = clr.StrongBox[System.Array[System.Int32]]()
            ray_t = rg.Intersect.Intersection.MeshRay(allMeshesJoined, ray, hitMFI_arr)
            
            if (ray_t >= tol):
                # ray hits 'allMeshesJoined' at some point (we don't need to know which one. It is only important that it intersects)
                
                # check the color of the MF vertices which was hit
                hitMFI_L = gismo_prep.arrayToList2(hitMFI_arr)
                
                ## WARNING ##
                # it can be that 'ray hit the mesh but 'len(hitMFI_L) == 0' because the originPt is exactly at one of the ME of 'allMeshesJoined'. In that case ray will hit the 'allMeshesJoined', but the hit will be on the ME not MF. So 'hitMFI_L' will be empty
                ## WARNING ##
                if (len(hitMFI_L) > 0): 
                    for MFI in hitMFI_L:
                        if (MFI > -1):
                            
                            MF = allMeshesJoined.Faces[MFI]
                            
                            # MF vertex index
                            MVI1 = MF.A
                            MVI2 = MF.B
                            MVI3 = MF.C
                            
                            # mesh vertex color
                            MVC1 = allMeshesJoined_MVC_L[MVI1]
                            MVC2 = allMeshesJoined_MVC_L[MVI2]
                            MVC3 = allMeshesJoined_MVC_L[MVI3]
                            
                            if MF.IsQuad:
                                MVI4 = MF.D
                                MVC4 = allMeshesJoined_MVC_L[MVI4]
                            
                            
                            if (MVC1.G == 0):  # black color has RGB: 0,0,0. So its .G property equals 0
                                continue  # the first intersection are buildings (which are always black). This means that the tree or green area can be behind the building, so it is not visible
                            else:
                                # there is an intersection with 'greenJoinedMesh', but the first intersection has G (green) propery larger than 0, which means it is not 'black' color. Use this mesh intersection
                                ## WARNING ##
                                # we assume that the input buildings are always meshed with 'black' color!!
                                # and that green areas and trees are meshed with non 'black' color (color whose .G propery is larger than 0).
                                
                                # so meshes with only two colors are allowed: 0,0,0 (black) and color which has .G propery larger than 0!
                                ## WARNING ##
                                
                                numOfGreenJoinedMeshHits += 1
                                
                                interscPt = rg.Ray3d.PointAt(ray, ray_t)  # we don't need it
                                
                                if (l == componentIndex):
                                    intersc_ln = rg.Line(originPt, interscPt)
                                    greenJoinedMesh_all_interscLn_L.append( intersc_ln )
                
            
            else:
                # no intersc with 'greenJoinedMesh'
                if (l == componentIndex):
                    intersc_ln = rg.Line(originPt, divPt)
                    
                    # dummy - we will extend the 'intersc_ln', just for testing.
                    extendDist = 150  # dummy value. Just for testing
                    succ = intersc_ln.Extend(0, extendDist)
                    greenJoinedMesh_all_NotInterscLn_L.append( intersc_ln )
            
        if (l == componentIndex):
            #Bake(greenJoinedMesh_all_NotInterscLn_L)
            pass
        
        
        
        
        
        
        GVI_per_originPt_srf__fraction = numOfGreenJoinedMeshHits/srf_divPt_L.Count
        GVI_per_originPt_srf__perc = GVI_per_originPt_srf__fraction * 100
        GVI_per_originPt_srf_L.append( GVI_per_originPt_srf__perc )
    
        
        GVI_for_originPt_avr = sum(GVI_per_originPt_srf_L) / len(GVI_per_originPt_srf_L)
        
        GVI_L[l] = GVI_for_originPt_avr  # dynamic allocation
    
    
    
    GVI_L_avr = sum(GVI_L)/len(GVI_L) # final average GVI for the whole 'analysisMesh_lifted'
    
    
    
    
    
    # h)color 'analysisMesh_lifted'
    
    # legendBakePar_ input
    # deconstruct the "legendBakePar_" input to its parts, so that we can use some of them to color the sphereMesh, for title and legend
    legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, legendFontName, legendFontSize, numDecimals, legendUnit, customTitle, scale, lay, layerColor, layerCategoryName = gismo_prep.read_legendBakePar(legendBakePar)
    
    if (legendBakePar.Branches.Count == 0):
        # 'legendBakePar_' input is empty. Set the 'customColors' to green nuances
        customColors = [System.Drawing.Color.FromArgb(255, 255, 255),
                        System.Drawing.Color.FromArgb(124, 207, 0),
                        System.Drawing.Color.FromArgb(18, 91, 0)]
        
        # recreate 'legendBakePar' input with new 'customColors'
        legendBakePar_LL = [legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, legendFontName, legendFontSize, numDecimals, legendUnit, customTitle, scale, lay, layerColor, layerCategoryName]
        legendBakePar = Grasshopper.DataTree[object]()
        for i,item in enumerate(legendBakePar_LL):
            if isinstance(item, list):
                legendBakePar.AddRange(item, Grasshopper.Kernel.Data.GH_Path(i))
            else:
                legendBakePar.AddRange([item], Grasshopper.Kernel.Data.GH_Path(i))
    
    
    # colors for 'analysisMesh_lifted'
    colors = gismo_prep.numberToColor(GVI_L, customColors, minValue, maxValue)
    
    if (analysisGeo_inputType == "brep"):
        # color the terrainMesh with generated colors for every analysisType except 6,7,8,9 types
        for f in xrange(len(analysisMesh_lifted.Vertices)):
            analysisMesh_lifted.VertexColors.Add(colors[f])
        
        analysisMesh_lifted_L = [analysisMesh_lifted]
    
    
    elif (analysisGeo_inputType == "pt"):
        
        analysisMesh_lifted_L = []
        for h in xrange(analysisMesh_lifted_exploded_L.Count):
            
            circle_mesh = analysisMesh_lifted_exploded_L[h]
            color = colors[h]
            
            for f in xrange(len(circle_mesh.Vertices)):
                circle_mesh.VertexColors.Add(color)
                analysisMesh_lifted_L.append( circle_mesh )
    
    
    
    
    
    # legend
    legendUnit = "perc."
    legendMesh, legendStartPlane = gismo_geo.createLegend(analysisMesh_lifted_L, GVI_L, legendBakePar, legendUnit)
    
    # title
    title_str = "Green View Index"
    titleMesh, titleOriginPt, titleTextSize = gismo_prep.createTitle("mesh", analysisMesh_lifted_L, [title_str], customTitle, textSize=legendFontSize, fontName=legendFontName)
    
    
    
    
    
    
    # baking, grouping
    if bakeIt_:
        lay = "gridSize={}_offsetDist={}_vertFOVangles={},{}".format( gridSize_, analysisHeight, vertUpFOVAngleD, vertDownFOVAngleD )
        
        layParentName = "GISMO"; laySubName = "ANALYSIS"; layerCategoryName = "GVI"; newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(181,230,29)  # green
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layerIndex, lay_dummy = gismo_prep.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, lay, laySubName_color, layerColor, legendBakePar_) 
        
        geometryToBakeL = analysisMesh_lifted_L + [titleMesh, legendMesh]
        
        geometry_id_L = gismo_prep.bakeGeometry(geometryToBakeL, layerIndex)
        
        
        # grouping
        groupIndex = gismo_prep.groupGeometry(lay, geometry_id_L)
    
    
    
    
    # hide origin, legendPlane output
    ghenv.Component.Params.Output[6].Hidden = True
    ghenv.Component.Params.Output[8].Hidden = True
    
    gc.collect()
    
    
    return analysisMesh_lifted_L, GVI_L, GVI_L_avr, titleMesh, titleOriginPt, legendMesh, legendStartPlane


def printOutput(analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, precision):
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "GVI component results successfully completed %s!" % bakedOrNot
    printOutputMsg = \
    """
Input data:

Number of '_treesAndGreenAreas' input items: {}
Number of 'context_' input items: {}
Number of '_analysisGeo' input items: {}
'_analysisGeo' input type: {}

gridSize: {}
offsetDist: {}
vertical Up FOV angle: {}
vertical Down FOV angle: {}
precision: {}
    """.format(len(_treesAndGreenAreas), len(context_), len(_analysisGeo), analysisGeo_inputType, gridSize_, offsetDist_, vertUpFOVAngleD, vertDownFOVAngleD, precision)
    print resultsCompletedMsg
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gXform = sc.sticky["gismo_Transfrom"]()
        gismo_prep = sc.sticky["gismo_Preparation"]()
        gismo_geo = sc.sticky["gismo_CreateGeometry"]()
        
        analysisMesh_lifted, analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, validInputData, printMsg = checkInputData(_treesAndGreenAreas, context_, _analysisGeo, gridSize_, offsetDist_, vertFOVangles_, precision_)
        if validInputData:
            if _runIt:
                GVI, GVIvalues, GVIvaluesAvr, title, titleOriginPt, legend, legendPlane = main(_treesAndGreenAreas, context_,  analysisMesh_lifted, analysisGeo_inputType, offsetDist_, vertUpFOVAngleD, vertDownFOVAngleD, legendBakePar_)
                printOutput(analysisGeo_inputType, vertUpFOVAngleD, vertDownFOVAngleD, precision_)
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the GVI component"
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
