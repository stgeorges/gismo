# Rhino unit to meters
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2022, Djordje Spasic <djordjedspasic@gmail.com>
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
ghenv.Component.Message = "VER 0.0.3\nDEC_26_2022"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "3 | More"
#compatibleGismoVersion = VER 0.0.3\nDEC_26_2022
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper


def main(valueRhinoUnit_DT):
    
    
    unitConversionFactor, unitSystemLabel = gis_prep.checkUnits()
    
    
    valueMeter_DT = Grasshopper.DataTree[object]()  # for output
    
    
    path_L = valueRhinoUnit_DT.Paths
    valueRhinoUnit_LL = valueRhinoUnit_DT.Branches
    
    
    for i in xrange(valueRhinoUnit_LL.Count):
        path = path_L[i]
        subL = valueRhinoUnit_LL[i]
        
        subL2 = []
        for v_rhUnit in subL:
            
            if (v_rhUnit == None) or (v_rhUnit == ''):
                v_meter = 0
            else:
                
                if gis_prep.isNumber(v_rhUnit):
                    v_meter = float(v_rhUnit) * unitConversionFactor
                else:
                    v_meter = 0  # example: 'pi' or some other weird openstreetmap entry for for example 'circumference'
            
            subL2.append( v_meter )
        
        valueMeter_DT.AddRange(subL2, path)
    
    
    
    # check if there was any valid number value in the input ''
    if (valueMeter_DT.DataCount == 0):
        validInputData = False
        printMsg = "'_valueRhinoUnit' input contains no valid values."
        unitConversionFactor, valueMeter_DT, validInputData, printMsg
    
    else:
        validInputData = True
        printMsg = 'ok'
        return unitConversionFactor, valueMeter_DT, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gis_prep = sc.sticky["gismo_Preparation"]()
        
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
