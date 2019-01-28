# Rhino boolean union
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2019, Djordje Spasic <djordjedspasic@gmail.com>
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
Grasshopper's "Solid Union" component may sometimes fail to perform boolean union of the 3d buildings coming from Gismo "OSM shapes" component.
In that case use this component, which replicated Rhino's _BooleanUnion command.
-
However, this component works much better on Rhino 5, as Rhino 5 allowed creation of soldis with non-manifold edges!
-
Provided by Gismo 0.0.3
    
    input:
        _threeDeeShapes: Plug in the "threeDeeShapes" output from the Gismo "OSM 3D" component
        closedSolid_: Set to "True" to make all the union solids closed.
                      -
                      If not supplied default value "True" will be used.
        bakeIt_: Set to "True" to bake the extruded _shape geometry into the Rhino scene.
                 The geometry will be grouped. To ungroup it, select it and call the "Ungroup" Rhino command.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        threeDeeShapesUnioned: Boolean unioned "_threeDeeShapes" input
        -
        This component works much better on Rhino 5, as Rhino 5 allowed creation of soldis with non-manifold edges!
"""

ghenv.Component.Name = "Gismo_Rhino Boolean Union"
ghenv.Component.NickName = "RhinoBooleanUnion"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import Rhino



def main(threeDeeShapes):
    if (not threeDeeShapes) or (_threeDeeShapes[0] == None):
        threeDeeShapes_allClosedPolysrf_objs = None
        validInput = False
        printMsg = "Input closed 3d objects into \"_threeDeeShapes\" input to boolean union them."
        return threeDeeShapes_allClosedPolysrf_objs, validInput, printMsg
    
    if (_runIt == False):
        threeDeeShapes_allClosedPolysrf_objs = None
        validInput = False
        printMsg = "Set the \"_runIt\" input to \"True\" in order to run the component."
        return threeDeeShapes_allClosedPolysrf_objs, validInput, printMsg
    
    
    
    # perform boolean union of the 3d buildings, and make them all "closed polysurfaces"
    
    rs.EnableRedraw(False)
    
    errorMsg = "Something went wrong. Open a new topic at:\nhttps://www.grasshopper3d.com/group/gismo/forum\n and attach your .gh file."
    
    threeDeeShapes_unboolean_rhino_ids = []
    
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    # add all breps to Rhino document
    for i,threeDeeShape in enumerate(_threeDeeShapes):
        rhino_ids = Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(threeDeeShape)
        threeDeeShapes_unboolean_rhino_ids.append(rhino_ids)
    
    # perform Rhino BooleanUnion
    selIds = ""
    for rhino_id in threeDeeShapes_unboolean_rhino_ids:
        selIds += "_SelId %s " % rhino_id
    
    commandString1 = "_-BooleanUnion " + selIds + "_Enter "
    
    echo1 = False
    success1 = rs.Command(commandString1, echo1)
    if (success1 == False):
        print errorMsg
    
    
    # explode and rejoin the shape in case it is not a "closed solid"
    if closedSolid_:
        ######################
        if (rs.ContextIsGrasshopper() == True):
            # document is set to sc.doc = ghdoc (for some reason. For example the component was copy pasted from one definition to another)
            sc.doc = Rhino.RhinoDoc.ActiveDoc
        ######################
        
        threeDeeShapes_someOpenPolysrf_rhino_ids = rs.LastCreatedObjects(select=True)
        rs.UnselectAllObjects()
        
        global threeDeeShapes_allClosedPolysrf_rhino_ids
        threeDeeShapes_allClosedPolysrf_rhino_ids = []
        for rhino_id2 in threeDeeShapes_someOpenPolysrf_rhino_ids:
            threeDeeShapes_someOpenPolysrf = rs.coercegeometry(rhino_id2)
            if (type(threeDeeShapes_someOpenPolysrf) == Rhino.Geometry.Brep):  # do not include the textDot's which can be created in Rhino 6 once the "_BooleanUnion" command fails
                if (threeDeeShapes_someOpenPolysrf.IsSolid == False):  # explode only "open polysurfaces" fron Rhino
                    """
                    # method 1: use grasshopper's Rhino.Gemometry.JoinBreps()  - not working!!!
                    tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
                    threeDeeShapes_closedPolysrf = Rhino.Geometry.Brep.JoinBreps( [rs.coercegeometry(rhino_id2)], tol)[0]
                    threeDeeShapes_closedPolysrf_rhino_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(threeDeeShapes_closedPolysrf)
                    threeDeeShapes_allClosedPolysrf_rhino_ids.append( threeDeeShapes_closedPolysrf_rhino_id )
                    """
                    
                    
                    # method 2: use Rhino's "_Explode, _Join" commands
                    commandString2 = "_-SelId %s _Explode _Join _Enter" % rhino_id2
                    echo2 = False
                    success2 = rs.Command(commandString2, echo2)
                    threeDeeShapes_joined_rhino_ids = rs.LastCreatedObjects(select=False)
                    threeDeeShapes_allClosedPolysrf_rhino_ids.extend( threeDeeShapes_joined_rhino_ids )
                    rs.UnselectAllObjects()
                    
                    if (success2 == False):
                        print errorMsg
                elif (threeDeeShapes_someOpenPolysrf.IsSolid == True):  # no need to explode it. It is "closed polysurface"
                    threeDeeShapes_allClosedPolysrf_rhino_ids.append(rhino_id2)
    
    
    # delete all objects from rhino working space
    threeDeeShapes_allClosedPolysrf_objs = [rs.coercegeometry(id)  for id in threeDeeShapes_allClosedPolysrf_rhino_ids]
    print "threeDeeShapes_allClosedPolysrf_rhino_ids: ", threeDeeShapes_allClosedPolysrf_rhino_ids
    print "-------------------------------------------"
    print "-------------------"
    #rs.SelectObjects(threeDeeShapes_allClosedPolysrf_rhino_ids)
    for rhino_id3 in threeDeeShapes_allClosedPolysrf_rhino_ids:
        try:
            rs.DeleteObject(rhino_id3)
        except:
            # for some reason the "Parameter must be a Guid or string representing a Guid" error is thrown
            Rhino.RhinoDoc.ActiveDoc.Objects.Delete(rhino_id3, quiet=False)
    
    
    sc.doc = ghdoc
    
    
    if bakeIt_:
        for rhino_id4 in threeDeeShapes_allClosedPolysrf_objs:
            final_id = Rhino.RhinoDoc.ActiveDoc.Objects.AddBrep(rhino_id4)
    
    
    rs.EnableRedraw(True)
    
    
    validInput = True
    printMsg = "ok"
    return threeDeeShapes_allClosedPolysrf_objs, validInput, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
threeDeeShapesUnioned, validInput, printMsg = main(_threeDeeShapes)
if not validInput:
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
