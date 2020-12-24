# color palette
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
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
Use this component define color palette (gradient colors) for the Gismo's "Legend Bake Parameters" component
-
Provided by Gismo 0.0.3

    input:
        paletteIndex_: An index of the color palette:
                       -
                       0 - Gismo default palette
                       1 - Aspect ArcView
                       2 - Aspect ArcGISnew
                       3 - Aspect QGIS
                       4 - Differences QGIS
                       5 - Elevation QGIS
                       6 - Elevation topology QGIS
                       7 - Haxby QGIS
                       8 - NDVI QGIS
                       9 - Population QGIS
                       10 - Precipitation QGIS
                       11 - Slope QGIS
                       12 - Bathymetry 1
                       13 - Bathymetry 2
                       14 - Time travel vintage
                       15 - Urban noise
                       16 - Lotus diverging 1
                       17 - Lotus diverging 2
                       18 - Centennial map custom
                       19 - PiYG diverging
                       20 - PRGn diverging
                       21 - Spectral diverging
                       22 - Dark red - yellow - white
    
    output:
        readMe!: ...
        paletteColors: A list of colors representing the chosen palette.
                        Plug it to "customColors_" input of Gismo's "Legend Bake Parameters" component.
"""

ghenv.Component.Name = "Gismo_Color Palette"
ghenv.Component.NickName = "ColorPalette"
ghenv.Component.Message = "VER 0.0.3\nDEC_16_2020"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import System
import Rhino


def main(paletteIndex):
    
    colorPalette_dict_orderKeys = [
    "Gismo default palette", 
    "Aspect ArcView", 
    "Aspect ArcGIS new", 
    "Aspect QGIS", 
    "Differences QGIS", 
    "Elevation QGIS", 
    "Elevation topology QGIS", 
    "Haxby QGIS", 
    "NDVI QGIS", 
    "Population QGIS", 
    "Precipitation QGIS", 
    "Slope QGIS", 
    "Bathymetry 1",
    "Bathymetry 2",
    "Time travel vintage",
    "Urban noise",
    "Lotus diverging 1",
    "Lotus diverging 2",
    "Centennial map custom",
    "PiYG diverging",
    "PRGn diverging",
    "Spectral diverging",
    "Dark red - yellow - white"]
    
    
    # check input
    if (paletteIndex == None):
        paletteColors = None
        validInputData = False
        printMsg = "Please add a number to the \"paletteIndex_\" input do define certain color pallete."
        return paletteColors, validInputData, printMsg
    
    elif (paletteIndex < 0) or (paletteIndex > len(colorPalette_dict_orderKeys)-1):
        paletteColors = None
        validInputData = False
        printMsg = "\"paletteIndex_\" input only accepts values from 0 to %s." % str( len(colorPalette_dict_orderKeys)-1 )
        return paletteColors, validInputData, printMsg
    
    
    
    colorPalette_dict = {
    # gradient blue-green-red
    """Gismo default palette""" :
    [[2,83,250],
    [68,219,226],
    [155,253,126],
    [173,255,25],
    [253,255,16],
    [251,192,31],
    [248,64,74]]
    ,
    # https://www.researchgate.net/figure/Aspect-map-of-the-Orr-watershed-MP-India_fig4_267628746
    """Aspect ArcView""" :
    [[253, 1, 0],
    [255, 166, 2],
    [255, 253, 3],
    [3, 253, 7],
    [0, 255, 255],
    [1, 166, 255],
    [0, 0, 252],
    [255, 0, 255],
    [253, 1, 0]]
    ,
    # https://www.esri.com/arcgis-blog/products/arcgis-pro/imagery/new-aspect-slope-raster-function-now-available
    """Aspect ArcGIS new""" :
    [[132, 214, 0],
    [0, 104, 192],
    [108, 0, 163],
    [202, 0, 156],
    [255, 85, 104],
    [255, 171, 71],
    [244, 250, 0],
    [132, 214, 0]]
    ,
    # source: https://grasswiki.osgeo.org/wiki/Color_tables
    """Aspect QGIS""" :
    [["white"], ["yellow"], ["green"], ["cyan"], ["red"], ["yellow"]]
    ,
    """Differences QGIS""" :
    [["blue"], ["white"], ["red"]]
    ,
    """Elevation QGIS""" :
    [[0, 191, 191],
    [0, 255, 0],
    [255, 255, 0],
    [255, 127, 0],
    [191, 127, 63],
    [26, 23, 62],
    [200, 200, 200]]
    ,
    """Elevation topology QGIS""" :
    [[0, 0, 0],
    [0, 0, 100],
    [50, 50, 200],
    [150, 150, 255],
    [0, 150, 0],
    [90, 165, 90],
    [90, 175, 90],
    [50, 180, 50],
    [70, 170, 70],
    [70, 145, 75],
    [70, 155, 75],
    [150, 156, 100],
    [220, 220, 220],
    [245, 245, 245],
    [255, 255, 255]]
    ,
    """Haxby QGIS""" :
    [[37,57,175],
    [40,127,251],
    [50,190,255],
    [106,235,255],
    [138,236,174],
    [205,255,162],
    [240,236,121],
    [255,189,87],
    [255,161,68],
    [255,186,133],
    [255,255,255]]
    ,
    """NDVI QGIS""" :
    [[5, 24, 82],
    [5, 24, 82],
    [255, 255, 255],
    [206, 197, 180],
    [191, 163, 124],
    [179, 174, 96],
    [163, 181, 80],
    [144, 170, 60],
    [166, 195, 29],
    [135, 183, 3],
    [121, 175, 1],
    [101, 163, 0],
    [78, 151, 0],
    [43, 132, 4],
    [0, 114, 0],
    [0, 90, 1],
    [0, 73, 0],
    [0, 56, 0],
    [0, 31, 0],
    [0, 0, 0]]
    ,
    """Population QGIS""" :
    [[255, 255, 255],
    [255, 218, 164],
    [255, 218, 164],
    [255, 186, 90],
    [255, 186, 90],
    [205, 129, 32],
    [205, 129, 32],
    [139, 64, 16],
    [139, 64, 16],
    [90, 4, 0],
    [90, 4, 0]]
    ,
    """Precipitation QGIS""" :
    [[255, 255, 255],
    [158, 255, 222],
    [200, 255, 255],
    ["cyan"],
    [0, 0, 255],
    [153, 51, 255],
    ["violet"],
    [51, 0, 51],
    [20, 0, 20],
    [0, 0, 0]]
    ,
    """Slope QGIS""" :
    [[255, 255, 255],
    [255, 255, 0],
    [0, 255, 0],
    [0, 255, 255],
    [0, 0, 255],
    [255, 0, 255],
    [255, 0, 0],
    [0, 0, 0]]
    ,
    """Bathymetry 1""" :
    [["blue"], ["cyan"], ["green"], ["yellow"], ["red"]]
    ,
    """Bathymetry 2""" :
    [[241,241,122],
    [249,201,50],
    [252,161,8],
    [245,122,23],
    [227,89,50],
    [202,64,74],
    [171,47,94],
    [137,34,106],
    [104,22,110],
    [69,10,105],
    [33,12,74],
    [6,4,24]]
    ,
    # https://www.colourlovers.com/palette/3524375/Vintage_Time_Travel
    """Time travel vintage""" :
    [[153,188,182],
    [209,209,181],
    [239,209,171],
    [228,174,172],
    [223,119,142]]
    ,
    # http://www.coloringnoise.com/theoretical_background
    """Urban noise""" :
    [[184,207,203],
    [206,228,204],
    [226,242,191],
    [243,198,131],
    [232,126,77],
    [207,76,69],
    [165,36,85],
    [113,7,93]]
    ,
    # https://www.degraeve.com/color-palette/?src=rss
    """Lotus diverging 1""" :
    [[0,136,68],
    [51,170,119],
    [255,238,238],
    [255,187,221],
    [255,119,153]]
    ,
    # https://www.degraeve.com/color-palette/?src=rss
    """Lotus diverging 2""" :
    [[17,102,68],
    [85,153,119],
    [255,238,255],
    [255,204,221],
    [238,170,170]]
    ,
    # https://www.colourlovers.com/palette/3554256/Centennial_Map
    """Centennial map custom""" :
    [[179, 183, 133],
    [227, 189, 137],
    [215, 111, 112],
    [190, 195, 173],
    [83, 76, 60]]
    ,
    # http://colorbrewer2.org/#type=diverging&scheme=PiYG&n=11
    """PiYG diverging""" :
    [[39, 100, 25],
    [77, 146, 33],
    [127, 188, 65],
    [184, 225, 134],
    [230, 245, 208],
    [247, 247, 247],
    [253, 224, 239],
    [241, 182, 218],
    [222, 119, 174],
    [197, 27, 125],
    [142, 1, 82]]
    ,
    # http://colorbrewer2.org/#type=diverging&scheme=PRGn&n=11
    """PRGn diverging""" :
    [[0, 68, 27],
    [27, 120, 55],
    [90, 174, 97],
    [166, 219, 160],
    [217, 240, 211],
    [247, 247, 247],
    [231, 212, 232],
    [194, 165, 207],
    [153, 112, 171],
    [118, 42, 131],
    [64, 0, 75]]
    ,
    # http://colorbrewer2.org/#type=diverging&scheme=Spectral&n=11
    """Spectral diverging""" :
    [[94, 79, 162],
    [50, 136, 189],
    [102, 194, 165],
    [171, 221, 164],
    [230, 245, 152],
    [255, 255, 191],
    [254, 224, 139],
    [253, 174, 97],
    [244, 109, 67],
    [213, 62, 79],
    [158, 1, 66]]
    ,
    """Dark red - yellow - white""" :
    [[255, 255, 255],
    [255, 172, 0],
    [255, 0, 0],
    [130, 18, 0]]
    }
    
    
    #if colorPalette_dict.has_key(requiredColorPaletteName):  # no need to check. The upper indexPalette checks for index range
    requiredColorPaletteName = colorPalette_dict_orderKeys[paletteIndex]
    paletteColors_notFinal = colorPalette_dict[requiredColorPaletteName]
    
    paletteColors = []
    for paletteColor in paletteColors_notFinal:
        if isinstance(paletteColor[0], System.String):
            # convert string to color
            color = System.Drawing.ColorTranslator.FromHtml(paletteColor[0])
        else:
            # convert R,G,B values to color
            color = System.Drawing.Color.FromArgb(paletteColor[0], paletteColor[1], paletteColor[2])
        paletteColors.append(color)
    
    
    print "'%s' colors outputted" % requiredColorPaletteName
    
    validInputData = True
    printMsg = "ok"
    
    return paletteColors, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        
        paletteColors, validInputData, printMsg = main(paletteIndex_)
        if not validInputData:
            print printMsg
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)
