# OSM clean values
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2017, Djordje Spasic <djordjedspasic@gmail.com>
# Component icon based on free OSM icon from: <https://icons8.com/web-app/13398/osm> and <http://findicons.com/icon/94106/edit_clear>
#
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
A lot of times the items coming from the "values" output of OSM components may have empty data (<empty>).
Use this component to clean all that empty data, or to replace it with some other value.
-
Provided by Gismo 0.0.2

    input:
        _shapes: Shapes data tree.
                 Connect the "shapes" or "threeDeeShapes" or "foundShapes" output of some of the Gismo OSM components to this component's "_shapes" input."
        _valuesPerKey: Values data tree.
                       Connect the \"values\" output for particular key of some of the Gismo components to this input.
                       To do that, use the "List Item" component and add the "values" output to its "L" input. Also Set its "index" input to correspond to the specific key you are looking for.
                       Then plug the "i" ("item") ouput to this component's "_valuesPerKey" input.
        replaceValue_: If a value from the "_valuesPerKey" input is invalid (equals to <empty>), then replace it with some number/text added to this input.
                       If nothing is added to this input, then in case the value is invalid, it will simply be removed.
                       -
                       Optionally add a number or a text.
        convertToNum_: Optional input to determine if each of the data added to the "_valuesPerKey" input will be converted to a number or not.
                       This is useful as data coming from "values" outputs of Gismo OSM components is always a text (string) even though it may look like it is numeric.
                       -
                       If nothing is added to this input, default value of "False" will be used.
                       -
                       Boolean value ("True" or "False").
    
    output:
        readMe!: ...
        cleanedShapes: Cleaned "_shapes" input.
        cleanedValues: Cleaned "_valuesPerKey" input.
        cullingPattern: This ouput shows if an item from the "_valuesPerKey" input is valid or not (invalid items are labeled as: <empty>).
                        -
                        If the item is valid, "True" will be generated.
                        If it isn't valid, "False" will be generated.
"""

ghenv.Component.Name = "Gismo_OSM Clean Values"
ghenv.Component.NickName = "OSMcleanValues"
ghenv.Component.Message = "VER 0.0.2\nMAY_09_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.2\nMAR_07_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import Rhino


def main(shapesDataTree, valuesPerKeyDataTree, replaceValue, convertToNum):
    
    cleanedShapesDataTree = Grasshopper.DataTree[object]()
    cleanedValuesDataTree = Grasshopper.DataTree[object]()
    cullingPatternDataTree = Grasshopper.DataTree[object]()
    
    
    if (shapesDataTree.DataCount == 0):
        validInputData = False
        printMsg = "Please connect the \"shapes\" or \"threeDeeShapes\" or \"foundShapes\" output of some of the Gismo OSM components to this component's \"_shapes\" input."
        return cleanedShapesDataTree, cleanedValuesDataTree, cullingPatternDataTree, validInputData, printMsg
    
    elif (len(shapesDataTree.Branches) == 1) and (shapesDataTree.Branches[0][0] == None):
        validInputData = False
        printMsg = "There is no data supplied to the \"_shapes\" input.\n" + \
                   " \n" + \
                   "Make sure that you the component from which the data is coming to the \"_shapes\" input, is ran (its \"_runIt\" is set to \"True\")."
        return cleanedShapesDataTree, cleanedValuesDataTree, cullingPatternDataTree, validInputData, printMsg
    
    
    if (valuesPerKeyDataTree.DataCount == 0):
        validInputData = False
        printMsg = "Please connect the \"values\" output for particular key of some of the Gismo components to this component's \"_valuesPerKey\" input."
        return cleanedShapesDataTree, cleanedValuesDataTree, cullingPatternDataTree, validInputData, printMsg
    
    elif (len(valuesPerKeyDataTree.Branches) == 1) and (valuesPerKeyDataTree.Branches[0][0] == None):
        validInputData = False
        printMsg = "There is no data supplied to the \"_valuesPerKey\" input.\n" + \
                   " \n" + \
                   "Make sure that you the component from which the data is coming to the \"_valuesPerKey\" input, is ran (its \"_runIt\" is set to \"True\")."
        return cleanedShapesDataTree, cleanedValuesDataTree, cullingPatternDataTree, validInputData, printMsg
    
    
    if len(shapesDataTree.Paths) != len(valuesPerKeyDataTree.Paths):
        validInputData = False
        printMsg = "The number of tree branches added to the \"_shapes\" and \"_valuesPerKey\" inputs do not match.\n" + \
                   " \n" + \
                   "Make sure that the data you added to both of them, comes from the same OSM component."
        return cleanedShapesDataTree, cleanedValuesDataTree, cullingPatternDataTree, validInputData, printMsg
    
    
    paths_shapes = shapesDataTree.Paths
    paths_values = valuesPerKeyDataTree.Paths
    shapesLL = shapesDataTree.Branches
    
    for branchIndex, valuesPerBranch in enumerate(valuesPerKeyDataTree.Branches):
        cleanedValuesBranchL = []
        cullingPatternBranchL = []
        for value in valuesPerBranch:
            
            if (value == ""):
                if (replaceValue != None):
                    if (convertToNum == True):
                        replaceNumber_without_letters = "".join([letter  for letter in replaceValue  if letter.isdigit()])
                        cleanedValuesBranchL.append(replaceNumber_without_letters)
                    elif (convertToNum == False):
                        cleanedValuesBranchL.append(replaceValue)
                
                elif (replaceValue == None):
                    # nothing added to the "replaceValue_" input
                    # do not add anything to the "cleanedValuesBranchL"
                    pass
                
                cullingPatternBranchL.append(False)
            
            
            elif (value != ""):
                if (convertToNum == True):
                    number_without_letters = "".join([letter  for letter in value  if letter.isdigit()])
                    cleanedValuesBranchL.append(number_without_letters)
                elif (convertToNum == False):
                    cleanedValuesBranchL.append(value)
                
                cullingPatternBranchL.append(True)
        
        path_shapes = paths_shapes[branchIndex]
        path_values = paths_values[branchIndex]
        if (len(cleanedValuesBranchL) > 0):
            cleanedShapesDataTree.AddRange(shapesLL[branchIndex], path_shapes)
            cleanedValuesDataTree.AddRange(cleanedValuesBranchL, path_values)
        if (len(cullingPatternBranchL) > 0):  # this will always happen as "cullingPatternDataTree" will always have the same number of branches as initial "_shapes" and "_valuesPerKey"
            cullingPatternDataTree.AddRange(cullingPatternBranchL, path_values)
    
    
    # deleting
    del shapesDataTree; del valuesPerKeyDataTree
    
    print "OSM Clean Values component results successfully completed!"
    
    validInputData = True
    printMsg = "ok"
    
    return cleanedShapesDataTree, cleanedValuesDataTree, cullingPatternDataTree, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        cleanedShapes, cleanedValues, cullingPattern, validInputData, printMsg = main(_shapes, _valuesPerKey, replaceValue_, convertToNum_)
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
