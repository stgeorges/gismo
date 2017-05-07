# create legend
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
Use this component to create a legend for particular geometry and recolor the geometry based on that legend.
-
Provided by Gismo 0.0.2
    input:
        _values: A list of numerical or textual values for which the legend needs to be created.
        _analysisGeometry: The geometry for which the legend needs to be created based on upper "_values" input.
                           It can be:
                           -
                           a) A list of meshes/surfaces/polysurfaces. In that case their number needs to correspond to the number of items added to the "_values" input.
                           b) A single mesh. In that case the number of mesh vertices needs to correspond to the number of items added to the "_values" input.
        legendBakePar_: Optional legend parameters from the Gismo "Legend Bake Parameters" component.
        bakeIt_: Set to "True" to bake the terrain analysis geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        coloredGeometry: "_analysisGeometry" colored for the "_values" input.
        title: Title.
               By default it is set to "undefined title". Use the "Legend Bake Parameters" component's "customTitle_" input to change it.
        titleOriginPt: Title base point, which can be used to move the "title" geometry with grasshopper's "Move" component.
                       -
                       Connect this output to a Grasshopper's "Point" parameter in order to preview the point in the Rhino scene.
        legend: Legend geometry of the "coloredGeometry" output.
        legendPlane: Legend starting plane, which can be used to move the "legend" geometry with grasshopper's "Move" component.
                     -
                     Connect this output to a Grasshopper's "Plane" parameter in order to preview the "legendPlane" plane in the Rhino scene.
"""

ghenv.Component.Name = "Gismo_Create Legend"
ghenv.Component.NickName = "CreateLegend"
ghenv.Component.Message = "VER 0.0.2\nMAY_07_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.2\nMAY_07_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import System
import Rhino


def main(values, analysisGeometry, legendBakePar):
    
    # legend and title
    if (len(values) == 0)  or  ((len(values) == 1) and (values[0] == None)):
        coloredJoinedMeshL = title = titleOriginPt = legend = legendPlane = customCellNumbers = None
        validInputData = False
        printMsg = "Please add a list of \"_values\" which correspond to each \"_analysisGeometry\" item or mesh vertex in case \"_analysisGeometry\" is a mesh."
        return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg
    
    if (len(analysisGeometry) == 0)  or  ((len(analysisGeometry) == 1) and (analysisGeometry[0] == None)):
        coloredJoinedMeshL = title = titleOriginPt = legend = legendPlane = customCellNumbers = None
        validInputData = False
        printMsg = "Please add the geometry to the \"_analysisGeometry\"input.\n\n" + \
                   "The geometry can be a single mesh, where the number of items added to the upper \"_values\" input corresponds to the number of mesh verticies. Or,\n" + \
                   "More than one mesh or surface/polysurface, where the number of items added to the upper \"_values\" input corresponds to the number of added meshes/surfaces/polysurfaces."
        return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg
    
    
    if (len(analysisGeometry) == 1):
        if (type(analysisGeometry[0]) == Rhino.Geometry.Mesh):
            numOfMeshVertices = len(list(analysisGeometry[0].Vertices))
            if (len(values) > 1) and (len(values) != numOfMeshVertices):
                print "1"
                coloredJoinedMeshL = title = titleOriginPt = legend = legendPlane = customCellNumbers = None
                validInputData = False
                printMsg = "The number of items added to the \"_values\" input (%s), and the number of vertices of the mesh added to the \"_analysisGeometry\" (%s) input is not the same." % (len(values), numOfMeshVertices)
                return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg
        elif (type(analysisGeometry[0]) != Rhino.Geometry.Mesh):
            if (len(values) != len(analysisGeometry)):
                print "2"
                coloredJoinedMeshL = title = titleOriginPt = legend = legendPlane = customCellNumbers = None
                validInputData = False
                printMsg = "The number of items added to the \"_values\" (%s) and \"_analysisGeometry\" (%s) inputs is not the same." % (len(values), len(analysisGeometry))
                return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg
    
    elif (len(analysisGeometry) > 1):
        if (len(values) != len(analysisGeometry)):
            coloredJoinedMeshL = title = titleOriginPt = legend = legendPlane = customCellNumbers = None
            validInputData = False
            printMsg = "The number of items added to the \"_values\" (%s) and \"_analysisGeometry\" (%s) inputs is not the same." % (len(values), len(analysisGeometry))
            return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg
    
    
    
    if _runIt:
        # deconstruct the "legendBakePar_"
        legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, legendFontName, legendFontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = gismo_preparation.read_legendBakePar(legendBakePar)
        
        # check if "_values" are numbers or strings
        values2 = []
        for v in values:
            if (type(v) == System.String):
                # one of the item in "_values" input is a string. Assume all of them are
                valuesAreStrings = True
                break
        else:
            # neither value in the "_values" input is a string: meaning they are all numbers (floats or integers)
            valuesAreStrings = False
        
        if (valuesAreStrings == True):
            values2_with_indices = {}
            customCellNumbers = []
            values2 = []
            index = 0
            for v in values:
                if (values2_with_indices.has_key(v) == False):
                    index += 1
                    values2_with_indices[v] = index
                    customCellNumbers.append(v)
                    values2.append(index)
                elif (values2_with_indices.has_key(v) == True):
                    values2.append(values2_with_indices[v])
        
        elif (valuesAreStrings == False):
            values2 = values
            customCellNumbers = []
        
        
        # create mesh colors
        meshColorsPerEachGeometryAnalysisItem = gismo_preparation.numberToColor(values2, customColors, minValue, maxValue)
        
        # create a mesh from analysisGeometry
        coloredJoinedMeshL = []
        
        for analysisGeometryIndex, item in enumerate(analysisGeometry):
            joinedMesh = Rhino.Geometry.Mesh()
            if (type(item) == Rhino.Geometry.Mesh):
                joinedMesh.Append(item)
            elif (type(item) == Rhino.Geometry.Brep):
                meshes = Rhino.Geometry.Mesh.CreateFromBrep(item)
                for mesh2 in meshes:
                    joinedMesh.Append(mesh2)
            else:
                # the "item" is not a mesh nor a brep.
                coloredJoinedMeshL = title = titleOriginPt = legend = legendPlane = customCellNumbers = None
                validInputData = False
                printMsg = "One of the items you added to the \"_analysisGeometry\" input is not a mesh, nor a surface or polysurface.\n" + \
                           "The \"_analysisGeometry\" input only accepts those three geometry types: mesh, surface, polysurface."
                return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg
            
            
            # create mesh colors for each "_analysisGeometry"
            if (len(analysisGeometry) == 1) and (type(analysisGeometry[0]) == Rhino.Geometry.Brep):
                # there is only a single item in the "_values", so the once the brep is converted to a mesh all of mesh vertices need to be painted with that single item's color
                meshColorsForSpecificGeometryAnalysisItem = [meshColorsPerEachGeometryAnalysisItem[analysisGeometryIndex]  for i in range(joinedMesh.Vertices.Count)]
            elif (len(analysisGeometry) == 1) and (type(analysisGeometry[0]) == Rhino.Geometry.Mesh):
                # each item in the "_values" corresponds to the color of the mesh vertex
                meshColorsForSpecificGeometryAnalysisItem = meshColorsPerEachGeometryAnalysisItem
            elif (len(analysisGeometry) > 1):  # and (type(analysisGeometry[0]) == Rhino.Geometry.Brep)
                # there is the same number of items in both "_values" and "_analysisGeometry" inputs. They all correspond to each vertex color of the mesh
                meshColorsForSpecificGeometryAnalysisItem = [meshColorsPerEachGeometryAnalysisItem[analysisGeometryIndex]  for i in range(joinedMesh.Vertices.Count)]
            #elif (len(analysisGeometry) > 1) and (type(analysisGeometry[0]) == Rhino.Geometry.Mesh)
                # this combination is not allowed
            
            # color the mesh
            coloredJoinedMesh = gismo_geometry.colorMeshVertices(joinedMesh, meshColorsForSpecificGeometryAnalysisItem)  # colored mesh
            coloredJoinedMeshL.append(coloredJoinedMesh)
        
        
        # title
        titleLabelText = "undefined title"
        title, titleOriginPt, titleTextSize = gismo_preparation.createTitle("mesh", coloredJoinedMeshL, [titleLabelText], customTitle, textSize=legendFontSize, fontName=legendFontName)
        
        # legend
        legend, legendPlane = gismo_geometry.createLegend(coloredJoinedMeshL, values2, legendBakePar, legendUnit, customCellNumbers)
    
    else:
        coloredJoinedMeshL = title = titleOriginPt = legend = legendPlane = customCellNumbers = None
        validInputData = True
        printMsg = "All inputs are ok. Please set \"_runIt\" to True, in order to run the Create Legend component"
        return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg
    
    
    # hide titleOriginPt, legendPlane output
    ghenv.Component.Params.Output[3].Hidden = True
    ghenv.Component.Params.Output[5].Hidden = True
    
    print "Create Legend component successfully ran!"
    validInputData = True
    printMsg = "ok"
    
    return coloredJoinedMeshL, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg


def bakingGrouping(customCellNumbers, values, coloredJoinedMeshL, title, legend):
    
    # define layers
    if (len(customCellNumbers) > 0):
        # _values are strings
        layerName = "values=%s" % "_".join(customCellNumbers)[:30]  # join all strings in the "customCellNumbers" and limit that final joined string to 30 characters
    elif (len(customCellNumbers) == 0):
        # _values are numbers
        layerName = "values_sum=%0.2f" % sum(values)
    
    layParentName = "GISMO"; laySubName = "CREATE_LEGEND_AND_RECOLOR_MESH"; layerCategoryName = "NEW"
    newLayerCategory = False
    laySubName_color = System.Drawing.Color.FromArgb(125,38,205)  # purple
    layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
    # create the new layer
    layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor, legendBakePar_) 
    
    # bake
    geometryToBakeL = coloredJoinedMeshL + [title, legend]
    geometryIds = gismo_preparation.bakeGeometry(geometryToBakeL, layerIndex)
    
    # group
    groupIndex = gismo_preparation.groupGeometry(layerName, geometryIds)


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_geometry = sc.sticky["gismo_CreateGeometry"]()
        
        if _runIt:
            coloredGeometry, title, titleOriginPt, legend, legendPlane, customCellNumbers, validInputData, printMsg = main(_values, _analysisGeometry, legendBakePar_)
            if not validInputData:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
            else:
                if bakeIt_: bakingGrouping(customCellNumbers, _values, coloredGeometry, title, legend)
        else:
            print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Create Legend component"
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
