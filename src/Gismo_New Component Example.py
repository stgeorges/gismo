# distance from point to sphere
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2019, Your First and Last name <youremail@address.com>
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
[Gismo welcomes new developers. Even a single new component can benefit and make Gismo a better plugin.]
[New components are welcome as long as they follow the code template.]
[This component provides the code template for possible new Gismo component which calculates the distance between a point ("_point" input) and a sphere.]
[There will be explanations of parts of code, like how to check inputs, how to create a title, a legend... Explanations are written in square brackets. For example: [this is explanation].]
[Rhinoscriptsyntax is used as more friendly, but you can also write directly in RhinoCommon, if you want to. Still rhinoscriptsyntax is fine.]
-
Provided by Gismo 0.0.3
    
    input:
        _point: A reference point which will be used to measure the distance from it to a sphere.
                [This is a required input. All required inputs, have an underscore on the left side of its name]
        _sphereCenter: A point representing the center of a sphere.
                       [This is a required input too: it has an underscore on the left side of its name]
        sphereRadius_: A number which defines the radius of the sphere.
                       [This is an optinal input. It has an underscore on the right side of its name]
                       -
                       If nothing added to this input, shpereRadius_ will be set to: 10 by default.
        legendBakePar_: Optional legend parameters from the Gismo "Legend Bake Parameters" component.
                        Use this input to control the look of the "legend" and "title" outputs. And the colors of the "sphere" output.
                        [This is an optinal input. It has an underscore on the right side of its name]
        bakeIt_: Set to "True" to bake the shapes geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
                [This input runs the component. It is used in cases when component is a bit heavier to run. For example: it take a couple of seconds for the component to run.]
                [If component runs quicker than that, then you do not even need this input.]
    
    output:
        readMe!: ...
                 [This output is used for debugging. It shows the error message in case something is wrong with the component.]
        distances: A list of distances between the _point and a sphere.
                   -
                   In Rhino document units (meters, feets...).
        sphere: A sphere created from "_sphereCenter" and "shpereRadius_" inputs.
                The sphere is colored in a way that colors correspond to distances between the sphere and _point input.
        title: Final geometry title.
               You can change it by using the "legendBakePar_" input (and Gismo "Legend Bake Parameters" component).
        legend: A legend corresponding to distances between the _point and a sphere.
"""

ghenv.Component.Name = "Gismo_New Component Example"   # [this string defines component's Name. It should be something like: "Gismo_Distance Point To Sphere"]
ghenv.Component.NickName = "NewComponentExample"   # [this string defines component's Nickname. It should be something like: "DistancePointToSphere"]
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"   # [this line defines component's version and date]
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application   # [ do not change this line. It enables using both component icon and component name]
ghenv.Component.Category = "Gismo"   # [do not change this line. It assigns component to the "Gismo" plugin]
ghenv.Component.SubCategory = "3 | More"   # [this string defines the specific tab to which component belongs]
# [the line below defines the version and date of "Gismo Gismo" component which is compatible with this component. You can simply set both the version and the date to the latest "Gismo Gismo" component's version and date]
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"   # [this string defines tab's row. For example: "1" means that, component will be located in the first row of upper defined "3 | More" tab]
except: pass

# [we first import some general modules:]
import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import Rhino

# [then we start writing the code a series of functions:]
def checkInputData(point, sphereCenter, sphereRadius):
    
    # [a) check required inputs first]
    # [if either of required inputs (_point or _sphereCenter) is missing, we stop the function and the component like this:]
    if (point == None):
        point = sphereCenter = sphereRadius = None
        validInputData = False
        printMsg = "Please add a point to the _point input."
        return point, sphereCenter, sphereRadius, validInputData, printMsg
    
    # [now we do the same check for _sphereCenter input:]
    if (sphereCenter == None):
        point = sphereCenter = sphereRadius = None
        validInputData = False
        printMsg = "Please add a point to the _sphereCenter input."
        return point, sphereCenter, sphereRadius, validInputData, printMsg
    
    
    # [b) check optional inputs]
    if (sphereRadius == None):
        sphereRadius = 10
    
    # [we can additionally set the valid range of _shpereRadius like this:]
    if (sphereRadius < 1) or (sphereRadius > 100):
        point = sphereCenter = sphereRadius = None
        validInputData = False
        printMsg = "_sphereRadius input accepts only radii from 1 to 100."
        return point, sphereCenter, sphereRadius, validInputData, printMsg
    
    
    # [if everything is ok with the upper three inputs, then we return them from this function:]
    
    validInputData = True
    printMsg = "ok"
    
    return point, sphereCenter, sphereRadius, validInputData, printMsg


def main(point, sphereCenter, sphereRadius, legendBakePar):
    # [this is the main function which will calculate the distances from the "point" to the sphere.]
    # [to do this we need to actually calculate the distances between the "point" and points on a sphere.]
    # [these points on a sphere can be vertices of a mesh created from that sphere. So we will first create a sphere, and then create a mesh from that sphere.]
    
    # [create a sphere:]
    sphereId = rs.AddSphere(sphereCenter, sphereRadius)
    sphereBrep = rs.coercegeometry(sphereId)  # ["shpereId" represent and id of a sphere. To get the shpere geometry: we use the "rs.coercegeometry" function:]
    
    # [create a mesh from sphereBrep. There is no rhinoscriptsyntax function which converts a brep to a mesh, so we have to use RhinoCommon one instead:]
    sphereMesh = Rhino.Geometry.Mesh.CreateFromBrep(sphereBrep)[0]  # [the "[0]" at the end takes a single mesh, because "Rhino.Geometry.Mesh.CreateFromBrep" returns a list]
    
    # [now we calculate the distances between the "point" and "sphereMesh" vertices:]
    distances = []
    meshVertices = sphereMesh.Vertices  # [get mesh vertices]
    for vertex in meshVertices:
        distance = rs.Distance(point, vertex)  # [rhinoscriptsyntax function to calculate the distance between a "point" and each mesh vertex]
        distances.append(distance)
    
    
    # deconstruct the "legendBakePar_" input to its parts, so that we can use some of them to color the sphereMesh, for title and legend
    legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, legendFontName, legendFontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = gismo_preparation.read_legendBakePar(legendBakePar)
    
    # [now we color our mesh, according to the upper "ditances" list:]
    meshColors = gismo_preparation.numberToColor(distances, customColors, minValue, maxValue)
    coloredSphereMesh = gismo_geometry.colorMeshVertices(sphereMesh, meshColors)
    
    
    # [that's it! now we can create the "title" and "legend" outputs:]
    # title
    titleLabelText = "Distance between a point and a sphere"  # [this is the text of the title]
    title, titleStartPt, titleTextSize = gismo_preparation.createTitle("mesh", [sphereMesh], [titleLabelText], customTitle, textSize=legendFontSize, fontName=legendFontName)
    
    # legend
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits() 
    legendUnit = unitSystemLabel
    legend, legendPlane = gismo_geometry.createLegend([sphereMesh], distances, legendBakePar_, legendUnit)
    
    
    return distances, sphereMesh, title, legend


def bakingGrouping(point, sphereCenter, sphereRadius, sphere, title, legend):
    # [in case the "bakeIt_" input is set to "True", this function will bake the outputs]
    
    # a) baking
    # [we first create the layerName and we set the point, sphereCenter, sphereRadius inputs to 2 decimals:]
    layerName = "point=%0.2f,%0.2f,%0.2f_sphereCenter=%0.2f,%0.2f,%0.2f_sphereRadius=%0.2f" % (point.X, point.Y, point.Z, sphereCenter.X, sphereCenter.Y, sphereCenter.Z, sphereRadius)
    
    # [the following four lines define Parent, SubLayer and CategoryLayer names and their colors:]
    layParentName = "GISMO"; laySubName = "DISTANCE_CALCULATOR"; layerCategoryName = "POINT_TO_SPHERE"
    newLayerCategory = False
    laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # green
    layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
    
    # [the line below creates the layer for the upper set up parameters:]
    layerIndex, layerName_dummy = gismo_preparation.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, layerName, laySubName_color, layerColor, legendBakePar_) 
    
    geometryToBakeL = [point, sphereCenter, sphere, title, legend]  # [we define what we would like to bake. The order of variables is not important]
    geometryIds = gismo_preparation.bakeGeometry(geometryToBakeL, layerIndex)  # [this line actually performs the baking. And returns the ids of the baked geometry. We will need these for grouping]
    
    # b) grouping of baked geometry
    # [sometimes we want to group our baked geometry. This is what the line below does. If you do not want to group the baked geometry, just delete this line:]
    groupIndex = gismo_preparation.groupGeometry(layerName, geometryIds)


def printOutput(point, sphereCenter, sphereRadius):
    # [the point of this function is to print the used inputs to the "readMe!" output. It can be useful if a user reports an error with a component, and posts a screenshot of a message comming from the "readMe!" output]
    
    if bakeIt_ == True:
        bakedOrNot = "and baked "
    elif bakeIt_ == False:
        bakedOrNot = ""
    resultsCompletedMsg = "New Component Example component successfully ran %s!" % bakedOrNot
    
    printOutputMsg = \
    """
Input data:

Point: %s
Sphere center: %s
Sphere radius: %s
    """ % (point, sphereCenter, sphereRadius)
    print resultsCompletedMsg
    print printOutputMsg


# [the following four lines check if "Gismo Gismo" component has been ran first, and if this component is compatible with "Gismo Gismo" component:]
level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning  # [do not change this line 
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        # [two lines before enable importing two classes from "Gismo Gismo" component: Preparation and CreateGeometry class. Once they are imported we can call their methods inside our functions above:]
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        gismo_geometry = sc.sticky["gismo_CreateGeometry"]()
        
        # [we finally start calling the functions we wrote above. First we call the "checkInputData" to check inputs:]
        point, sphereCenter, sphereRadius, validInputData, printMsg = checkInputData(_point, _sphereCenter, sphereRadius_)
        if validInputData:  # [if inputs are valid we continue further]
            if _runIt:  # [all inputs are OK, so we can run our component]
                distances, sphere, title, legend = main(point, sphereCenter, sphereRadius, legendBakePar_)
                if bakeIt_: bakingGrouping(point, sphereCenter, sphereRadius, sphere, title, legend)  # [this line is for baking the results]
                printOutput(point, sphereCenter, sphereRadius)
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the New Component Example component"
        else:  # [if inputs are not valid then we stop the component, and raise the warning. This check process is repeated for other functions above:]
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)


# [And that's it!!]
# [It wasn't really that hard. We learned how to check if "Gismo Gismo" component is ran, its version compatibility,
# [ check inputs, perform the actual task that the component is suppose to do, color the resulting sphere,
# [ create a title and a legend, bake the results, and print the inputs to "readMe!" ouput.]

# [ To change the icon of the component, make a 24x24 pixels .png image, and drag and drop it onto the current one.]

# [If you would like to create a new component for Gismo plugin, and you have some issues, you can report them on: http://www.grasshopper3d.com/group/gismo, 
# [ or send an email to djordjedspasic@gmail.com. Do not hesitate to do that.]
