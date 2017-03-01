# Rhino text to number
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
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
Use this component to convert values from Rhino units to meters. This can be useful for Gismo component's "radius_" inputs, as all of them use values in meters, regardless of what the Rhino units have been set at.
-
Provided by Gismo 0.0.2

    input:
        _rhinoText: Rhino text.
                    Use Grashopper's "Guid" parameter to input it.
    
    output:
        readMe!: ...
        text: A string extracted from upper "_rhinoText" input.
              -
              String.
        point: A point which corresponds to the origin of upper "_rhinoText" input.
"""

ghenv.Component.Name = "Gismo_Rhino Text To Number"
ghenv.Component.NickName = "RhinoTextToNumber"
ghenv.Component.Message = "VER 0.0.2\nMAR_01_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.2\nMAR_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import Rhino


def main(rhinoTextIds):
    
    if (len(rhinoTextIds) == 0) or (rhinoTextIds[0] == None):
        texts = pts = None
        validInputData = False
        printMsg = "Please add a Rhino text to \"_rhinoText\" input by using Grasshopper's \"Guid\" parameter."
        return texts, pts, validInputData, printMsg
    
    texts = []
    pts = []
    sc.doc = Rhino.RhinoDoc.ActiveDoc
    for id in rhinoTextIds:
        textObj = sc.doc.Objects.Find(id)
        if (textObj == None):
            texts = []
            pts = []
        elif (textObj != None):
            print "textObj: ", textObj
            textEntity = textObj.Geometry
            text = textEntity.Text
            
            pt = textEntity.Plane.Origin
            try:
                ptZ = float(text)
            except:
                textReplaced = text.replace(" ", ".")
                if textReplaced.endswith("."):
                    textReplaced = textReplaced[:-1]
                ptZ = float(textReplaced)
            texts.append(ptZ)
            #ptLifted = Rhino.Geometry.Point3d(pt.X, pt.Y, ptZ)
            #pts.append(ptLifted)
            pts.append(pt)
    sc.doc = ghdoc
    
    validInputData = True
    printMsg = "ok"
    
    return texts, pts, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        text, point, validInputData, printMsg = main(_rhinoText)
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
