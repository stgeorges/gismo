# Tree CO2
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2023, Djordje Spasic <djordjedspasic@gmail.com>
#
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to calculate simplified CO2 sequestering during the entire lifespan of a tree.
For the inputs of this components you can use:
1) Gismo 'OSM 3D' component's outputs
2) Gismo 'Read SHP' component's outputs
----------------------
Component works under the following assumptions:
- If trunk 'circumference_' input is empty, it will be be calculated as conservative (minimal) circumference which prevents elastical buckling of the tree, under its own weight:
- Tree weight independent of tree species
- Current height and trunk circumference taken as final
- Root green weight equals 20% of above ground green weight
- Dry weight equals 72.5% percent of total green weight
- Carbon in total dry weight equals 50%
----------------------
based on:
https://www.researchgate.net/publication/355725572_Mathematical_Modelling_to_Determine_the_Greatest_Height_of_Trees
https://www.ecomatcher.com/how-to-calculate-co2-sequestration/
-
Provided by Gismo 0.0.3
    
    input:
        _height: Tree height IN METERS. Plug in 'height' output of 'OSM 3D' component. Or output of 'Read SHP' component.
                 If you are not using Meters, as your Rhino unit system, use Gismo's 'Rhino Unit to Meters' component first.
                 -
                 IN METERS!!!
        circumference_: Tree's trunk circumference (perimeter) IN METERS.  This input is measured at 'breast height': 1.3 meters (4.5 feet) above the ground.
                        Get it from'OSM 3D' component's 'values' output. Or output of 'Read SHP' component.
                        If you are not using Meters, as your Rhino unit system, use Gismo's 'Rhino Unit to Meters' component first.
                        -
                        IN METERS!!!
        density_: Fresh green wood density, for specific wood species in kg/m3.
                  This input is only important, in case 'circumference_' input is empty!
                  If this input is empty, default value of 800kg/m3 will be used.
                  -
                  In kg/m3.
        YoungsModulus_: Elastic Modulus, for specific wood species in Giga Pascals.
                        This input is only important, in case 'circumference_' input is empty!
                        If this input is empty, default value 9 GPa will be used.
                        -
                        In GPa.
        _runIt: ...
    
    output:
        readMe!: ...
        CO2: Weight of CO2 in Kilograms, sequestered for tree's entire lifespan.
             Unit: Kilograms of CO2
"""

ghenv.Component.Name = "Gismo_Tree CO2"
ghenv.Component.NickName = "TreeCO2"
ghenv.Component.Message = "VER 0.0.3\nFEB_26_2023"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nDEC_26_2022
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import rhinoscriptsyntax as rs
import scriptcontext as sc
import Grasshopper
import System
import Rhino
import math
import gc


def checkInputData(heightDT_M, circumferenceDT_M, densityDT_kgM3, Edt_GPa):
    
    validInputData = True  # iniv
    
    # check inputs
    if (heightDT_M.DataCount == 0):
        circumference_inputIsEmpty = density_inputIsEmpty = E_inputIsEmpty = None
        validInputData = False
        printMsg = "'_height' input is empty.\n" + \
                   "The data for this input can come either from:\n" + \
                   "  - 'OSM 3D' component's 'height' output. Or \n" + \
                   "  - 'Read SHP' component's 'values' output."
        return circumference_inputIsEmpty, density_inputIsEmpty, E_inputIsEmpty, validInputData, printMsg
    
    elif (len(heightDT_M.Branches) == 1) and (heightDT_M.Branches[0][0] == None):
        # this happens when "OSM 3D" component's "_runIt" input is set to "False"
        circumference_inputIsEmpty = density_inputIsEmpty = E_inputIsEmpty = None
        validInputData = False
        printMsg = "There is no valid data supplied to the \"_height\" input.\n" + \
                   " \n" + \
                   "If you are using tree heights from 'OSM 3D' component 'height' output, make sure that you set its '_runIt' input to \"True\"."
        return circumference_inputIsEmpty, density_inputIsEmpty, E_inputIsEmpty, validInputData, printMsg
    
    
    
    
    height_LL = heightDT_M.Branches
    circumference_LL = circumferenceDT_M.Branches
    density_LL = densityDT_kgM3.Branches
    E_LL = Edt_GPa.Branches
    
    height_flatten_L = [itm    for subL in height_LL    for itm in subL    if (itm != None) and (itm != '')]
    circumference_flatten_L = [itm    for subL in circumference_LL    for itm in subL    if (itm != None) and (itm != '')]
    density_flatten_L = [itm    for subL in density_LL    for itm in subL    if (itm != None) and (itm != '')]
    E_flatten_L = [itm    for subL in E_LL    for itm in subL    if (itm != None) and (itm != '')]
    
    
    # something is inputted to 'circumference_', check if it has the same length/number of items as '_height'
    if (circumference_flatten_L.Count != 0):
        circumference_inputIsEmpty = False
        
        if (len(heightDT_M.Paths) != len(circumferenceDT_M.Paths)):
            validInputData = False
            printMsg = "The number of tree branches inputted to the \"_height\" and \"circumference_\" inputs do not match."
        
        """
        if (len(height_flatten_L) != len(circumference_flatten_L)):
            validInputData = False
            printMsg = "The number of items in inputted to the \"_height\" and \"circumference_\" data trees do not match."
        """
    
    else:
        # nothing inputted to 'YoungsModulus_'. Calculate it in 'main' func later
        circumference_inputIsEmpty = True
    
    
    
    # something is inputted to 'density_', check if it has the same length/number of items as '_height'
    if (density_flatten_L.Count != 0):
        density_inputIsEmpty = False
        
        if (len(heightDT_M.Paths) != len(densityDT_kgM3.Paths)):
            validInputData = False
            printMsg = "The number of tree branches inputted to the \"_height\" and \"density_\" inputs do not match."
        
        if (len(height_flatten_L) != len(density_flatten_L)):
            validInputData = False
            printMsg = "The number of items in inputted to the \"_height\" and \"density_\" data trees do not match."
    
    else:
        # nothing inputted to 'density_'. Use default value later
        density_inputIsEmpty = True
    
    
    
    # something is inputted to 'YoungsModulus_', check if it has the same length/number of items as '_height'
    if (E_flatten_L.Count != 0):
        E_inputIsEmpty = False
        
        if (len(heightDT_M.Paths) != len(Edt_GPa.Paths)):
            validInputData = False
            printMsg = "The number of tree branches inputted to the \"_height\" and \"YoungsModulus_\" inputs do not match."
        
        if (len(height_flatten_L) != len(E_flatten_L)):
            validInputData = False
            printMsg = "The number of items in inputted to the \"_height\" and \"YoungsModulus_\" data trees do not match."
    
    else:
        # nothing inputted to 'YoungsModulus_'. Use default value later
        E_inputIsEmpty = True
    
    
    
    # delete local variables
    del height_LL
    del circumference_LL
    del density_LL
    del E_LL
    
    del height_flatten_L
    del circumference_flatten_L
    del density_flatten_L
    del E_flatten_L
    gc.collect()
    
    if (validInputData == False):
        return circumference_inputIsEmpty, density_inputIsEmpty, E_inputIsEmpty, validInputData, printMsg
    else:
        validInputData = True
        printMsg = "ok"
        return circumference_inputIsEmpty, density_inputIsEmpty, E_inputIsEmpty, validInputData, printMsg


def trunkDiameterFromHeight(treeHeight_M, density_N_M3, E__N_m2):
    """calculate tree trunk diameter, based on tree height.
    diameter will be calculated as minimal circumference which prevents elastical buckling of the tree, under its own weight.
    output:
        tree trunk diameter in meters"""
    # based on: https://www.researchgate.net/publication/355725572_Mathematical_Modelling_to_Determine_the_Greatest_Height_of_Trees
    
    C = 1.959  # constant
    r = math.sqrt(  (treeHeight_M**3) / (C * (E__N_m2/density_N_M3))  )
    
    trunkDiam_M = 2 * r
    return trunkDiam_M


def treeCO2sequestered(treeHeightMeter, trunkDiamMeter):
    """calculate simplified amount of CO2 sequestered in a tree, for entire lifespan
    assumptions:
        tree weight independent of tree species
        current height and trunk diameter taken as final
        root green weight equals 20% of above ground green weight
        dry weight equals 72.5% percent of total green weight
        carbon in total dry weight equals 50%
    
    input:
        tree height in meters
        tree trunk diameter at 1.3 meters above the ground
    output:
        weight of CO2 in Kilograms, sequestered for its entire lifespan.
        To get tree's yearly sequestration rate, divide this value by tree’s age:  CO2weightKg_perYear = CO2weightKg/treeAgeInYears"""
    
    # based on:  https://www.ecomatcher.com/how-to-calculate-co2-sequestration/#:~:text=EcoMatcher%20estimates%20that%20the%20trees,pounds%20over%20a%20tree's%20lifetime.
    #            https://www.unm.edu/~jbrink/365/Documents/Calculating_tree_carbon.pdf
    
    # convert metric to imperial units, because equations are based on imerial ones
    trunkDiamInInch = trunkDiamMeter * 39.3701
    treeHeightInFeet = treeHeightMeter * 3.28084
    
    
    
    
    # a) green weight
    if (trunkDiamInInch <= 11):
        # small diameter tree
        aboveGround_greenWeight = 0.25 * (trunkDiamInInch**2) * treeHeightInFeet
    elif (trunkDiamInInch > 11):
        # large diameter tree
        aboveGround_greenWeight = 0.15 * (trunkDiamInInch**2) * treeHeightInFeet
    
    
    rootWeight_perc = 20  # in percent. default
    root_greenWeight = aboveGround_greenWeight * (rootWeight_perc/100)
    
    total_greenWeight = aboveGround_greenWeight + root_greenWeight 
    
    
    
    # b) dry weight
    avrTree_dryMatter_perc = 72.5  # in percent. default
    
    total_dryWeight = total_greenWeight * (avrTree_dryMatter_perc/100)
    
    
    # c) weight of the Carbon in a tree
    carbonPerc_in_total_dryWeight = 50  # in percent. default
    
    carbonWeight = total_dryWeight * (carbonPerc_in_total_dryWeight/100)
    
    
    # d) weight of CO2 in a tree
    weightOf_Carbon = 12
    weightOf_Oxigen = 16
    weightOfCO2 = weightOf_Carbon + (weightOf_Oxigen * 2)
    
    CO2_to_C_ratio = weightOfCO2 / weightOf_Carbon   # 3.67 default
    
    
    CO2weightLbs = CO2_to_C_ratio * carbonWeight  # in CO2 lbs, for the entire lifetime of the tree
    
    CO2weightTon = CO2weightLbs * 0.000453592
    CO2weightKg = CO2weightTon * 1000
    
    return CO2weightKg


def main(heightDT_M, circumferenceDT_M, densityDT_kgM3, Edt_GPa,   circumference_inputIsEmpty, density_inputIsEmpty, E_inputIsEmpty):
    
    
    # for output
    trunkDiam_DT = Grasshopper.DataTree[object]()
    CO2_DT = Grasshopper.DataTree[object]()
    # for output
    
    
    path_L = heightDT_M.Paths
    
    height_LL = heightDT_M.Branches
    circumference_LL = circumferenceDT_M.Branches
    density_LL = densityDT_kgM3.Branches
    E_LL = Edt_GPa.Branches
    
    
    
    
    for i in xrange(height_LL.Count):
        branch = path_L[i]
        height_L = height_LL[i]
        
        trunkDiam_L = []
        CO2_L = []
        
        if (len(height_L) == 0):  # no height was extracted from 'height' output of 'OSM 3D' component. OR no tree was created there
            pass
        elif (len(height_L) > 0):
            # value in 'height_' has some number
            
            for g in xrange(height_L.Count):
                height_M = height_L[g]
                
                
                # this can be either '<null>' in grasshopper yellow panel (None)  or '<empty>' in grasshopper yellow panel ('')
                if (height_M == None) or (height_M == ''):
                    CO2_L.append( height_M )  # just append None or ''
                
                
                else:
                    # a) height
                    if not gismo_preparation.isNumber(height_M):
                        raise ValueError("_height value '{}' in branch '{}' is not a valid number.".format(height_M, branch) )
                    
                    
                    
                    # b) density
                    if not density_inputIsEmpty:
                        # take 'density' from input
                        density_kg_M3 = density_LL[i][g]
                        
                        if not gismo_preparation.isNumber(density_kg_M3):
                            raise ValueError("density_ value '{}' in branch '{}' is not a valid number.".format(density_kg_M3, branch) )
                    else:
                        # take default value
                        density_kg_M3 = 800  # kg/m3
                    density_N_M3 = density_kg_M3 * 9.8066500286389  # convert kg/M3 to N/M3
                    
                    
                    
                    # c) Young's modulus
                    if not E_inputIsEmpty:
                        # take 'E' (YoungsModulus) from input
                        E_GPa = E_LL[i][g]
                        
                        if not gismo_preparation.isNumber(E_GPa):
                            raise ValueError("YoungsModulus_ value '{}' in branch '{}' is not a valid number.".format(E_GPa, branch) )
                    else:
                        # take default value
                        E_GPa = 9  # GPa
                    E__N_m2 = E_GPa * 1e9  # convert GPa to N/m2
                    
                    
                    
                    # d) trunk diameter
                    if not circumference_inputIsEmpty:
                        # take 'circumference' from input, and calculate 'diameter' from it
                        circumference_M = circumference_LL[i][g]
                        
                        
                        if not gismo_preparation.isNumber(circumference_M):
                            #raise ValueError("circumference_ value '{}' in branch '{}' is not a valid number.".format(circumference_M, branch) )
                            # 'circumference' not given as input. Calcuate the 'diameter' based on 'height_M'
                            trunkDiam_M = trunkDiameterFromHeight(height_M, density_N_M3, E__N_m2)
                        else:
                            circumference_M_ = float(circumference_M)
                            trunkDiam_M = circumference_M_ / math.pi  # diameter from circumference formula
                    
                    else:
                        # 'circumference' not given as input. Calcuate the 'diameter' based on 'height_M'
                        trunkDiam_M = trunkDiameterFromHeight(height_M, density_N_M3, E__N_m2)
                        
                        
                    
                    
                    
                    
                    # finally calculate the CO2 sequestered by each tree, for an entire lifespan of the tree
                    CO2weightKg = treeCO2sequestered(height_M, trunkDiam_M)
                    
                    
                    trunkDiam_L.append( trunkDiam_M )
                    CO2_L.append( CO2weightKg )
        
        
        
        trunkDiam_DT.AddRange(trunkDiam_L, branch)
        CO2_DT.AddRange(CO2_L, branch)
    
    
    printMsg = 'Tree CO2 component results successfully completed !'
    return trunkDiam_DT, CO2_DT, printMsg



level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        circumference_inputIsEmpty, density_inputIsEmpty, E_inputIsEmpty, validInputData, printMsg = checkInputData(_height, circumference_, density_, YoungsModulus_)
        if validInputData:
            if _runIt:
                trunkDiameter, CO2, printMsg = main(_height, circumference_, density_, YoungsModulus_,   circumference_inputIsEmpty, density_inputIsEmpty, E_inputIsEmpty)
                print printMsg
            else:
                print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Tree CO2 component"
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
