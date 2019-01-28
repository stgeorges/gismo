# legend bake parameters
#
# Gismo is a plugin for GIS Environmental Analysis (GPL) started by Djordje Spasic.
# 
# This file is part of Gismo.
# 
# Copyright (c) 2019, Djordje Spasic <djordjedspasic@gmail.com>
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to define the parameters important for legend and baking.
Any component which has a "legendBakePar_" input can be used to define these.
-
Provided by Gismo 0.0.3
    input:
        legendStyle_: The following legend cell styles are supported:
                      -
                      0 - rectangular
                      1 - filleted
                      2 - elliptical
                      3 - rhombus
                      -
                      If nothing supplied to this input, legendStyle_ = 0 (rectangular legend cells) will be used as a default value.
        legendPlane_: Starting legend plane.
                      -
                      If nothing added to this input, the plane will set by default to XY plane, with origin being the right most point of the geometry for which the legend is created.
        maxValue_: Legend's maximal value.
                   -
                   If nothing added to this input, the maximal value found during particular analysis (for which the legend is created) will be used.
        minValue_: Legend's minimal value.
                   -
                   If nothing added to this input, the minimal value found during particular analysis (for which the legend is created) will be used.
        customColors_: A list of colors from which a legend will be created.
                       Use Grasshopper's "Colour Swatch" parameter, or Ladybug's "Gradient Library" component to define them.
                       -
                       If nothing added to this input, default color gradient blue-green-red will be used as default.
        numLegendCells_: The number of legend cells.
                         -
                         If nothing added to this input, 12 legend cells will be used by default.
        fontName_: Name of the legend font. Some component may enable using this input to change the font name of component's title as well.
                   -
                   If nothing added to this input, "Verdana" font name will be used by default.
        fontSize_: Size of the legend font. Some component may enable using this input to change the font size of component's title as well.
                   -
                   If nothing added to this input, fontSize will be calculated based on the size of your component's geometry (3 times smaller than geometry's bounding box width).
        numDecimals_: The number of legend result decimals.
                      You can choose from 0 (no decimals - integers only) to 6 decimals.
                      -
                      If nothing added to this input, 2 decimals will be used as default.
        legendUnit_: A custom legend unit.
                     -
                     If nothing added to this input, component's default legend unit will be used.
        customTitle_: A custom title for component.
                      Use "\n" python characters if you would like your custom title to be separated into multiple lines.
                      -
                      If nothing added to this input, component's default title will be used.
        scale_: The scale of the whole legend.
                -
                If nothing added to this input, scale of 1.0 will be used as default.
        layerName_: A custom name of the final layer to which the geometry will be baked.
                    -
                    If nothing added to this input, component's default layer name will be used.
        layerColor_: A custom color of the final layer to which the geometry will be baked.
                    -
                    If nothing added to this input, black color will always be used as default.
        layerCategoryName_: A custom name of the layer category.
                            -
                            If nothing added to this input, component's default category name will be used.
    
    output:
        readMe!: ...
        legendBakePar: A list of all Legend Bake Parameters. Plug it to any component which has the "legendBakePar_" input.
"""

ghenv.Component.Name = "Gismo_Legend Bake Parameters"
ghenv.Component.NickName = "LegendBakeParameters"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import System


def checkInputData(legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName):
    
    # legend and title
    if (legendStyle == None):
        legendStyle = 0  # rectangle cells
    
    if (legendPlane == None):
        legendPlane = None  # pick bounding box bottom right corner point
    
    if (maxValue == None):
        maxValue = None  # pick the largest value
    
    if (minValue == None):
        minValue = None  # pick the smallest value
    
    if (len(customColors) == 0):
        customColors = []
    elif (len(customColors) == 1):
        legendBakePar_DataTree = legendBakePar_LL = None
        validInputData = False
        printMsg = "The \"customColors_\" input needs to have at least two colors.\n" + \
                   "Add at least one more color to this input."
        return legendBakePar_DataTree, legendBakePar_LL, validInputData, printMsg
    
    if (numLegendCells == None):
        numLegendCells = 12
    
    if (fontName == None):
        fontName = "Verdana"
    
    if (fontSize == None):
        fontSize = None  # calculate it according to the bounding box length
    
    if (numDecimals == None):
        numDecimals = 2
    
    if (legendUnit == None):
        legendUnit = None  # use the legendUnit defined by the component
    
    if (scale == None):
        scale = 1
    
    
    # baking
    if (layerName == None):
        layerName = None  # use layerName defined by the component
    
    if (layerColor == None):
        layerColor = None  # no layer category will be created
    
    if (layerCategoryName == None):
        layerCategoryName = None  # no layer category will be created
    
    
    legendBakePar_LL = [legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName]
    legendBakePar_DataTree = Grasshopper.DataTree[object]()
    for i,item in enumerate(legendBakePar_LL):
        if isinstance(item, list):
            legendBakePar_DataTree.AddRange(item, Grasshopper.Kernel.Data.GH_Path(i))
        else:
            legendBakePar_DataTree.AddRange([item], Grasshopper.Kernel.Data.GH_Path(i))
    
    
    validInputData = True
    printMsg = "ok"
    
    return legendBakePar_DataTree, legendBakePar_LL, validInputData, printMsg


def printOutput(legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName):
    
    if layerColor != None:
        printLayerColor = (int(layerColor.R),int(layerColor.G),int(layerColor.B))
    else:
        printLayerColor = None
    
    printOutputMsg = \
    """
Input data:

legendStyle: %s
legendPlane: %s
maxValue: %s
minValue: %s
customColors: %s
numLegendCells: %s
fontName: %s
fontSize: %s
numDecimals: %s
legendUnit: %s
customTitle: %s
scale: %s

layerName: %s
layerColor: %s
layerCategoryName: %s
    """ % (legendStyle, legendPlane, maxValue, minValue, [(int(color.R),int(color.G),int(color.B)) for color in customColors], numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, printLayerColor, layerCategoryName)
    print printOutputMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        
        legendBakePar, legendBakePar_LL, validInputData, printMsg = checkInputData(legendStyle_, legendPlane_, maxValue_, minValue_, customColors_, numLegendCells_, fontName_, fontSize_, numDecimals_, legendUnit_, customTitle_, scale_, layerName_, layerColor_, layerCategoryName_)
        if validInputData:
            legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = legendBakePar_LL  # unpack "legendBakePar_LL" for "printOutput"
            printOutput(legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName)
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
