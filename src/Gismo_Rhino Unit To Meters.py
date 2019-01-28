# Rhino unit to meters
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
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
Use this component to convert values from Rhino units to meters. This can be useful for Gismo component's "radius_" inputs, as all of them use values in meters, regardless of what the Rhino units have been set at.
-
Provided by Gismo 0.0.3

    input:
        _valueRhinoUnit: A number in Rhino units, which you would like to convert to meters.
                         -
                         In Rhino document units.
    
    output:
        unitFactor: Unit conversion factor.
                    -
                    Unitless.
        valueMeters: _valueRhinoUnit number converted to meters.
                     It equals: _valueRhinoUnit * unitFactor
                     -
                     In meters.
"""

ghenv.Component.Name = "Gismo_Rhino Unit To Meters"
ghenv.Component.NickName = "RhinoUnitToMeters"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper


def main(valueRhinoUnit):
    
    # check inputs
    if (valueRhinoUnit == None):
        unitConversionFactor = valueMeters = None
        validInputData = False
        printMsg = "Please add a number to \"_valueRhinoUnit\" input."
        return unitConversionFactor, valueMeters, validInputData, printMsg
    
    unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
    valueMeters = valueRhinoUnit * unitConversionFactor
    
    validInputData = True
    printMsg = "ok"
    return unitConversionFactor, valueMeters, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        unitFactor, valueMeters, validInputData, printMsg = main(_valueRhinoUnit)
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
