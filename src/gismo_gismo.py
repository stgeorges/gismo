# this is Gismo's main component
#
# Gismo is a plugin for GIS Environmental Analysis (GPL) started by Djordje Spasic.
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
This component contains all Gismo classes. Other Gismo components are being run by referencing these classes.
So in order for any other Gismo component to work, you need to run this component first. If this component is ran successfully you will hear the Gismo penquin peeping!!
-
Provided by Gismo 0.0.3
    input:
        mapFolder_: Optional folder path for MapWinGIS installation folder.
                    -
                    Most of Gismo's components require MapWinGIS application being installed.
                    If you did that, Gismo Gismo component will automatically find your MapWinGIS installation folder.
                    However sometimes Gismo Gismo component will fail to find your MapWinGIS installation folder. In that case you need to input it manually by adding it to the mapFolder_ input.
        gismoFolder_: Optional folder path for Gismo working folder.
                      -
                      If nothing is supplied to this input, then gismoFolder_ will be set to: "c:\gismo" by default.
    output:
        readMe!: This output will inform whether the component has been successfully ran or not.
"""

ghenv.Component.Name = "Gismo_Gismo"
ghenv.Component.NickName = "Gismo"
ghenv.Component.Message = "VER 0.0.3\nFEB_10_2025"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.icon
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "0 | Gismo"
try: ghenv.Component.AdditionalHelpFromDocStrings = "1"
except: pass

from System.Runtime.InteropServices import Marshal
import ghpythonlib.components as ghc
import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext as sc
import Grasshopper
import datetime
import System
import shutil
import urllib
import Rhino
import time
import math
import sys
import clr
import csv
import os


tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance


class Check(object):
    """
    check component's version and date
    """
    def deconstructComponents_versionDate(self, componentMessage):
        """
        deconstruct the "ghenv.Component.Message" string to a version and date
        """
        versionIncomplete, dateIncomplete = componentMessage.split("\n")
        
        # version
        VERstring, version = versionIncomplete.split(" ")
        
        # date
        date = dateIncomplete.replace("_","/")  # example: JUN/09/2020
        date_timeStruct = time.strptime(date, "%b/%d/%Y")
        
        return version, date_timeStruct
    
    
    def normalizeVersion(self, v):
        """
        normalize gismo version string
        """
        # from: http://stackoverflow.com/a/1714132/3137724
        parts = [int(x) for x in v.split(".")]
        while parts[-1] == 0:
            parts.pop()
        return parts
    
    
    def versionDate(self, component):
        """
        compare GismoGismo component and other component's versions and that component's "#compatibleLBVersion" version and date
        """
        gismoGismo_ComponentMessage = ghenv.Component.Message
        components_ComponentMessage = component.Message
        gismoGismo_version, gismoGismo_date_timeStruct = self.deconstructComponents_versionDate(gismoGismo_ComponentMessage)
        component_version, component_date_timeStruct_dummy = self.deconstructComponents_versionDate(components_ComponentMessage)
        
        # a) compare the Gismo_Gismo and components version (date is irrelevant)
        versionCompareResult = cmp(self.normalizeVersion(gismoGismo_version), self.normalizeVersion(component_version))  # returns: -1 (smaller than), 0 (equal), 1 (larger than)
        if versionCompareResult == -1:
            validVersionDate = False
            printMsg = "You are using an older version of Gismo_Gismo component.\nDownload the newest one from:\n\n" + \
                       "https://github.com/stgeorges/gismo/blob/master/userObjects/Gismo_Gismo.ghuser\n\n" + \
                       "Once you download the Gismo_Gismo.ghuser file, follow these four simple steps:\n\n" + \
                       "1) Check if Gismo_Gismo.ghuser file has been blocked: right click on it, and choose \"Properties\". If there is an \"Unblock\" button click on it, and then click on \"OK\". If there is no \"Unblock\" button, just click on \"OK\".\n\n" + \
                       "2) Put this file into your Grasshopper's: \"File->Special Folders->User Object Folder\" folder.\n\n" + \
                       "3) In your Grasshopper definition, delete the old \"Gismo_Gismo\" component and drag and drop the new one from the \"0 | Gismo\" menu.\n\n" + \
                       "4) In Grasshopper's top menu, choose: \"Solution->Recompute\". That's it!"
            del component
            return validVersionDate, printMsg
        else:
            # Gismo_Gismo component and component's version are equal(versionCompareResult = 0) or GismoGismo is newer(versionCompareResult = 1)
            # b) compare the component's "#compatibleLBVersion" version AND date with Gismo_Gismo version AND date
            componentsCodeString = component.Code
            codePerLine = componentsCodeString.split("\n")
            for line in codePerLine:
                if "#compatibleGismoVersion" in line:
                    #dateIncomplete = line.split("\\n")[-1].strip()  # example: JUN_09_2020
                    versionIncomplete, dateIncomplete = line.split("\\n")
                    
                    # "#compatibleGismoVersion" version
                    compatibleGismoVersion_version = versionIncomplete.split("VER")[-1].strip()
                    
                    # "#compatibleGismoVersion" date
                    dateIncomplete2 = dateIncomplete.strip()
                    date = dateIncomplete2.replace("_","/")  # example: JUN/09/2020
                    component_date_timeStruct = time.strptime(date, "%b/%d/%Y")
                    break
            else:
                # "#compatibleGismoVersion" is not found in the components code
                validVersionDate = False
                printMsg = "This component does not contain the Gismo_Gismo compatibility tag (\"#compatibleGismoVersion\").\nReport this issue at:" + \
                           "http://www.grasshopper3d.com/group/gismo" + \
                           "\n\nby opening a new topic there."
                del component
                del componentsCodeString
                return validVersionDate, printMsg
           
            versionCompareResult2 = cmp(self.normalizeVersion(gismoGismo_version), self.normalizeVersion(compatibleGismoVersion_version))  # returns: -1 (smaller than), 0 (equal), 1 (larger than)
            if versionCompareResult2 == -1:
                # the "#compatibleGismoVersion" version is newer than Gismo_Gismo version
                validVersionDate = False
                printMsg = "You are using an older version of Gismo_Gismo component ,\nDownload the newest one from:\n\n" + \
                           "https://github.com/stgeorges/gismo/blob/master/userObjects/Gismo_Gismo.ghuser\n\n" + \
                           "Once you download the Gismo_Gismo.ghuser file, follow these four simple steps:\n\n" + \
                           "1) Check if Gismo_Gismo.ghuser file has been blocked: right click on it, and choose \"Properties\". If there is an \"Unblock\" button click on it, and then click on \"OK\". If there is no \"Unblock\" button, just click on \"OK\".\n\n" + \
                           "2) Put this file into your Grasshopper's: \"File->Special Folders->User Object Folder\" folder.\n\n" + \
                           "3) In your Grasshopper definition, delete the old \"Gismo_Gismo\" component and drag and drop the new one from the \"0 | Gismo\" menu.\n\n" + \
                           "4) In Grasshopper's top menu, choose: \"Solution->Recompute\". That's it!"
                del component
                del componentsCodeString
                return validVersionDate, printMsg
            else:
                if gismoGismo_date_timeStruct < component_date_timeStruct:
                    # the "#compatibleGismoVersion" date is newer than Gismo_Gismo date
                    validVersionDate = False
                    printMsg = "You are using an older version of Gismo_Gismo component ;\nDownload the newest one from:\n\n" + \
                               "https://github.com/stgeorges/gismo/blob/master/userObjects/Gismo_Gismo.ghuser\n\n" + \
                               "Once you download the Gismo_Gismo.ghuser file, follow these four simple steps:\n\n" + \
                               "1) Check if Gismo_Gismo.ghuser file has been blocked: right click on it, and choose \"Properties\". If there is an \"Unblock\" button click on it, and then click on \"OK\". If there is no \"Unblock\" button, just click on \"OK\".\n\n" + \
                               "2) Put this file into your Grasshopper's: \"File->Special Folders->User Object Folder\" folder.\n\n" + \
                               "3) In your Grasshopper definition, delete the old \"Gismo_Gismo\" component and drag and drop the new one from the \"0 | Gismo\" menu.\n\n" + \
                               "4) In Grasshopper's top menu, choose: \"Solution->Recompute\". That's it!"
                    del component
                    del componentsCodeString
                    return validVersionDate, printMsg
                else:
                    validVersionDate = True
                    printMsg = "ok"
                    del component
                    del componentsCodeString
                    return validVersionDate, printMsg


class mainComponent(object):
    """
    check gismoFolder_ and mapFolder_ inputs of "Gismo Gismo" component
    """
    def gismoWorkingFolder(self, gismoFolder):
        """
        check gismoFolder_ of Gismo Gismo component
        """
        if (gismoFolder == None):
            gismoFolder = "c:\gismo"
        
        myPreparation = Preparation()
        folderCreated = myPreparation.createFolder(gismoFolder)
        if folderCreated:
            # gismoFolder successfully created or it already exists
            printMsg = "ok"
            return gismoFolder, printMsg
        else:
            # "gismoFolder_" inputted to Gismo Gismo component can not be created
            printMsg = "gismoFolder_ is invalid"
            return False, printMsg
    
    
    def mapWinGIS(self, mapFolder=None):
        """
        check if mapWinGIS is installed
        """
        # identify if Rhino 5 is 32 or 64 bit version
        if System.Environment.Is64BitProcess == False:
            bitVersion = "Win32"
        elif System.Environment.Is64BitProcess == True:
            bitVersion = "x64"
        
        if mapFolder == None:
            # check if there is a "MapWinGIS" folder present in some well known places
            iteropMapWinGIS_dll_folderPathLL = [
            "c:\\MapWindow",
            "c:\\ProgramData\\MapWindow", 
            "c:\\Program Files\\MapWindow", 
            "c:\\Program Files (x86)\\MapWindow", 
            "D:\\MapWindow", 
            "D:\\ProgramData\\MapWindow", 
            "D:\\Program Files\\MapWindow", 
            "D:\\Program Files (x86)\\MapWindow", 
            "c:\\MapWinGIS", 
            "c:\\dev\\MapWinGIS",
            "c:\\ProgramData\\MapWinGIS", 
            "c:\\Program Files\\MapWinGIS", 
            "c:\\Program Files (x86)\\MapWinGIS", 
            "D:\\MapWinGIS", 
            "D:\\dev\\MapWinGIS",
            "D:\\ProgramData\\MapWinGIS", 
            "D:\\Program Files\\MapWinGIS", 
            "D:\\Program Files (x86)\\MapWinGIS"]
        else:
            iteropMapWinGIS_dll_folderPathLL = [mapFolder]
        
        iteropMapWinGIS_dll_fileName = "Interop.MapWinGIS.dll"
        
        InteropMapWinGISDll_present = False
        for iteropMapWinGIS_dll_folderPath in iteropMapWinGIS_dll_folderPathLL:
            iteropMapWinGIS_dll_filePath = os.path.join(iteropMapWinGIS_dll_folderPath, iteropMapWinGIS_dll_fileName)
            InteropMapWinGISDll_present = os.path.isfile(iteropMapWinGIS_dll_filePath)
            if InteropMapWinGISDll_present != False:
                # "Interop.MapWinGIS.dll" file found in the "MapWinGIS" folder
                break
        else:
            # "Interop.MapWinGIS.dll" file was found in the "iteropMapWinGIS_dll_folderPathLL" folders
            #InteropMapWinGISDll_present = False
            if mapFolder == None:
                # nothing inputted into the "mapFolder_"
                printMsg = "This component requires the \"MapWinGIS\" application to be installed in order for it to work.\n" + \
                           "The component could not find the installation folder of the \"MapWinGIS\" application.\n" + \
                           "-\n" + \
                           "If you haven't installed the \"MapWinGIS\" application, download its %s version from the link below, and install it:\n" % bitVersion + \
                           "https://github.com/MapWindow/MapWinGIS/releases\n" + \
                           "-\n" + \
                           "If you already downloaded and installed the \"MapWinGIS\" application, then supply its installation folder path to the \"mapFolder_\" input."
            else:
                # some folder path inputted into the "mapFolder_"
                printMsg = "The folder path you added to Gismo_Gismo component's \"mapFolder_\" input is invalid: meaning this is not the MapWinGIS application install folder.\n" + \
                           "-\n" + \
                           "You can find the valid \"mapFolder_\" path by using the Start Menu -> Search function (and search for \"MapWinGIS\").\n" + \
                           "If you do not input the correct folder path to \"mapWindow\" some Gismo components might not be able to work."
            iteropMapWinGIS_dll_folderPath = gdalDataPath_folderPath = None
            validInputData = False
            return iteropMapWinGIS_dll_folderPath, gdalDataPath_folderPath, validInputData, printMsg
        
        
        try:
            clr.AddReferenceToFileAndPath(iteropMapWinGIS_dll_filePath)
        except:
            pass
        
        iteropMapWinGIS_dll_loaded_Success = "Interop.MapWinGIS" in [assembly.GetName().Name for assembly in clr.References]
        
        if iteropMapWinGIS_dll_loaded_Success:
            # import GDAL libraries and register GDAL drivers
            global MapWinGIS  # so that other methods in this Gismo Gismo component could use the MapWinGIS module
            import MapWinGIS
            
            # testing if the "Retrieving the COM class factory for component with CLSID" error will appear
            try:
                dummyShape = MapWinGIS.ShapeClass()
                sc.sticky["MapWinGIS"] = ""  # "" is dummy value. Only the key name "MapWinGIS" is important
            except Exception, e:
                # the "Retrieving the COM class factory for component with CLSID" error appeared
                iteropMapWinGIS_dll_folderPath = gdalDataPath_folderPath = None
                validInputData = False
                printMsg = "The following error has been raised:\n" + \
                           " \n" + \
                           "%s\n" % e + \
                           " \n \n" + \
                           "If upper error is:\n" + \
                           "1) \"Retrieving the COM class factory for component with CLSID...\" then try the following fix:\n" + \
                           " a) Close Rhino. Restart your PC. Once the PC boots up, double click on the \"regMapWinGIS.cmd\" file in \"MapWinGIS\" installation folder. When it closes the Command Prompt window it opened, try running Rhino, Grasshopper and the component again.\n" + \
                           " b) If the upper COM class error appears again, then close Rhino, and uninstall the MapWinGIS application. It is advisable to do that with an application which does that by removing not only the installation files but also the leftover files (like those from registry). For example, use the: Revo Uninstaller Pro. A free 30 days full working version can be downloaded from: http://www.revouninstaller.com.\n" + \
                           " After the Revo Uninstaller Pro uninstalls MapWinGIS, install it again, but this time by running the installation file by right clicking on it, and choosing: Run as -> Administrator. After the installation is complete double click on \"regMapWinGIS.cmd\" file in \"MapWinGIS\" installation folder. When it closes the Command Prompt window it opened, try running Rhino, Grasshopper and the component again.\n" + \
                           " If after this the COM class error appears again, then post a question about this issue at:\n" + \
                           " http://www.grasshopper3d.com/group/gismo/forum.\n" + \
                           " \n \n" + \
                           "2) If the upper error is not \"Retrieving the COM class factory for component with CLSID...\", please post a question about this issue at:\n" + \
                           "http://www.grasshopper3d.com/group/gismo/forum."
                return iteropMapWinGIS_dll_folderPath, gdalDataPath_folderPath, validInputData, printMsg
            
            # set the folderpath for "gdal_data" folder
            gdalDataPath_folderPath = os.path.join(iteropMapWinGIS_dll_folderPath, "gdal-data")
            MapWinGIS.GlobalSettingsClass().GdalDataPath = gdalDataPath_folderPath  # added in 4.9.3 version
            
            validInputData = True
            printMsg = "ok"
            return iteropMapWinGIS_dll_folderPath, gdalDataPath_folderPath, validInputData, printMsg
        
        else:
            # the "MapWinGIS" install folder contains the "Interop.MapWinGIS.dll" file but some other ones are missing
            gdalDataPath_folderPath = None
            validInputData = False
            printMsg = "This component requires the \"MapWinGIS\" application to be installed in order for it to work.\n" + \
                       " \n" + \
                       "For some reason it seems that \"MapWinGIS\" is installed but its install folder (\"%s\") does not contain all the necessary files.\n" % iteropMapWinGIS_dll_folderPath + \
                       "Close Rhino. Uninstall the MapWinGIS application. Then install it again.\n" + \
                       " \n" + \
                       "If after this, you still get this same message please post a question about this issue at:\n" + \
                       "http://www.grasshopper3d.com/group/gismo/forum."
            iteropMapWinGIS_dll_folderPath = None  # set in here, to prevent the "iteropMapWinGIS_dll_folderPath" being equal to "None" when printed in upper "printMsg"
            return iteropMapWinGIS_dll_folderPath, gdalDataPath_folderPath, validInputData, printMsg


class Transform(object):
    """
    methods used to perform transformation
    """
    def copy(self, obj):
        """copy the object. Use this func instead of 'ds.CopyObj!'"""
        if isinstance(obj, Rhino.Geometry.GeometryBase):
            obj2 = obj.Duplicate()
        else:
            obj2 = System.ICloneable.Clone(obj)
            
            if (obj2 == None):
                try:
                    obj2 = copy.copy(obj)  # does not work on Rhino.Geometry.Leader
                except Exception, e:
                    print "%s of type %s couldn't be copied" % (obj, type(obj))
        
        return obj2
    
    
    def move(self, obj, transVec):
        """moves a copy of obj"""
        obj2 = self.copy(obj)
        
        if hasattr(transVec, "__iter__"):  # supports list, tuple, Array, List
            transVec = rg.Vector3d(transVec[0], transVec[1], transVec[2])
        
        tm = rg.Transform.Translation(transVec)
        obj2.Transform(tm)
        return obj2
    
    
    def scale(self, obj, pln, scaleFac):
        """scale the object uniformly in all directions
        input:
            obj to scale
            scaling pln
            scaleFactor number"""
        obj_c = self.copy(obj)
        
        xform = rg.Transform.Scale(pln, scaleFac, scaleFac, scaleFac)
        obj_c.Transform(xform)
        return obj_c


class Preparation(object):
    """
    methods used to prepare components before performing analysis/running results
    """
    def checkUnits(self):
        """
        calculate unitConversionFactor for appropriate Rhino document Model unit. And check Rhino Model units
        """
        unitSystem_id = int(Rhino.RhinoDoc.ActiveDoc.ModelUnitSystem)
        
        if (unitSystem_id == 2):
            fromUnitSystem =  Rhino.UnitSystem.Millimeters
            unitSystem = "Millimeters"
        elif (unitSystem_id == 3):
            fromUnitSystem = Rhino.UnitSystem.Centimeters
            unitSystem = "Centimeters"
        elif (unitSystem_id == 4):
            fromUnitSystem = Rhino.UnitSystem.Meters
            unitSystem = "Meters"
        elif (unitSystem_id == 8):
            fromUnitSystem = Rhino.UnitSystem.Inches
            unitSystem = "Inches"
        elif (unitSystem_id == 9):
            fromUnitSystem = Rhino.UnitSystem.Feet
            unitSystem = "Feet"
        elif (unitSystem_id == 10):
            fromUnitSystem = Rhino.UnitSystem.Miles
            unitSystem = "Miles"
        else:
            # chosen unit system is not one of the above supported ones
            return None, "unknown unit system"
        
        toMeters = Rhino.UnitSystem.Meters
        unitConversionFactor = Rhino.RhinoMath.UnitScale(fromUnitSystem, toMeters)
        return unitConversionFactor, unitSystem
    
    
    def cleanString(self, string):
        """
        for a given string, replace "/", "\", " ", "," with "_"
        """
        stringCorrected = System.String.Replace(   System.String.Replace(  System.String.strip(System.String.Replace(System.String.Replace(string,"\\","_"), "/", "_") )  ," ", "_")   ,",", "_") # removing "/", "\", " ", ","
        return stringCorrected
    
    
    def isNum(self, obj):
        """check if 'obj' is integer or float. Strings in form of number are NOT considered (example: "3.23")"""
        return isinstance(obj, (int, float))
    
    
    def strToNum(self, n_str):
        """convert a string number to a float or integer number
        a string number can have either '.' or ',' as its decimal separator (in case it is a decimal, and not an integer)."""
        if self.isNum(n_str): return n_str  # in case 'n_str' is a int() or float()
        
        if "," in n_str: 
            # n_str is a decimal number with "," as decimal
            n_str2 = n_str.replace(",",".")
            n = float(n_str2)
        elif "." in n_str:
            # n_str is a decimal number with "." as decimal
            n = float(n_str)
        else: n = float(n_str)
        
        # interger or not
        if n == int(n): return int(n)  # happens for example 2400.000 == 2400 results in True
        else: return n
    
    
    def epsilonEquals(self, n1, n2, tol=0.001):
        """compare two numbers within the tolerance
        input:
            two numbers
        output:
            True if they are equal within the tolerance (if n1 and n2 are less or equal than 'tol' different)
            False if they are NOT equal within the tolerance"""
        
        areEqual = abs(n1 - n2) <= tol
        return areEqual
    
    
    def isFileWithFullPath(self, filefullWithEXT):
        """check if a file exists.
        Add "r" at it's beginning if python escape char "\" is present inside it.
        
        input: 
            fileFolderPathWithExt - a full file folder path (WITH extension)
        output:
            full file folder path if it exists. 
            False if it does not"""
        
        fileFolderPathWithExt2 = fileFolderPathWithExt.replace("\\", "/")  # "\" is an escaped characater in python
        
        folderExists = os.path.isfile(fileFolderPathWithExt2)
        
        if (folderExists == False): return False
        elif (folderExists != False): return fileFolderPathWithExt2
    
    
    def createFolder(self, folderPath):
        """
        creates a folder for a given folderPath.
        Returns "True" if folder is created or it it already exists. And "False" if folderPath is invalid
        """
        if os.path.isdir(folderPath):
            # "folderPath" exists
            folderCreated = True
            return folderCreated
        else:
            # "folderPath" does not exist
            try:
                # try creating the folder according to "folderPath"
                os.mkdir(folderPath)
                folderCreated = True
                return folderCreated
            except Exception, e:
                # invalid folderPath
                folderCreated = False
                return folderCreated
    
    
    def splitFolderAndFile(self, fileFolderPath):
        """
        split joined folder and file string into separate folder and file strings. It can have extension at the end of the filename or not.
        input: file with folder string. Example: "C:/libraries/someFolder/someLib.dll"
        output: 
            folder path
            fileName
            example: print ds.SplitFolderAndFile("C:/libraries/someFolder/someLib.dll")  # "C:/libraries/someFolder", "someLib.dll"  """
        folder = os.path.dirname(fileFolderPath)
        filename = os.path.basename(fileFolderPath)
        
        return folder, filename
    
    
    def dateNow(self, delimiter='.'):
        """return current date as a string"""
    
        now = datetime.datetime.now()
        
        date_now = now.strftime( '%Y{}%m{}%d'.format(delimiter, delimiter) )
        return date_now
    
    
    def timeNow(self, delimiter=':'):
        """return current time (hour,minute,second) as a string"""
        now = datetime.datetime.now()
        
        time_now = now.strftime( '%H{}%M{}%S'.format(delimiter, delimiter) )
        return time_now
    
    
    def checkInternetConnection(self):
        """
        check if PC is connected to internet
        """
        # connectedToInternet first check
        connectedToInternet1 = System.Net.NetworkInformation.NetworkInterface.GetIsNetworkAvailable()
        if connectedToInternet1 == False:
            # connectedToInternet second check
            try:
                client = System.Net.WebClient()
                client.OpenRead("http://www.google.com")
                connectedToInternet = True
            except:
                connectedToInternet = False
                # you are not connected to the Internet
        elif connectedToInternet1 == True:
            # no need for connectedToInternet second check
            connectedToInternet = True
        
        return connectedToInternet
    
    
    def downloadFile(self, downloadLink, downloadedFilePath):
        """
        downloading a file for the given link and filepath location.
        Returns "True" is file is successfully downloaded and "False" if download fails
        """
        try:
            # try "secure http" download
            client = System.Net.WebClient()
            client.DownloadFile(downloadLink, downloadedFilePath)
        except Exception, e:
            print "downloadFile_e1: ", e
            try:
                # "secure http" failed, try "http" download:
                filePathDummy, infoHeader = urllib.urlretrieve(downloadLink, downloadedFilePath)
            except Exception, e:
                print "downloadFile_e2: ", e
                # downloading of file failed
                fileDownloaded_success = False
                return fileDownloaded_success
        
        fileDownloaded_success = True
        return fileDownloaded_success
    
    
    def urlReader(self, _link):
        """
        return a http GET request as a string
        If faied, return 'file failed'
        """
        import subprocess
        
        # a) first try to download - via System.Net.WebClient.DownloadString
        with System.Net.WebClient() as client:
            try:
                JSON_asStr = client.DownloadString(_link);
            except System.Net.WebException as ex:
                #ex_str = str(ex)
                #raise ValueError(ex_str)
                JSON_asStr = 'file failed'
        
        
        # b) second try to download - via Windows CommandPrompt
        if (JSON_asStr == 'file failed'):
            # call url via Windows CommandPrompt
            cmd_str = 'curl -H "Accept: application/json" -X GET "{}"'.format(_link)  # do not change
            
            # return the results of the call in 'JSONasString' variable
            JSON_asStr2 = subprocess.Popen(cmd_str, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
            return JSON_asStr2
        
        
        return JSON_asStr
    
    
    def constructLocation(self, locationName, latitude, longitude, timeZone = 0, elevation = 0):
        """
        construct .epw file location
        """
        locationString = "Site:Location,\n" + \
                   "%s,\n" % locationName + \
                   "%s,      !Latitude\n" % latitude + \
                   "%s,     !Longitude\n" % longitude + \
                   "%s,     !Time Zone\n" % timeZone + \
                   "%s;       !Elevation" % elevation
        
        return locationString
    
    
    def deconstructLocation(self, location):
        """
        deconstruct a location string from .epw file
        """
        deconstructedLocationStrings = []
        splittedStrings = location.split("\n")
        for index,item in enumerate(splittedStrings):
            splittedStrings2 = item.split(",")
            firstItem = splittedStrings2[0].strip()
            if index == len(splittedStrings)-1:
                firstItem = firstItem.split(";")[0]
            deconstructedLocationStrings.append(firstItem)
        
        locationLabel, locationName, latitude, longitude, timeZone, elevation = deconstructedLocationStrings
        return locationName, latitude, longitude, timeZone, elevation
    
    
    def checkLocationData(self, location):
        """
        extended version of upper "deconstructLocation" method. Also fixes the locationName
        """
        if location:
            try:
                # location data
                locationName, latitude, longitude, timeZone, elevation = self.deconstructLocation(location)  # latitude positive towards north, longitude positive towards east
                locationNameCorrected = System.String.Replace(   System.String.Replace(  System.String.strip(System.String.Replace(System.String.Replace(locationName,"\\","_"), "/", "_") )  ," ", "_")   ,",", "_") # removing "/", "\", " ", "," from locationName
                
                latitude = float(latitude)
                longitude = float(longitude)
                timeZone = float(timeZone)
                elevation = float(elevation)
                
                validLocationData = True
                printMsg = "ok"
            
            except Exception, e:
                # something is wrong with "_location" input (the input is not from Ladybug "Import epw" component "location" ouput)
                locationNameCorrected = latitude = longitude = timeZone = elevation = None
                validLocationData = False
                printMsg = "Something is wrong with \"_location\" input."
        else:
            locationNameCorrected = latitude = longitude = timeZone = elevation = None
            validLocationData = False
            printMsg = "Please add location from Gismo's \"Create Location\" component, to this component's \"_location\" input."
        
        return locationNameCorrected, latitude, longitude, timeZone, elevation, validLocationData, printMsg
    
    
    def angle2northClockwise(self, north):
        """
        retuns north angle in radians and north vector for given either of these two
        this method is entirely copied from Ladybug_Ladybug "angle2northClockwise" method.
        """
        try:
            northVec = Rhino.Geometry.Vector3d.YAxis
            northVec.Rotate(-math.radians(float(north)),Rhino.Geometry.Vector3d.ZAxis)
            northVec.Unitize()
            return 2*math.pi-math.radians(float(north)), northVec
        except Exception, e:
            try:
                northVec = Rhino.Geometry.Vector3d(north)
                northVec.Unitize()
                return Rhino.Geometry.Vector3d.VectorAngle(Rhino.Geometry.Vector3d.YAxis, northVec, Rhino.Geometry.Plane.WorldXY), northVec
            except Exception, e:
                return 0, Rhino.Geometry.Vector3d.YAxis
    
    
    def checkShapeType(self, shapesLL):
        """
        determine which shapeType_ input has been used for "OSM Shapes" component based on its "shapes" output
        """
        numOfShapes = 0
        numOfShapesClosed = 0
        for shapesL in shapesLL:
            if (len(shapesL) != 0):
                # if branch is not empty
                numOfShapes += 1
                for shape in shapesL:
                    if isinstance(shape, Rhino.Geometry.Point):
                        # shapes_ are points
                        shapeType = 2
                        del shapesLL
                        return shapeType
                    else:
                        # check if shapeType = 0 (closed polygon) or 1 (polyline)
                        if shape.IsClosed:
                            numOfShapesClosed += 1
        
        if numOfShapes == numOfShapesClosed:
            # shapeType = 0 will always have closed polygons!
            shapeType = 0
        elif numOfShapes != numOfShapesClosed:
            # it may happen that shapeType = 1 will sometimes have a couple of closed polygons (those that are not added to "closed_ways_are_polygons=" line in osmconf.ini)
            shapeType = 1
        
        del shapesLL
        return shapeType
    
    
    def LiftingOSMshapesHeight(self, shapesDataTree, shapeType, bb_height, bb_bottomLeftCorner):
        # OSM shapes need to always be above the terrain in order for the brep created from them to be successfully cut from the terrain.
        # check how much OSM shapes need to be lifted above the terrain
        
        # all _shapes are plannar because they come from "OSM shapes" component. Therefor they all have the same Z coordinate.
        for shapesL in shapesDataTree.Branches:
            if (len(shapesL) > 0) and (shapesL[0] != None):
                if (shapeType == 0):
                    # polygons
                    OSMshapes_Zcoord = shapesL[0].PointAtStart.Z
                    break
                elif (shapeType == 1):
                    # polylines
                    OSMshapes_Zcoord = shapesL[0].PointAtStart.Z
                    break
                elif (shapeType == 2):
                    # points
                    OSMshapes_Zcoord = shapesL[0].Location.Z
                    break
        
        terrainHeighestPt_Zcoord = bb_bottomLeftCorner.Z + bb_height
        
        if (terrainHeighestPt_Zcoord >= OSMshapes_Zcoord):
            # highest terrain point is above the shapes plane. Move the shapes upwards
            liftingOSMshapesHeight = 2 * (terrainHeighestPt_Zcoord - OSMshapes_Zcoord)  # "2" is a dummy value
        elif (terrainHeighestPt_Zcoord < OSMshapes_Zcoord):
            # highest terrain point is below the shapes plane. This is fine, but still move the shapes upwards in case some unexpected issue arises
            liftingOSMshapesHeight = 1.2 * (OSMshapes_Zcoord - terrainHeighestPt_Zcoord)  # "1.2" is a dummy value
        
        return liftingOSMshapesHeight
    
    
    def flatten_dataTree(self, dataTree):
        """
        convert a data tree content to a single list
        """
        branchesLL = dataTree.Branches
        branchesLL_flattened = []
        for branchL in branchesLL:
            if (len(branchL) > 0):
                branchesLL_flattened.extend(branchL)
        
        del dataTree
        del branchesLL
        return branchesLL_flattened
    
    
    def modify_dataTree(self, oldDataTree, newBranchIndex, newBranchList):
        """
        modify the datatree list on a certain branch index
        """
        newDataTree = Grasshopper.DataTree[object]()
        
        oldDataTree_Paths = oldDataTree.Paths
        for branchIndex, oldBranchList in enumerate(oldDataTree.Branches):
            if (branchIndex == newBranchIndex):
                newDataTree.AddRange(newBranchList, oldDataTree_Paths[branchIndex])
            else:
                newDataTree.AddRange(oldBranchList, oldDataTree_Paths[branchIndex])
        del oldDataTree
        return newDataTree
    
    
    def datatree_shiftPaths(self, dataTree):
        """
        shifting data tree paths by -1
        """
        
        branches = dataTree.Branches
        paths = dataTree.Paths
        
        newPaths = [p.CullElement() for p in paths]
        
        shiftedPathsTree = Grasshopper.DataTree[object]()
        for i in xrange(dataTree.BranchCount):
            shiftedPathsTree.AddRange(branches[i], newPaths[i])
        
        del dataTree
        return shiftedPathsTree
    
    
    def grasshopperDTtoLL(self, DT):
        """convert grasshoppper data tree to a list of lists"""
        LL = []
        for i in xrange(DT.BranchCount):
            branch_dotNET_L = DT.Branches[i]
            branch_L = [DT.Branches[i][g]    for g in xrange(DT.Branches[i].Count)]
            LL.append(branch_L)
        return LL
    
    
    def flattenLL(self, LL):
        """flatten (convert to a regular list) a list of lists"""
        L = [item     for subL in LL     for item in subL]
        return L
    
    
    def LLtranspose(self, LL, emptyItem=None):
        """replace rows with columns in a list of list
        This func supports row_L with equal or different length.
        
        input:
            LL
            emptyItem - if not equal to None, then that value will be used to fill in gaps between row_L of different sizes
        output:
            LL_flip"""
        
        # a) find longest length among all row_L
        maxCol = len(LL[0])  # iniv
        
        for row_L in LL:
            rowLength = len(row_L)
            if rowLength > maxCol:
                maxCol = rowLength
        
        
        # b) create 'LL_flip'
        LL_flip = []
        
        for colIndex in xrange(maxCol):
            
            LL_flip.append([])
            for row_L in LL:
                if colIndex < len(row_L):
                    LL_flip[colIndex].append(row_L[colIndex])
                else:
                    # optional addition of 'emptyItem'
                    if emptyItem:
                        LL_flip[colIndex].append( emptyItem )
        
        return LL_flip
    
    
    def joinMeshes(self, mesh_L):
        """join a list of meshes in to a single mesh"""
        joinedMesh = Rhino.Geometry.Mesh()
        joinedMesh.Append(mesh_L)
        
        return joinedMesh
    
    
    def toMesh(self, brep, minEdgeLength=tol, maxEdgeLength=0, jaggedSeams=False, simplePlanes=False):
        """convert brep to mesh"""
        
        meshParam = Rhino.Geometry.MeshingParameters()
        
        # mesh parameters
        meshParam.JaggedSeams = jaggedSeams
        meshParam.SimplePlanes = simplePlanes
        
        # assign 'minEdgeLength' and 'maxEdgeLength' parameters only if they do not contain default func values (because if I remember correctly they created issues with non default values, at some point in past)
        if (minEdgeLength != tol):
            meshParam.MinimumEdgeLength = minEdgeLength  # in mm
        if (maxEdgeLength != 0):
            meshParam.MaximumEdgeLength = maxEdgeLength  # in mm
        
        
        
        if (type(brep) == Rhino.Geometry.Extrusion):
            brep = brep.ToBrep()
        
        # convert brep to mesh
        meshes = Rhino.Geometry.Mesh.CreateFromBrep(brep, meshParam)
        joinedMesh = Rhino.Geometry.Mesh()
        for mesh in meshes:
            joinedMesh.Append(mesh)
        
        return joinedMesh
    
    
    def boundingBox_properties(self, geometryL, accurate=True):
        """
        getting volume, centroid, corner pts and dimensions of a bounding box created around a "geometry"
        """
        ####unionBB = geometry.GetBoundingBox(accurate)
        #mesh = Rhino.Geometry.Mesh.CreateFromBrep(geometry)[0]
        #unionBB = Rhino.Geometry.Mesh.GetBoundingBox(mesh, accurate)
        
        bbL = []
        for geo in geometryL:
            bbL.append(geo.GetBoundingBox(accurate))
        
        unionBB = bbL[0]  # initial value
        for i in range(len(bbL)-1):
            unionBB = Rhino.Geometry.BoundingBox.Union(unionBB, bbL[i+1])
        
        
        bb_centroid = unionBB.Center
        
        bb_edges = unionBB.GetEdges()
        bb_length = bb_edges[0].Length
        bb_depth = bb_edges[1].Length
        bb_height = bb_edges[8].Length
        
        bb_corners = unionBB.GetCorners()
        bb_bottomLeftCorner = bb_corners[0]
        bb_bottomRightCorner = bb_corners[1]
        bb_topRightCorner = bb_corners[2]
        bb_topLeftCorner = bb_corners[3]
        
        try:
            bb_volume = Rhino.Geometry.VolumeMassProperties.Compute(unionBB.ToBrep()).Volume
        except:
            bb_volume = None
        
        return bb_volume, bb_centroid, bb_length, bb_depth, bb_height, bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner
    
    
    def textJustificationEnumeration(self, justificationIndex):
        """
        get TextJustification type based on justificationIndex
        """
        # justificationIndices:
        # 0 - bottom left (default)
        # 1 - bottom center
        # 2 - bottom right
        # 3 - middle left
        # 4 - center
        # 5 - middle right
        # 6 - top left
        # 7 - top middle
        # 8 - top right
        
        constantsList  = [0, 2, 4, 131072, 131074, 131076, 262144, 262146, 262148]
        try:
            justificationConstant = constantsList[justificationIndex]
        except:
            # if 0 < justificationIndex > 8
            justificationConstant = 0
        textJustification = System.Enum.ToObject(Rhino.Geometry.TextJustification, justificationConstant)
        return textJustification
    
    
    def text2srfOrMesh(self, returnSrfOrMesh, textL, textStartPt, textSize, fontName="Verdana", bold=True, italic=False, justificationIndex=0):
        """
        convert text to surface or mesh
        this method is based on "text2srf" method from Ladybug plugin
        """
        textObjectIdsL = []
        textSrfsL = []
        textMeshesL = []
        plane = Rhino.Geometry.Plane(textStartPt, Rhino.Geometry.Vector3d(0,0,1))
        joinedTextGeometry = Rhino.Geometry.Mesh()  # joined final text mesh
        textJustification = self.textJustificationEnumeration(justificationIndex)
        
        for text in textL:
            #textString = str(text)
            textString = unicode(text)
            textObjectId = Rhino.RhinoDoc.ActiveDoc.Objects.AddText(textString, plane, textSize, fontName, bold, italic, textJustification)
            textObjectIdsL.append(textObjectId)
            textObject = Rhino.RhinoDoc.ActiveDoc.Objects.Find(textObjectId)
            textCrvs = textObject.Geometry.Explode()
            joinedTextCrvs = Rhino.Geometry.Curve.JoinCurves(textCrvs)
            textSrfs = Rhino.Geometry.Brep.CreatePlanarBreps(joinedTextCrvs)
            if returnSrfOrMesh == "srf":
                textSrfsL.extend(textSrfs)
            elif returnSrfOrMesh == "mesh":
                textSrfsL.extend(textSrfs)
        
        tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        if returnSrfOrMesh == "srf":
            joinedTextGeometry = Rhino.Geometry.Brep.MergeBreps(textSrfsL, tol)
        elif returnSrfOrMesh == "mesh":
            for brep in textSrfsL:
                brepMeshes = Rhino.Geometry.Mesh.CreateFromBrep(brep)
                for brepMesh in brepMeshes:
                    brepMesh.VertexColors.CreateMonotoneMesh(System.Drawing.Color.Black)
                    joinedTextGeometry.Append(brepMesh)
            del textSrfsL
        
        # deleting
        quiet = True
        for textObjectId in textObjectIdsL:
            Rhino.RhinoDoc.ActiveDoc.Objects.Delete(textObjectId, quiet)
        
        return joinedTextGeometry
    
    
    def defaultCustomColors(self):
        """
        a list of Gismo's default customColors_ (gradient blue-green-red)
        """
        defaultCustomColors = [
        System.Drawing.Color.FromArgb(2,83,250),
        System.Drawing.Color.FromArgb(68,219,226),
        System.Drawing.Color.FromArgb(155,253,126),
        System.Drawing.Color.FromArgb(173,255,25),
        System.Drawing.Color.FromArgb(253,255,16),
        System.Drawing.Color.FromArgb(251,192,31),
        System.Drawing.Color.FromArgb(248,64,74)]
        
        return defaultCustomColors
    
    
    def read_legendBakePar(self, legendBakePar):
        """
        deconstruct "legendBakePar_" input to its parts
        """
        legendBakePar_LL = legendBakePar.Branches
        
        if (len(legendBakePar_LL) == 0)  or  ((len(legendBakePar_LL) == 1) and (legendBakePar_LL[0][0] == None)):
            # a) "legendBakePar_" input is empty, or
            # b) "Legend Bake Parameters" component is not ran for some reason (its legendBakePar output returns "None").
            legendStyle = 0  # rectangle cells
            legendPlane = None  # pick bounding box bottom right corner point
            maxValue = None  # pick the largest value
            minValue = None  # pick the smallest value
            
            customColors = []
            
            numLegendCells = 12
            fontName = "Verdana"
            fontSize = None  # calculate it according to the bounding box length
            numDecimals = 2
            legendUnit = None  # use the legendUnit defined by the component
            customTitle = None  # use the title defined by the component
            scale = 1
            
            layerName = None  # use layerName defined by the component
            layerColor = None  # use layerColor defined by the component
            layerCategoryName = None  # no layer category will be created
            
            return legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName
        
        else:
            # something inputted to "legendBakePar_"
            legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = legendBakePar_LL  # all parts are lists now
            
            return legendStyle[0], legendPlane[0], maxValue[0], minValue[0], list(customColors), numLegendCells[0], fontName[0], fontSize[0], numDecimals[0], legendUnit[0], customTitle[0], scale[0], layerName[0], layerColor[0], layerCategoryName[0]
    
    
    def createTitle(self, returnSrfOrMesh, geometryL, textL, customTitle=None, textStartPt=None, textSize=None, fontName=None, bold=None, italic=None, textJustification=None):
        """
        create title below a certain geometryL
        """
        accurate = True
        bb_volume, bb_centroid, bb_length, bb_depth, bb_height, bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner = self.boundingBox_properties(geometryL, accurate)
        
        if (textSize == None):
            textSize = bb_depth / 25
        if (fontName == None):
            fontName = "Verdana"
        if (bold == None):
            bold = False
        if (italic == None):
            italic = False
        if (textStartPt == None):
            textStartPt = bb_bottomLeftCorner
        if (textJustification == None):
            textJustification = 6  # top left
        if (customTitle == None):
            # nothing inputted into "customTitle_" input of "Legend Bake Parameters" component. Use the upper "textL" as a string for the title text
            pass
        else:
            # something inputted into "customTitle_" input of "Legend Bake Parameters" component. Use the "customTitle_" input as a string for the title text
            
            # fixing the issue with "customTitle_" input not registring the "\n" for a new line
            customTitle2 = customTitle.replace("\\n", "\\\n")
            customTitle3 = customTitle2.replace("\\", "")
            textL = [customTitle3]
        
        
        textStartPt.Y = textStartPt.Y - textSize
        joinedTitleTextGeometry = self.text2srfOrMesh(returnSrfOrMesh, textL, textStartPt, textSize, fontName, bold, italic, textJustification)
        
        return joinedTitleTextGeometry, textStartPt, textSize
    
    
    def numberToColor(self, values, customColors, minB=None, maxB=None, tol=0.001):
        """
        interpolate numbers to a gradient between a list of colors
        """
        if (len(customColors) == 0):
            customColors = self.defaultCustomColors()
        
        # check if all values in input 'values' are the same
        sum_values = sum(values)
        sum_values2 = len(values)*values[0]
        if self.epsilonEquals(sum_values, sum_values2, tol):
            # all items in "values" are the same. Return the bottom most color
            return [customColors[0]] * len(values)
        
        
        # checking for "minB" and "maxB"
        minValue = min(values)
        maxValue = max(values)
        if (minB != None):
            if (minB >= minValue):  # check in case "minValue_" is smaller than the smallest value in "values"
                minValue = minB
        if (maxB != None):
            if (maxB <= maxValue):  # check in case "maxValue_" is larger than the largest value in "values"
                maxValue = maxB
        
        # edit all "values" so that they are not smaller than "minValue", and larger than "maxValue"
        valuesChangedFor_minB_maxB = []
        for value in values:
            if value < minValue:
                valuesChangedFor_minB_maxB.append(minValue)
            elif value > maxValue:
                valuesChangedFor_minB_maxB.append(maxValue)
            else:
                valuesChangedFor_minB_maxB.append(value)
        
        # normalize the "values" to range(0,1)
        normalizedValues = [(valueChanged - minValue) / (maxValue - minValue)  for valueChanged in valuesChangedFor_minB_maxB]
        
        # divide range(0,1) according to the number of customColors items
        stepValueLimit = 1/(len(customColors)-1)
        valueLimit = 0
        valuesLimits_perEachCustomColor = []
        for i in range(len(customColors)-1):
            valuesLimits_perEachCustomColor.append(valueLimit)
            valueLimit += stepValueLimit
        valuesLimits_perEachCustomColor.append(1.0)  # this is done to avoid bugs with last value in "valuesLimits_perEachCustomColor" sometimes being 0.999..
        
        # generate legendColors
        legendColors = []
        for i in range(len(normalizedValues)):
            color = None  # initial value
            normalizedValue = normalizedValues[i]
            
            for index, valueLimit in enumerate(valuesLimits_perEachCustomColor):
                if valueLimit >= normalizedValue:
                    if index == 0:
                        # if value is between 0 and next valueLimit
                        color1 = customColors[index]
                        color2 = customColors[index+1]
                        minValue = valuesLimits_perEachCustomColor[index]
                        maxValue = valuesLimits_perEachCustomColor[index+1]
                    else:
                        color1 = customColors[index-1]
                        color2 = customColors[index]
                        minValue = valuesLimits_perEachCustomColor[index-1]
                        maxValue = valuesLimits_perEachCustomColor[index]
                    
                    normalizedValue2 = (normalizedValue - minValue) / (maxValue - minValue)  # normalized for a range between two "valuesLimits_perEachCustomColor" numbers
                    
                    # based on: http://stackoverflow.com/a/22649247/3137724
                    resultRed = color1.R + normalizedValue2 * (color2.R - color1.R)
                    resultGreen = color1.G + normalizedValue2 * (color2.G - color1.G)
                    resultBlue = color1.B + normalizedValue2 * (color2.B - color1.B)
                    
                    color = System.Drawing.Color.FromArgb(resultRed, resultGreen, resultBlue)
                    
                    legendColors.append(color)
                    break
        
        return legendColors
    
    
    def isNumber(self, str2):
        """
        check if a string can be converted to a number
        """
        try:
            number = float(str2)
            return True
        except:
            return False
    
    
    def createLayer(self, layParentName, laySubName, projectName, newLayer, category, laySubName_color=None, category_color=None, legendBakePar=Grasshopper.DataTree[object]() ):
        """
        create a layers tree
        """
        # read the "legendBakePar_"
        legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, customLegendUnit, customTitle, scale, customLayerName, customLayerColor, customLayerCategoryName = self.read_legendBakePar(legendBakePar)
        
        if (customLayerName == None):
            # nothing added to "layerName_" input of "Legend Bake Parameters" component
            #category = category
            pass
        else:
            # something added to "layerName_" input of "Legend Bake Parameters" component
            category = customLayerName
        
        if (customLayerColor == None) and (category_color != None):
            # nothing added to "layerColor_" input of "Legend Bake Parameters" component, AND "category_color" has been defined through inputs
            #category_color = category_color
            pass
        elif (customLayerColor != None):
            # something added to "layerColor_" input of "Legend Bake Parameters" component
            category_color = customLayerColor
        elif (customLayerColor == None) and (category_color == None):
            # nothing added to "layerColor_" input of "Legend Bake Parameters" component, AND "category_color" has NOT been defined through inputs
            category_color = System.Drawing.Color.FromArgb(0,0,0)  # default, black
        
        if (customLayerCategoryName == None):
            # nothing added to "layerCategoryName_" input of "Legend Bake Parameters" component
            #layerCategoryName = layerCategoryName
            pass
        else:
            # something added to "layerCategoryName_" input of "Legend Bake Parameters" component
            projectName = customLayerCategoryName
        
        
        # add "newLayerCategory_ (boolean)" input to "Legend Bake Parameters" component
        newLayerCategory = False  # default, until "newLayerCategory_ (boolean)" input gets added to the "Legend Bake Parameters" component
        
        
        if (laySubName_color == None):
            laySubName_color = System.Drawing.Color.FromArgb(100,191,70)  # green
        
        
        
        #  setup parent and sublayers
        layerT = Rhino.RhinoDoc.ActiveDoc.Layers
        layParent = Rhino.DocObjects.Layer.GetDefaultLayerProperties()
        laySub = Rhino.DocObjects.Layer.GetDefaultLayerProperties()
        laySubPath = layParentName + "::" + laySubName
        layParent.Name = layParentName
        laySub.Name = laySubName
        layParent.Color = System.Drawing.Color.FromArgb(29,42,85)
        laySub.Color = laySubName_color
        
        # adding parent/sublayers
        layParentIndex = layerT.Find(layParentName, True)
        if layParentIndex >= 0:
            parent = layerT[layParentIndex]
            laySub.ParentLayerId = parent.Id
            index = layerT.Add(laySub)
        else:
            layerT.Add(layParent)
        laySubIndex = Rhino.DocObjects.Tables.LayerTable.FindByFullPath(layerT, laySubPath, True)
        if laySubIndex < 0:
            layParentIndex = layerT.Find(layParentName, True)
            parent = layerT[layParentIndex]
            laySub.ParentLayerId = parent.Id
            index = layerT.Add(laySub)
        
        # check projectName
        if projectName:
            projectName = str(projectName)
        else:
            projectName = "Project"
        if Rhino.DocObjects.Layer.IsValidName(projectName) == False: 
            print "Layer name: '" +  projectName + "' is not a valid layer name"
            return None, None
        
        # setting up and adding projectname_n layers
        layerPCAIndex = layerT.Find(laySubName, True)
        layerPCA = layerT[layerPCAIndex]
        project_n = Rhino.DocObjects.Layer.GetDefaultLayerProperties()
        project_n.IsVisible = False
        project_n.ParentLayerId = layerPCA.Id
        projectNameLayers = layerPCA.GetChildren()
        if not projectNameLayers:
            projectName_n = projectName + "_0"
            project_n.Name = projectName_n
            project_nIndex = layerT.Add(project_n)
        elif projectNameLayers:
            integers = []
            try:
                for l in projectNameLayers:
                    if projectName in l.Name:
                        integers.append(int(l.Name.split(projectName + "_")[-1]))
                        lastLayer = l.Name
                integers.sort()
                maxInt = integers[-1]
                if newLayer == True:
                    projectName_n = projectName + "_" + str(maxInt + 1)
                    project_n.Name = projectName_n
                    project_nIndex = layerT.Add(project_n)
                else: 
                    project_nIndex = layerT.Find(lastLayer, True)
            except:
                project_n.Name = projectName + "_0"
                project_nIndex = layerT.Add(project_n)
        
        # setting up and adding category layers
        project_n = layerT[project_nIndex]
        categoryL = Rhino.DocObjects.Layer.GetDefaultLayerProperties()
        if (category_color == None):
            category_color = System.Drawing.Color.FromArgb(0,0,0)  # default, black color of the final layer
        categoryL.Color = category_color
        categoryL.ParentLayerId = project_n.Id
        projectNameLayers = project_n.GetChildren()
        integers = []
        if projectNameLayers:
            for l in projectNameLayers:
                splittedLayerName = l.Name.split("_")
                layerNameWithoutNumber = "_".join(splittedLayerName[:-1])
                #layerNameWithoutNumber = l.Name.split("_")[0]
                if category == layerNameWithoutNumber:
                    integers.append(int(l.Name.split(category + "_")[-1]))
            
            try:
                integers.sort()
                maxInt = integers[-1]
                categoryName_n = category + "_" +str(int(maxInt)+1)
                categoryL.Name = categoryName_n
                categoryIndex = layerT.Add(categoryL)
            except Exception, e:
                categoryL.Name = category  + "_0"
                categoryIndex = layerT.Add(categoryL)
                maxInt = -1
        else:
            categoryL.Name = category + "_0"
            categoryIndex = layerT.Add(categoryL)
            maxInt = -1
        
        return categoryIndex, categoryL.Name
    
    
    def bakeGeometry(self, geometryToBakeL, layerIndex):
        """
        add the geometry to the Rhino scene
        """
        # attributes
        attr = Rhino.DocObjects.ObjectAttributes()
        attr.LayerIndex = layerIndex
        attr.ColorSource = Rhino.DocObjects.ObjectColorSource.ColorFromObject
        attr.PlotColorSource = Rhino.DocObjects.ObjectPlotColorSource.PlotColorFromObject
        
        # bake
        geometryBaseTypes = [Rhino.Geometry.AnnotationBase, Rhino.Geometry.Brep, Rhino.Geometry.BrepLoop, Rhino.Geometry.Curve, Rhino.Geometry.PolyCurve, Rhino.Geometry.NurbsCurve, Rhino.Geometry.DetailView, Rhino.Geometry.Hatch, Rhino.Geometry.Light, Rhino.Geometry.Mesh, Rhino.Geometry.Point, Rhino.Geometry.Point3dGrid, Rhino.Geometry.PointCloud, Rhino.Geometry.Surface, Rhino.Geometry.NurbsSurface, Rhino.Geometry.TextDot]
        geometryIds = []
        for obj in geometryToBakeL:
            if type(obj) in geometryBaseTypes:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.Add(obj, attr)
            elif type(obj) == Rhino.Geometry.Circle:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddCircle(obj, attr)
            elif type(obj) == Rhino.Geometry.Extrusion:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddExtrusion(obj, attr)
            elif type(obj) == Rhino.Geometry.Line:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddLine(obj, attr)
            elif type(obj) == Rhino.Geometry.Plane:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddPoint(obj.Origin, attr)
            elif type(obj) == Rhino.Geometry.Point3d:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddPoint(obj, attr)
            elif type(obj) == Rhino.Geometry.Polyline:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddPolyline(obj, attr)
            elif type(obj) == Rhino.Geometry.Sphere:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddSphere(obj, attr)
            elif type(obj) == Rhino.Geometry.TextEntity:
                id = Rhino.RhinoDoc.ActiveDoc.Objects.AddText(obj, attr)
            else:
                #del geometryToBakeL
                print "######## no valid type has been found for particular item in \"geometryToBakeL\""
                print "type(obj): ", type(obj)
                return None  # no valid type has been found for particular item in "geometryToBakeL"
            geometryIds.append(id)
        
        del geometryToBakeL
        return geometryIds
    
    
    def groupGeometry(self, groupName, geometryIds):
        """
        group the rhino geometry based on rhino ids
        """
        groupIndex = Rhino.RhinoDoc.ActiveDoc.Groups.Add(groupName + "_" + str(time.time()))
        Rhino.RhinoDoc.ActiveDoc.Groups.AddToGroup(groupIndex, geometryIds)
        del geometryIds
        return groupIndex
    
    
    def arrayToList2(self, arr):
        """convert a dotNET array (and NOT nested dotNET array!) to a python list.
        This function can be used to convert StrongBox[Array[type]] to python list"""
        
        L = []
        
        enumerator = arr.GetEnumerator()
        
        while enumerator.MoveNext():
            item = enumerator.Current
            L.append( item )
        
        return L


class IO():
    """
    methods to read and export files
    """
    def localizeFloats(self, row, decimal=','):
        return [
            str(el).replace('.', decimal) if isinstance(el, float) else el 
            for el in row]
    
    
    def readCSV(self, CSV_filefull, delimiter_=';'):
        """read the csv file as the List of Lists"""
        
        import codecs
        
        with open(CSV_filefull) as csv_file:
            csv_reader = csv.reader(codecs.EncodedFile(csv_file, 'utf-8', 'utf-8-sig'), delimiter=delimiter_)
            
            csvValue_LL = []
            
            for row_splitted_L in csv_reader:
                row_splitted_encoded_L = [str2.encode('utf-8')  if isinstance(str2, str) else str2  for str2 in row_splitted_L]
                csvValue_LL.append(row_splitted_encoded_L)
        
        return csvValue_LL
    
    
    def exportCSV(self, csvValueLL, filename, folder, delimiter_=';', decimal=',', _encode='utf-8'):
        """export a list of values a .csv file
        input:
            csvValueLL - a list of lists, where each sublist represents a single line (row)
        output:
            if .csv file successfully saved, then its full folder path.
            Otherwise None"""
        
        
        # create the 'folder'
        prep_gismo = Preparation()
        folder_created = prep_gismo.createFolder(folder)
        
        if (folder_created == False):
            raise ValueError("@@    'exportCSV' func terminated. Input folder: '{}' can not be found/created.".format(folder))
        
        elif (folder_created != False):
            CSV_filefullWithExt = os.path.join(folder, filename + '.csv')
            
            # test if .csv file can be created
            try:
                with open(CSV_filefullWithExt, mode='w') as csvfile:
                    pass
            except:
                printMsg = "@@    'exportCSV' func terminated because csv file could not be created. Due to: \n" + \
                                  "1) CSV file is already OPENED. Close it.  or \n" + \
                                  "2) folder path is incorrect (no such partion exists, or folder parth contains invalid characters. or \n" + \
                                  "3) filename is invalid"
                
                raise ValueError(printMsg)
            
            
            
            # finally write values to a .csv file
            with open(CSV_filefullWithExt, mode='w') as csvfile:
                csvwriter = csv.writer(csvfile, delimiter=delimiter_, quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
                for subL in csvValueLL:
                    localizedFloat_L = self.localizeFloats(subL, decimal)
                    
                    if _encode:
                        localizedFloat_and_encoding_L = [str2.encode(_encode)  if isinstance(str2, str) else str2  for str2 in localizedFloat_L]
                    else:
                        localizedFloat_and_encoding_L = [str2  for str2 in localizedFloat_L]
                    
                    csvwriter.writerow(localizedFloat_and_encoding_L)
            
            return CSV_filefullWithExt


class CreateGeometry():
    """
    methods which create some sort of geometry
    """
    def polygonCrv(self, pln, radius=10, numOfSeg=4, filletRadius=0):
        """create a polygon at the 'pln'. Polygon's starting point will be at 'pln's Y+, counter-clockwise oriented.
        input:
            pln - plane 
            radius - cirle radius on which polygon points lie
            numOfseg - number of polygon segments
            filletRadius - the fillet of polygon corners. By default it is set to 0 - no fillet. ## WARNING ## Too big filletRadius (depending on 'radius' value) may create corrupted crv.
        output: polygon crv"""
        # based on: https://blenderartists.org/t/what-is-a-good-way-to-create-polygons-via-python/589082/2
        
        # create polygon crv in XY plane, then transform it to 'pln' input
        
        angleD_max = 360  # do not change. Full circle
        angleD = 0  # initial value
        step = angleD_max / numOfSeg  # initial value
        
        controlPt_L = []
        for i in range(numOfSeg):
            angleR = math.radians(angleD)
            controlPt = rg.Point3d(math.sin(angleR)*radius, math.cos(angleR)*radius, 0) 
            angleD += step
            
            controlPt_L.append(controlPt)
        
        controlPt_L.append(controlPt_L[0])  # close the ply
        
        # upper code creates controlPt clockwise starting from Y+ (the starting point is at Y+)
        controlPt_L.reverse()
        
        # fillet
        polygon_ply = rg.Polyline(controlPt_L)
        polygon_crv = polygon_ply.ToPolylineCurve()  # conver ply to crv
        if (filletRadius > 0):
            polygonFillet_crv = rg.Curve.CreateFilletCornersCurve(polygon_crv, filletRadius, tol, tolAngleD)
        else: polygonFillet_crv = polygon_crv
        
        # transfrom 'polygonFillet_crv' from XY plane to 'pln'
        worldXY = rg.Plane(rg.Point3d(0,0,0), rg.Vector3d(0,0,1))
        xform = rg.Transform.PlaneToPlane(worldXY, pln)
        polygonFillet_crv.Transform(xform)
        
        return polygonFillet_crv
    
    
    def explodeCrv(self, crv, returnItselfIfLine=False):
        """Explodes, or un-joins, one curves. Unlike rs.ExplodeCurves this method returns crv objects not guids
        ## WARNING ## if a crv can not be exploded, and empty list will be returned !!! To prevent this, and return the crv itself, set the input 'returnItselfIfLine=True'.
        input: crv's object or guid
        output:
            a list of exploded crv objects
            or if 'crv' is a line then:
                and empty list if 'returnItselfIfLine=False'
                or the input '[crv]' itself if 'returnItselfIfLine=True'.
        """
        if type(crv) == System.Guid:
            crv = rs.coercecurve(crv)
        
        if type(crv) == rg.Polyline:
            segL = []
            for i in range(crv.SegmentCount):
                segL.append( crv.SegmentAt(i) )
            return segL
        else:
            segL = crv.DuplicateSegments()
            if (len(segL) == 0):  # 'crv' is a line
                if returnItselfIfLine:
                    return [transform.Copy(crv)]  # return the line itself, instead of an empty list
                else:
                    return []
            else:
                return segL
    
    
    def srfDivide(self, BF, U, V):
        """create a grid of pts on a surface.
        input:
            BF
            U - number of divisions in U direction + 1
            V - number of divisions in V direction + 1
        output:
            divPt_L, divPtNormal_L, UV_LL"""
        
        Udomain = BF.Domain(0)
        Vdomain = BF.Domain(1)
        
        U_step = 1 / U
        V_step = 1 / V
        
        U_t_normalized = 0
        V_t_normalized = 0
        
        
        
        # output lists
        divPt_L = []
        divPtNormal_L = []
        UV_LL = []
        
        for i in xrange(U + 1):
            for g in xrange(V + 1):
                
                U_t = Udomain.ParameterAt(U_t_normalized)
                V_t = Vdomain.ParameterAt(V_t_normalized)
                
                divPt = BF.PointAt(U_t, V_t)
                isPtOnBF = BF.IsPointOnFace(U_t, V_t)
                if (isPtOnBF == rg.PointFaceRelation.Exterior):  # add 'None' for divPt which is outside of BF. This is consistent with grasshopper 'Divide Surface' component
                    # pt is outside of BF. Add 'None'
                    divPt = None
                    divPtNormal = None
                else:
                    divPtNormal = BF.NormalAt(U_t, V_t)
                
                
                # append to lists
                divPt_L.append( divPt )
                divPtNormal_L.append( divPtNormal )
                UV_LL.append( (U_t, V_t) )
                
                
                V_t_normalized += V_step
            
            V_t_normalized = 0  # reset V_t_normalized
            U_t_normalized += U_step
        
        
        return divPt_L, divPtNormal_L, UV_LL
    
    
    def explodeMesh(self, mesh):
        """explode a mesh to mesh faces, and then convert them to individual meshes.
        input:
            mesh to explode
        output:
            a) a list of exploded mesh faces converted to individual meshes on success.
            b) if input mesh has only one mesh face, then the copy itself will be returned
            c) if explode failed, then 'None' will be returned."""
        
        mesh_EM_L = rg.Mesh.ExplodeAtUnweldedEdges(mesh)
        
        if (mesh_EM_L.Count == 0):  # I think this happens when input mesh has only one mesh face, so the explode is not possible
            return [mesh]
        
        return mesh_EM_L
    
    
    def calculateMeshFaceAreas(self, mesh):
        """
        calculate each mesh face area
        """
        def triangleMeshFaceArea(A,B,C):
            # Heron's formula
            a = A.DistanceTo(B)
            b = B.DistanceTo(C)
            c = A.DistanceTo(C)
            s = (a+b+c)/2  # triangle semiperimeter
            triangleMeshFaceArea = math.sqrt(s * (s - a) * (s - b) * (s - c))
            
            return triangleMeshFaceArea
        
        meshFaces = mesh.Faces
        meshVertices = mesh.Vertices
        meshFaceAreas = []
        for mFace in meshFaces:
            if mFace.IsTriangle:
                triangleMeshFaceArea1 = triangleMeshFaceArea(meshVertices[mFace.A], meshVertices[mFace.B], meshVertices[mFace.C])
                triangleMeshFaceArea2 = 0 
            elif mFace.IsQuad:
                d1 = meshVertices[mFace.A].DistanceTo(meshVertices[mFace.C])
                d2 = meshVertices[mFace.B].DistanceTo(meshVertices[mFace.D])
                if d1 > d2:
                    triangleMeshFaceArea1 = triangleMeshFaceArea(meshVertices[mFace.D], meshVertices[mFace.A], meshVertices[mFace.B])
                    triangleMeshFaceArea2 = triangleMeshFaceArea(meshVertices[mFace.D], meshVertices[mFace.B], meshVertices[mFace.C])
                else:
                    triangleMeshFaceArea1 = triangleMeshFaceArea(meshVertices[mFace.A], meshVertices[mFace.B], meshVertices[mFace.C])
                    triangleMeshFaceArea2 = triangleMeshFaceArea(meshVertices[mFace.A], meshVertices[mFace.C], meshVertices[mFace.D])
            meshFaceAreas.append(triangleMeshFaceArea1+triangleMeshFaceArea2)
        
        return meshFaceAreas
    
    
    def meshFromPoints(self, u, v, pts, meshColors=None):
        """
        create a mesh from a grid of points
        """
        mesh = Rhino.Geometry.Mesh()
        if (meshColors == None) or (len(meshColors) == 0):
            for pt in pts:
                mesh.Vertices.Add(pt)
        else:
            for i,pt in enumerate(pts):
                mesh.Vertices.Add(pt)
                mesh.VertexColors.Add(meshColors[i])
        for i in xrange(1,u):
            for k in xrange(1,v):
                mesh.Faces.AddFace(k-1+(i-1)*v, k-1+i*v, k-1+i*v+1, k-1+(i-1)*v+1)
        
        return mesh
    
    
    def colorMeshVertices(self, mesh, colors):
        """
        color the vertices of a mesh in-place!
        """
        mesh_numOfVertices = mesh.Vertices.Count
        mesh.VertexColors.Clear()
        
        for i in range(mesh_numOfVertices):
            mesh.VertexColors.Add(colors[i])
        
        del colors
        return mesh  # colored mesh
    
    
    def convertCrvToPolyline(self, crv, explodePolyline = False):
        """
        convert a curve to polyline. For a given single curve, it returns a list!
        """
        nurbsCrv = crv.ToNurbsCurve()
        convertedToPolyline_Success, polyline = nurbsCrv.TryGetPolyline()
        if (convertedToPolyline_Success == True):
            # conversion succeeded
            pass
        if (convertedToPolyline_Success == False):
            # conversion failed. "crv" is not a polyline nor a polycurve
            distanceTol = 0.0
            angleTol = 0.0
            minimumSegmentLength = 0.5  # in rhino document units
            polyline, numOfSegments = ghc.CurveToPolyline(crv, distanceTol, angleTol, minimumSegmentLength)
        
        if (explodePolyline == True):
            nurbsCrv2 = polyline.ToNurbsCurve()
            explodedLines = nurbsCrv2.DuplicateSegments()
            if (len(explodedLines) == 0):
                # the "polyline" was a line, it can not be exploded further
                return [polyline]
            elif (len(explodedLines) > 0):
                return explodedLines
        else:
            return [polyline]
    
    
    def curveRoundedOrNot(self, crv):
        """
        check if the curve has rounded corners, or they are all sharp
        """
        continuityType = 2
        cornerPts = rs.CurveDiscontinuity(crv, continuityType)
        cornerPts.extend(cornerPts)
        startPt = crv.PointAtStart
        cornerPts.append(startPt)
        
        maximumDistance = 0
        for pt in cornerPts:
            success, t = crv.ClosestPoint(pt, maximumDistance)
            pt, tangent, angleR = ghc.EvaluateCurve(crv, t)  # "angleR" - angle between incoming vs outgoing curve at "t"
            angleD = math.degrees(angleR)
            if angleD >= 90:
                curveIsNotRounded = True
                break
        else:
            curveIsNotRounded = False
        
        del cornerPts
        return curveIsNotRounded
    
    
    def cullClosePolylinePts(self, polyline, distance = 0.01):
        """
        culling polyline points which are closer than "closeDistance" to the last polyline point 
        """
        # get polyline pts:
        controlPts = list(polyline)
        
        newPolylinePts = []
        for i,pt in enumerate(controlPts):
            if i == 0:
                lastPt = pt
                newPolylinePts.append(lastPt)
            elif i > 0:
                if lastPt.DistanceTo(pt) > distance:
                    lastPt = pt
                    newPolylinePts.append(lastPt)
                else:
                    pass
        
        del controlPts
        newPolyline = Rhino.Geometry.Polyline(newPolylinePts)
        return newPolyline
    
    
    def createLegend(self, geometryL, values_uncorrected, legendBakePar, legendUnit=None, customCellNumbers=[]):
        """
        create a legend for the given "values"
        """
        # read the "legendBakePar_"
        gismo_preparation = Preparation()
        legendStyle, legendPlane, maxValue, minValue, customColors, numLegendCells, fontName, fontSize, numDecimals, customLegendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = gismo_preparation.read_legendBakePar(legendBakePar)
        
        # modify "values_uncorrected" accorind to "maxValue_" and "minValue_" inputs
        maxValue_modified = False
        minValue_modified = False
        maxValue_uncorrected = max(values_uncorrected)
        minValue_uncorrected = min(values_uncorrected)
        values = []
        for value in values_uncorrected:
            if (maxValue != None):
                if (maxValue < maxValue_uncorrected):  # check in case "maxValue_" is larger than the largest value in "values"
                    maxValue_modified = True
                    if value > maxValue:
                        value = maxValue
            if (minValue != None):
                if (minValue > minValue_uncorrected):  # check in case "minValue_" is smaller than the smallest value in "values"
                    minValue_modified = True
                    if value < minValue:
                        value = minValue
            values.append(value)
        
        if (len(customColors) == 0):
            customColors = gismo_preparation.defaultCustomColors()
        
        if (customLegendUnit == None) and (legendUnit == None):
            # nothing inputted into "legendUnit_" input of "Legend Bake Parameters" component. And no "legendUnit" has been supplied to this method
            legendUnit = "unknown unit"
        elif (customLegendUnit != None):
            # something inputted into "legendUnit_" input of "Legend Bake Parameter" component
            legendUnit = customLegendUnit
        
        if sum(values) == (len(values)*values[0]):
            # all items in "values" are the same: meaning all colors will be the same. Set the "numLegendCells" to 1
            numLegendCells = 1
        
        if (len(customCellNumbers) != 0):
            # if "customCellNumbers" list has been added as an input to this method, then limit the "numLegendCells" to the number of items in the "customCellNumbers" list
            numLegendCells = len(customCellNumbers)
            if (customLegendUnit == None):
                # nothing inputted into "legendUnit_" input of "Legend Bake Parameters" component.
                legendUnit = "~"
        
        
        # calculate bounding box properties from the "geometryL"
        bb_volume, bb_centroid, bb_length, bb_depth, bb_height, bb_bottomLeftCorner, bb_bottomRightCorner, bb_topRightCorner, bb_topLeftCorner = gismo_preparation.boundingBox_properties(geometryL, accurate=True)
        
        # cell size, text size
        legendCellWidth = bb_length/10 * scale
        legendCellHeight = legendCellWidth * 0.75
        if (fontSize == None):
            cellNumber_textSize = legendCellWidth/3.5
        else:
            # something inputted to "fontSize_"
            cellNumber_textSize = fontSize
        
        # cellNumbers, cellColors
        valuesMin = min(values)
        valuesMax = max(values)
        if numLegendCells == 1:
            # fix for "Attempted to divide by zero" error
            step = (valuesMax-valuesMin)/1
        else:
            step = (valuesMax-valuesMin)/(numLegendCells-1)
        cellNumbers = []
        for i in range(numLegendCells):
            cellNumber = valuesMin + i*step
            cellNumbers.append(cellNumber)
        
        cellColors = gismo_preparation.numberToColor(cellNumbers, customColors, minValue, maxValue)
        
        # create the bottom cell
        legendStartPt = Rhino.Geometry.Point3d(bb_bottomRightCorner)
        legendStartPlane = Rhino.Geometry.Plane(legendStartPt, Rhino.Geometry.Vector3d(0,0,1))
        
        bottomCellStartPt = Rhino.Geometry.Point3d(legendStartPt.X + (bb_depth * 0.1), legendStartPt.Y, legendStartPt.Z)
        bottomCellStartPlane = Rhino.Geometry.Plane(bottomCellStartPt, Rhino.Geometry.Vector3d(0,0,1))
        
        bottomCell = Rhino.Geometry.Rectangle3d(bottomCellStartPlane, legendCellWidth, legendCellHeight).ToNurbsCurve()
        if (legendStyle == 0):
            # rectangular cells
            degree = 3
        elif (legendStyle == 1) or (legendStyle == 2) or (legendStyle == 3):
            bottomCell.Domain = Rhino.Geometry.Interval(0,1)
            if (legendStyle == 1):
                # filleted cells
                tL = [0, 0.05, 0.20, 0.25, 0.35, 0.40, 0.5, 0.55, 0.7, 0.75, 0.85, 0.90, 1.0]
                degree = 3
            elif(legendStyle == 2):
                # elliptical cells
                tL = [0.125, 0.375, 0.625, 0.875, 0.125]
                degree = 3
                curveKnotStyle = Rhino.Geometry.CurveKnotStyle.UniformPeriodic
            elif(legendStyle == 3):
                # rhombus cells
                tL = [0.125, 0.375, 0.625, 0.875, 0.125]
            
            interpolateCrv_pts = []
            for t in tL:
                pt = bottomCell.PointAt(t)
                interpolateCrv_pts.append(pt)
            
            if(legendStyle == 2):
                bottomCell = Rhino.Geometry.Curve.CreateInterpolatedCurve(interpolateCrv_pts, degree, curveKnotStyle)
            elif(legendStyle == 3):
                bottomCell = Rhino.Geometry.Polyline(interpolateCrv_pts).ToNurbsCurve()
            else:
                bottomCell = Rhino.Geometry.Curve.CreateControlPointCurve(interpolateCrv_pts, degree)
        
        
        # create the legend
        myGismo_geometry = CreateGeometry()
        meshParam = Rhino.Geometry.MeshingParameters()
        meshParam.SimplePlanes = True
        legendCells_joinedMesh = Rhino.Geometry.Mesh()
        cellNumber_joinedMesh = Rhino.Geometry.Mesh()
        
        cellNumber_startPts = []
        for i in range(numLegendCells):
            transformMatrix = Rhino.Geometry.Transform.Translation(0,legendCellHeight,0)
            copied_bottomCell = bottomCell.Duplicate()
            moveSuccess = copied_bottomCell.Translate(0,i*legendCellHeight,0)
            
            # create the mesh cell
            copied_bottomCell_srf = Rhino.Geometry.Brep.CreatePlanarBreps([copied_bottomCell])[0]
            copied_bottomCell_mesh = Rhino.Geometry.Mesh.CreateFromBrep(copied_bottomCell_srf, meshParam)[0]
            legendCells_mesh_colors = [cellColors[i]] * copied_bottomCell_mesh.Vertices.Count
            copied_bottomCell_mesh_colored = myGismo_geometry.colorMeshVertices(copied_bottomCell_mesh, legendCells_mesh_colors)
            legendCells_joinedMesh.Append(copied_bottomCell_mesh_colored)
            
            # create the cell number start point
            cellNumber_startPt = Rhino.Geometry.Point3d(bottomCellStartPt.X + legendCellWidth*1.2, bottomCellStartPt.Y + i*legendCellHeight, bottomCellStartPt.Z)
            cellNumber_startPts.append(cellNumber_startPt)
            
            # create cellNumber_joinedMesh
            if (len(customCellNumbers) != 0):
                # the "customCellNumbers" input of this method has been defined
                cellNumber_string = customCellNumbers[i]
            else:
                # the "customCellNumbers" input of this method has NOT been defined
                cellNumber_string = cellNumbers[i]
                if (numDecimals == 0):
                    cellNumber_string = "%0.0f" % cellNumber_string
                elif (numDecimals == 1):
                    cellNumber_string = "%0.1f" % cellNumber_string
                elif (numDecimals == 2):
                    cellNumber_string = "%0.2f" % cellNumber_string
                elif (numDecimals == 3):
                    cellNumber_string = "%0.3f" % cellNumber_string
                elif (numDecimals == 4):
                    cellNumber_string = "%0.4f" % cellNumber_string
                elif (numDecimals == 5):
                    cellNumber_string = "%0.5f" % cellNumber_string
                elif (numDecimals == 6):
                    cellNumber_string = "%0.6f" % cellNumber_string
            
            # add "<" to the first legend cell number, and ">" to the last one, in case "minValue_" and "maxValue_" have been defined
            if (i == 0) and (minValue_modified == True):
                cellNumber_string = "≤ " + cellNumber_string
            elif (i == (numLegendCells-1)) and (maxValue_modified == True):
                cellNumber_string = "≥ " + cellNumber_string
            
            cellNumber_mesh = gismo_preparation.text2srfOrMesh("mesh", [cellNumber_string], cellNumber_startPt, cellNumber_textSize, fontName, bold=False, italic=False, justificationIndex=0)
            cellNumber_joinedMesh.Append(cellNumber_mesh)
        
        legendUnits_startPt = Rhino.Geometry.Point3d(cellNumber_startPts[-1].X, cellNumber_startPts[-1].Y + legendCellHeight, cellNumber_startPts[-1].Z)
        legendUnits_mesh = gismo_preparation.text2srfOrMesh("mesh", [legendUnit], legendUnits_startPt, cellNumber_textSize, fontName, bold=False, italic=False, justificationIndex=0)
        
        # join cells and text into a single mesh
        legend_allMeshes_joined = Rhino.Geometry.Mesh()
        legend_allMeshes_joined.Append(legendCells_joinedMesh)
        legend_allMeshes_joined.Append(cellNumber_joinedMesh)
        legend_allMeshes_joined.Append(legendUnits_mesh)
        
        
        # orient the whole legend in case "legendPlane_" has been defined
        if (legendPlane != None):
            transformMatrix = Rhino.Geometry.Transform.PlaneToPlane(legendStartPlane, legendPlane)
            transformSuccess = legend_allMeshes_joined.Transform(transformMatrix)
            return legend_allMeshes_joined, legendPlane
        else:
            return legend_allMeshes_joined, legendStartPlane
    
    
    def compassDirections(self, originPt, radius, scale, northVec, textSize=None):
        """
        create compass directions curves and labels for 30 degrees increment
        """
        # create circles
        myPreparation = Preparation()
        unitConversionFactor, unitSystem = myPreparation.checkUnits()
        
        circleRadius = scale * (radius/unitConversionFactor)  # 200 meters is fixed radius
        originPt_plane = Rhino.Geometry.Plane(originPt, Rhino.Geometry.Vector3d(0,1,0), Rhino.Geometry.Vector3d(1,0,0))
        
        # rotate originPt_plane for northVec
        angleR = Rhino.Geometry.Vector3d.VectorAngle( Rhino.Geometry.Vector3d(0,1,0), northVec, Rhino.Geometry.Plane(originPt, Rhino.Geometry.Vector3d(0,0,-1)) )
        rotateSuccess = originPt_plane.Rotate(angleR, Rhino.Geometry.Vector3d(0,0,-1))
        
        circle = Rhino.Geometry.Circle(originPt_plane, circleRadius).ToNurbsCurve()
        circle2 = Rhino.Geometry.Circle(originPt, 1.05*circleRadius).ToNurbsCurve()
        circle3 = Rhino.Geometry.Circle(originPt, 1.07*circleRadius).ToNurbsCurve()
        
        # divide circle
        numOfDiv = 12  # divide 360 by 30 degrees increments
        includeEnds = True
        divisionParameters = circle.DivideByCount(numOfDiv, includeEnds)
        
        divisionPts = []
        moveVectors = []  # vectors for moving the 0,30,60... labels
        justificationIndexL = []
        for t in divisionParameters:
            pt = circle.PointAt(t)
            divisionPts.append(pt)
            moveVec = pt - originPt
            moveVectors.append(moveVec)
            
            angleR2 = Rhino.Geometry.Vector3d.VectorAngle( Rhino.Geometry.Vector3d(0,1,0), moveVec, Rhino.Geometry.Plane(originPt, Rhino.Geometry.Vector3d(0,0,-1)) )
            # determine justificationIndex
            if (math.degrees(angleR2) == 0) or (math.degrees(angleR2) == 360):
                justificationIndex = 1
            elif (math.degrees(angleR2) > 0) and (math.degrees(angleR2) < 90):
                justificationIndex = 0
            elif (math.degrees(angleR2) == 90):
                justificationIndex = 3
            elif (math.degrees(angleR2) > 90) and (math.degrees(angleR2) < 180):
                justificationIndex = 6
            elif (math.degrees(angleR2) == 180):
                justificationIndex = 7
            elif (math.degrees(angleR2) > 180) and (math.degrees(angleR2) < 270):
                justificationIndex = 8
            elif (math.degrees(angleR2) == 270):
                justificationIndex = 5
            elif (math.degrees(angleR2) > 270) and (math.degrees(angleR2) < 360):
                justificationIndex = 2
            
            justificationIndexL.append(justificationIndex)
        
        # create lines, textLabels
        textL = ["N", 30, 60, "E", 120, 150, "S", 210, 240, "W", 300, 330]
        
        if (textSize == None):
            # no textSize defined
            textSizeL = [circleRadius/20, circleRadius/24, circleRadius/24, circleRadius/20, circleRadius/24, circleRadius/24, circleRadius/20, circleRadius/24, circleRadius/24, circleRadius/20, circleRadius/24, circleRadius/24]
        else:
            # textSize defined
            textSizeL = [textSize, textSize/1.2, textSize/1.2, textSize, textSize/1.2, textSize/1.2, textSize, textSize/1.2, textSize/1.2, textSize, textSize/1.2, textSize/1.2]
        
        fontName = "Verdana"
        bold = True
        italic = False
        
        lines = []
        textLabels = []
        for i,pt in enumerate(divisionPts):
            line = Rhino.Geometry.Line(pt, pt + 0.1*moveVectors[i]).ToNurbsCurve()
            lines.append(line)
            textLabel = myPreparation.text2srfOrMesh("mesh", [textL[i]], pt + 0.11*moveVectors[i], textSizeL[i], fontName, bold, italic, justificationIndexL[i])
            textLabels.append(textLabel)
        
        compassCrvs = [circle, circle2, circle3] + lines
        
        return divisionPts, compassCrvs, textLabels
    
    
    def liftingOSMshapes_from_groundTerrain(self, shapesL, groundBrep_singleBrepFace, height, minHeight=None, bottomCrvControlPt_highestZcoord=None):
        """
        projecting OSM shapes to groundTerrain_ and then lifting them to a plane for height or minHeight above the highest shape point
        """
        topCrvs = []
        tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        for shapeIndex, shape in enumerate(shapesL):
            if (groundBrep_singleBrepFace == None):
                projectionPlane = Rhino.Geometry.Plane(Rhino.Geometry.Point3d(0,0,shape.PointAtStart.Z), Rhino.Geometry.Vector3d(0,0,1))  # it always be constant because each shapesL has a constant height (coming from "OSM shapes" component)
                projectedShapeCrvs = [Rhino.Geometry.Curve.ProjectToPlane(shape, projectionPlane)]
            elif (groundBrep_singleBrepFace != None):
                projectionDirection = Rhino.Geometry.Vector3d(0,0,1)  # it can be projectionDirection = Rhino.Geometry.Vector3d(0,0,-1) as well, does not matter
                projectedShapeCrvs = Rhino.Geometry.Curve.ProjectToBrep(shape, groundBrep_singleBrepFace, projectionDirection, tol)
            
            if len(projectedShapeCrvs) == 0:  # the shape is located outside of the "groundTerrain_" ("if groundTerrain_" inputted. If "groundTerrain_" not inputted, len(projectedShapeCrvs) will never be equal to 0)
                topCrvPts = []
                #topCrvs = []  # its already defined at the start of this method, so an empty list will be returned
            elif len(projectedShapeCrvs) != 0:
                #joinedProjectedShapeCrvs = Rhino.Geometry.Curve.JoinCurves(projectedShapeCrvs, tol)
                if (not shape.IsClosed):
                    # shape is not closed (probably shapeType = 1), so there is no need to lift it, as it will not be extruded
                    topCrvs.extend(projectedShapeCrvs)
                    bottomCrvControlPt_highestZcoord = projectedShapeCrvs[0].PointAtStart.Z
                elif shape.IsClosed:
                    # shape is closed (shapeType = 0)
                    projectedShapeCrv = projectedShapeCrvs[0]  # always take the first curve from the list of shapes projected curves
                    if (not projectedShapeCrv.IsClosed):
                        # the projected shape is not a closed curve anymore (it was before the projection). This happens when shape intersects with the "groundTerrain_" bounding box
                        line = Rhino.Geometry.Line(projectedShapeCrv.PointAtStart, projectedShapeCrv.PointAtEnd).ToNurbsCurve()
                        joinedPolyCrv = Rhino.Geometry.Curve.JoinCurves([projectedShapeCrv,line], tol)[0]
                        bottomCrv = joinedPolyCrv.ToNurbsCurve()
                    else:
                        # the projected shape is still a closed curve (and it was before the projection)
                        bottomCrv = projectedShapeCrv.ToNurbsCurve()
                    
                    # find the highest Z coordinate of the shape edit points
                    bottomCrvControlPts = bottomCrv.GrevillePoints()
                    
                    if (bottomCrvControlPt_highestZcoord == None):  # it may != None for shapes which are included in other building shapes (like shapes which have valid "building:part" key)
                        if shapeIndex == 0:  # this is a fix in case the "shapesL" has more than one shape. If it does then their topCrv can be created to different Z coordinate, and therefor not being able to be capped together with other topCrv from the same "shapeL".
                            bottomCrvControlPt_highestZcoord = -10000  # dummy value
                            for bottomCrvControlPt in bottomCrvControlPts:
                                if bottomCrvControlPt.Z > bottomCrvControlPt_highestZcoord:
                                    bottomCrvControlPt_highestZcoord = bottomCrvControlPt.Z
                    
                    # move the shape edit points upwards for: bottomCrvControlPt_highestZcoord + minHeight/height, in order to create the topCrv
                    topCrvPts = []
                    for bottomCrvControlPt in bottomCrvControlPts:
                        if minHeight != "":
                            # there is a valid "min_height" key. Lift the projected points for this value
                            topCrvPt = Rhino.Geometry.Point3d(bottomCrvControlPt.X, bottomCrvControlPt.Y, bottomCrvControlPt_highestZcoord + height)
                        else:
                            # there is no valid "min_height" key. Lift the projected points for the "height" value
                            topCrvPt = Rhino.Geometry.Point3d(bottomCrvControlPt.X, bottomCrvControlPt.Y, bottomCrvControlPt_highestZcoord + height)
                        topCrvPts.append(topCrvPt)
                    topCrv = Rhino.Geometry.Polyline(topCrvPts).ToNurbsCurve()
                    topCrvs.append(topCrv)
        
        del shapesL
        del groundBrep_singleBrepFace
        del topCrvPts
        
        return topCrvs, bottomCrvControlPt_highestZcoord
    
    
    def projectPlanarClosedCrvsToTerrain(self, planarCrvsL, groundTerrainBrep, groundTerrain_outerEdge_extrusion):
        """
        project planar closed curves to a single face brep and make their footprints on terrain
        """
        # get unitConversionFactor
        gismo_preparation = Preparation()
        unitConversionFactor, unitSystemLabel = gismo_preparation.checkUnits()
        
        
        if (groundTerrainBrep == None):
            planarSrfs = Rhino.Geometry.Brep.CreatePlanarBreps(planarCrvsL)  # returns a list!
            
            validGroundTerrain = True
            printMsg = "ok"
            return planarSrfs, [], validGroundTerrain, printMsg
        
        elif (groundTerrainBrep != None):
            # extract Faces[0] from "groundTerrain_",
            # shrink the upper terrain brepface in case it is not shrinked (for example: the terrain surface inputted to _terrain input is not created by Gismo "Terrain Generator" component)
            groundTerrainBrepFaces = groundTerrainBrep.Faces
            groundTerrainBrepFaces.ShrinkFaces()
            duplicateMeshes = False
            groundBrep_singleBrepFace = groundTerrainBrepFaces[0].DuplicateFace(duplicateMeshes)
            
            tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
            # move _roadShapes above so that intersection with groundTerrain_ is fullfiled successfully
            #####liftingOSMshapesHeight = 8848/unitConversionFactor  # "8848" dummy value
            liftingOSMshapesHeight = 260/unitConversionFactor
            bb_height = 100/unitConversionFactor  # "100" dummy value
            moveMatrix = Rhino.Geometry.Transform.Translation(0,0,liftingOSMshapesHeight)
            for planarOffsetRoadsCrv in planarCrvsL:
                planarOffsetRoadsCrv.Transform(moveMatrix)
            
            extrudedShapeBrepL = []
            srfProjectedOnTerainL = []
            planarBreps = Rhino.Geometry.Brep.CreatePlanarBreps(planarCrvsL)
            for planarBrep in planarBreps:
                shapeStartPt = planarOffsetRoadsCrv.PointAtStart
                extrudePathCurve = Rhino.Geometry.Line(shapeStartPt, Rhino.Geometry.Point3d(shapeStartPt.X, shapeStartPt.Y, shapeStartPt.Z - (liftingOSMshapesHeight+(2 * bb_height)) )).ToNurbsCurve()
                cap = True
                extrudedShapeBrep = planarBrep.Faces[0].CreateExtrusion(extrudePathCurve, cap)
                extrudedShapeBrepL.append(extrudedShapeBrep)
                splittedBreps = Rhino.Geometry.Brep.Split(groundBrep_singleBrepFace, extrudedShapeBrep, tol)
                
                if len(splittedBreps) > 0:
                    # the planarOffsetRoadsCrv is inside of groundTerrain_ bounding box (a) or it interesect with it (b)
                    # determine which one of these two is the case
                    intersectionYes, intersectCrvs, intersectPts = Rhino.Geometry.Intersect.Intersection.BrepBrep(groundTerrain_outerEdge_extrusion, extrudedShapeBrep, tol)
                    if (len(intersectCrvs) > 0):
                        #print "terrain edges intersect with road srf"
                        # planarOffsetRoadsCrv planar srf intersects with groundTerrrain_
                        
                        # check the planarOffsetRoadsCrv oriention to determine the brep face index in "splittedBreps"
                        upDirection = Rhino.Geometry.Vector3d(0,0,1)
                        srfProjectedOnTerrain = splittedBreps[len(splittedBreps)-1]  # works!
                        #srfProjectedOnTerrain = splittedBreps[0]
                        #print "len(splittedBreps): ", len(splittedBreps)
                        
                        gotPlane_success, plane = planarOffsetRoadsCrv.TryGetPlane()
                        
                        if (planarOffsetRoadsCrv.ClosedCurveOrientation(upDirection) == Rhino.Geometry.CurveOrientation.Clockwise):
                            srfProjectedOnTerrain = splittedBreps[len(splittedBreps)-1]  # works?
                            #srfProjectedOnTerrain = splittedBreps[0]
                            ####print "clockwise"
                            pass
                        elif (planarOffsetRoadsCrv.ClosedCurveOrientation(upDirection) == Rhino.Geometry.CurveOrientation.CounterClockwise):
                            srfProjectedOnTerrain = splittedBreps[0]
                            ####print "counter clockwise"
                            pass
                        
                        
                        srfProjectedOnTerrain.Faces.ShrinkFaces()  # shrink the cutted srfProjectedOnTerrain
                        srfProjectedOnTerainL.append(srfProjectedOnTerrain)
                        
                    elif (len(intersectCrvs) == 0):
                        ####print "terrain edges DO NOT intersect with road srf."
                        # planarOffsetRoadsCrv planar srf is inside groundTerrain_ and does not intersect it
                        srfProjectedOnTerrain = splittedBreps[len(splittedBreps)-1]
                        srfProjectedOnTerrain.Faces.ShrinkFaces()  # shrink the cutted srfProjectedOnTerrain
                        srfProjectedOnTerainL.append(srfProjectedOnTerrain)
                
                else:
                    # planarOffsetRoadsCrv is outside of groundTerrain_ bounding box, do not add it to the "srfProjectedOnTerainL" list
                    pass
                
                del planarBrep; del extrudePathCurve; del splittedBreps; del extrudedShapeBrepL; extrudedShapeBrepL = []
            
            
            # create a single mesh from all surfaces in the "" list
            if (len(srfProjectedOnTerainL) == 0):
                # the "groundTerrain_" is either too small (has very small radius) or it does not have the same origin as "_roadShapes", meaning the "_roadShapes" can not be projected to "groundBrep_singleBrepFace".
                validGroundTerrain = False
                printMsg = "Something is wrong with your \"groundTerrain_\" input.\n" + \
                           "Make sure that when you look at it in Rhino's \"Top\" view, it covers (encapsulates) the whole \"_roadShapes\" geometry or at least some of its parts."
                
                return srfProjectedOnTerainL, extrudedShapeBrepL, validGroundTerrain, printMsg
            elif (len(srfProjectedOnTerainL) > 0):
                # everything is fine
                validGroundTerrain = True
                printMsg = "ok"
                
                return srfProjectedOnTerainL, extrudedShapeBrepL, validGroundTerrain, printMsg
    
    
    def createRenderMesh(self, mesh, u):
        """
        create render mesh and its texture image (material diffuse map file).
        the code of this method is entirely based on VB.NET components by Vicente Soler:
        http://www.grasshopper3d.com/xn/detail/2985220:Comment:663243
        """
        mesh.Unweld(0, False)
        
        dt = []
        c = mesh.Faces.Count
        for i in range(c - 1+1):
            sub_dt = []
            f = mesh.Faces[i]
            color1 = mesh.VertexColors[f.A]
            color2 = mesh.VertexColors[f.B]
            color3 = mesh.VertexColors[f.C]
            color4 = mesh.VertexColors[f.D]
            sub_dt.append(System.Drawing.Color.FromArgb(color1.R, color1.G, color1.B))
            sub_dt.append(System.Drawing.Color.FromArgb(color2.R, color2.G, color2.B))
            sub_dt.append(System.Drawing.Color.FromArgb(color3.R, color3.G, color3.B))
            sub_dt.append(System.Drawing.Color.FromArgb(color4.R, color4.G, color4.B))
            dt.append(sub_dt)
        
        mesh.TextureCoordinates.Clear()
        for i in range(mesh.Vertices.Count):
            mesh.TextureCoordinates.Add(0,0)
        
        size = math.ceil(math.sqrt(c))
        count = -1
        
        for x in xrange(size - 1+1):
            for y in xrange(size - 1+1):
                count += 1
                if count < c - 1+1:
                    f = mesh.Faces[count]
                    sb = size * 2
                    mesh.TextureCoordinates[f.A] = Rhino.Geometry.Point2f((x * 2 + 0.5) / sb, (y * 2 + 0.5) / sb)
                    mesh.TextureCoordinates[f.B] = Rhino.Geometry.Point2f((x * 2 + 1.5) / sb, (y * 2 + 0.5) / sb)
                    mesh.TextureCoordinates[f.C] = Rhino.Geometry.Point2f((x * 2 + 1.5) / sb, (y * 2 + 1.5) / sb)
                    mesh.TextureCoordinates[f.D] = Rhino.Geometry.Point2f((x * 2 + 0.5) / sb, (y * 2 + 1.5) / sb)
        
        
        dt_length = len(dt)
        size = math.ceil(math.sqrt(dt_length))
        sb = size * 2 - 1
        bm = System.Drawing.Bitmap(size * 2, size * 2)
        bmb = System.Drawing.Bitmap(size * 4, size * 4)
        count = -1
        
        for x in xrange(size - 1+1):
            for y in xrange(size - 1+1):
                count += 1
                if count < dt_length - 1+1:
                    bm.SetPixel(x * 2 + 0, sb - (y * 2 + 0), dt[count][0])
                    bm.SetPixel(x * 2 + 1, sb - (y * 2 + 0), dt[count][1])
                    bm.SetPixel(x * 2 + 1, sb - (y * 2 + 1), dt[count][2])
                    bm.SetPixel(x * 2 + 0, sb - (y * 2 + 1), dt[count][3])
        
        g = System.Drawing.Graphics.FromImage(bmb)
        g.InterpolationMode = System.Drawing.Drawing2D.InterpolationMode.NearestNeighbor
        g.DrawImage(bm, 0, 0, size * 4 + 1, size * 4 + 1)
        bmb.Save(u)
        del dt
        
        return mesh


class EnvironmentalAnalysis():
    """
    various environmental analysis methods
    """
    def noLeavesPeriod(self, criteria, latitude, sunWindowQuadrantIndex, leaflessStartHOY=None, leaflessEndHOY=None):
        """
        calculate season(seasonIndex) of the sunWindow Quadrant
        """
        if criteria == "perQuadrant":
            if latitude > 0:  # northern hemisphere
                if sunWindowQuadrantIndex < 72:
                    seasonIndex = 0  # winter/autumn
                elif sunWindowQuadrantIndex >= 72:
                    seasonIndex = 1  # spring/summer
            elif latitude < 0:  # southern hemisphere
                if sunWindowQuadrantIndex < 72:
                    seasonIndex = 1  # spring/summer
                elif sunWindowQuadrantIndex >= 72:
                    seasonIndex = 0  # winter/autumn
        elif criteria == "perHoy":
            if leaflessStartHOY < leaflessEndHOY:
                if (sunWindowQuadrantIndex >= leaflessStartHOY) and (sunWindowQuadrantIndex <= leaflessEndHOY):
                    seasonIndex = 0  # leafless period
                else:
                    seasonIndex = 1  # inleaf period
            elif leaflessStartHOY > leaflessEndHOY:
                if (sunWindowQuadrantIndex >= leaflessStartHOY) or (sunWindowQuadrantIndex <= leaflessEndHOY):
                    seasonIndex = 0  # leafless period
                else:
                    seasonIndex = 1  # inleaf period
        
        return seasonIndex
    
    
    def calculateSkyExposureFactor(self, testPt, contextMeshes, latitude, radius, precision, treesTransmissionIndices=[0,[0,0]], leaflessStartHOY=None, leaflessEndHOY=None):
        """
        calculate sky exposure factor
        """
        # lifting up the testPt due to MeshRay intersection
        tol = Rhino.RhinoDoc.ActiveDoc.ModelAbsoluteTolerance
        testPtLifted = Rhino.Geometry.Point3d(testPt.X, testPt.Y, testPt.Z+tol)
        gismo_geometry = CreateGeometry()
        
        precisionU = precision*5
        precisionV = int(precisionU/3.5)
        
        skyDomeHalfSphere = Rhino.Geometry.Sphere(Rhino.Geometry.Plane(Rhino.Geometry.Point3d(testPtLifted),Rhino.Geometry.Vector3d(0,0,1)), radius)
        splittedSkyDomeDomainUmin, splittedSkyDomeDomainUmax = [0, 2*math.pi]  # sphere diameter
        splittedSkyDomeDomainVmin, splittedSkyDomeDomainVmax = [0, 0.5*math.pi]  # sphere vertical arc
        splittedSkyDomeDomainVmax = 0.995*splittedSkyDomeDomainVmax
        
        stepU = (splittedSkyDomeDomainUmax - splittedSkyDomeDomainUmin)/precisionU
        stepV = (splittedSkyDomeDomainVmax - splittedSkyDomeDomainVmin)/precisionV
        
        skyDomePts = []
        for i in xrange(0,precisionU):
            for k in xrange(0,precisionV):
                u = splittedSkyDomeDomainUmin + stepU*i
                v = splittedSkyDomeDomainVmin + stepV*k
                skyDomePt = skyDomeHalfSphere.PointAt(u,v)
                skyDomePts.append(skyDomePt)
        skyDomeMeshPts = skyDomePts + skyDomePts[:precisionV]  # increases precisionU for 1
        skyDomeMesh = gismo_geometry.meshFromPoints(precisionU+1, precisionV, skyDomeMeshPts)
        meshFacesCentroids = [skyDomeMesh.Faces.GetFaceCenter(i) for i in xrange(skyDomeMesh.Faces.Count)]
        meshFaces = skyDomeMesh.Faces
        meshVertices = skyDomeMesh.Vertices
        
        meshFaceAreas = gismo_geometry.calculateMeshFaceAreas(skyDomeMesh)
        skyDomeMeshArea = sum(meshFaceAreas)
        skyDomeMeshArea2 = Rhino.Geometry.AreaMassProperties.Compute(skyDomeMesh).Area
        #print "skyDomeMeshArea: ", skyDomeMeshArea
        #print "skyDomeMeshArea2: ", skyDomeMeshArea2
        
        del skyDomeMeshPts
        del meshVertices
        del meshFaces
        del skyDomeMesh
        leaflessStartHOYdummy = 0; leaflessEndHOYdummy = 1
        skyExposureFactor = 0  # 0 equals to 100% shading, 1 equals to 0% shading
        for i,centroid in enumerate(meshFacesCentroids):
            raysIntensityWithoutTransmissionIndex = meshFaceAreas[i]/skyDomeMeshArea
            vector = Rhino.Geometry.Vector3d(centroid)-Rhino.Geometry.Vector3d(testPtLifted)
            ray = Rhino.Geometry.Ray3d(testPtLifted, vector)
            for meshIndex,mesh in enumerate(contextMeshes):
                intersectParam = Rhino.Geometry.Intersect.Intersection.MeshRay(mesh,ray)
                # ray hitted something
                if intersectParam >= 0:
                    seasonIndexDummy = self.noLeavesPeriod("perHoy", latitude, i, leaflessStartHOYdummy, leaflessEndHOYdummy)
                    if meshIndex == 0:  # context mesh hitted
                        treesTransmissionIndex = 0
                    elif meshIndex == 1:  # coniferousTrees mesh hitted
                        treesTransmissionIndex = treesTransmissionIndices[0]
                    elif meshIndex == 2:  # deciduousTrees mesh hitted
                        treesTransmissionIndex = treesTransmissionIndices[1][seasonIndexDummy]
                    skyExposureFactor += raysIntensityWithoutTransmissionIndex*treesTransmissionIndex
                    break
            # no hitting, the ray only hits the sky dome
            else:
                treesTransmissionIndex = 1
                skyExposureFactor += raysIntensityWithoutTransmissionIndex * treesTransmissionIndex
        
        del meshFacesCentroids
        
        return skyExposureFactor


class GIS():
    """
    methods for manipulation of GIS data
    """
    def calculate_CRS_UTMzone(self, locationLatitudeD, locationLongitudeD):
        """
        calculate CRS UTMzone code based on location's latitude-longitude
        """
        # by http://stackoverflow.com/a/9188972/3137724 (link given by Even Rouault)
        CRS_UTMzone = (math.floor((locationLongitudeD + 180)/6) % 60) + 1
        if locationLatitudeD >= 0:
            # for northern hemisphere
            northOrsouth = "north"
            CRS_EPSG_code = 32600 + CRS_UTMzone
        elif locationLatitudeD < 0:
            # for southern hemisphere
            northOrsouth = "south"
            CRS_EPSG_code = 32700 + CRS_UTMzone
        
        return CRS_EPSG_code, int(CRS_UTMzone), northOrsouth
    
    
    def UTM_CRS_from_latitude(self, locationLatitudeD, locationLongitudeD, originLatitudeD = 0, originLongitudeD = 0):
        """
        create UTM CRS from latitude, longitude and anchor latitude, anchor longitude
        """
        CRS = MapWinGIS.GeoProjectionClass()
        CRS_EPSG_code, CRS_UTMzone, northOrsouth = self.calculate_CRS_UTMzone(locationLatitudeD, locationLongitudeD)
        proj4_string = "+proj=utm +zone=%s +%s +datum=WGS84 +ellps=WGS84 +lat_0=%s +lon_0=%s" % (CRS_UTMzone, northOrsouth, originLatitudeD, originLongitudeD)#, resamplingMethod)
        CRS.ImportFromProj4(proj4_string)
        
        return CRS
    
    
    def CRS_from_EPSGcode(self, EPSGcode):
        """
        create CRS from EPSG code
        """
        CRS = MapWinGIS.GeoProjectionClass()
        CRS.ImportFromEPSG(EPSGcode)
        
        return CRS
    
    
    def convertBetweenTwoCRS(self, inputCRS, outputCRS, firstCoordinate, secondCoordinate):
        """
        convert coordinates from one CRS to another
        """
        successStartTransform = inputCRS.StartTransform(outputCRS)
        
        secondCoordinate_ref = clr.StrongBox[System.Double](secondCoordinate)
        firstCoordinate_ref = clr.StrongBox[System.Double](firstCoordinate)
        successTransform = MapWinGIS.GeoProjectionClass.Transform(inputCRS, firstCoordinate_ref, secondCoordinate_ref)
        
        inputCRS.StopTransform()
        
        originPtProjected = Rhino.Geometry.Point3d(firstCoordinate_ref.Value, secondCoordinate_ref.Value, 0)
        
        return originPtProjected
    
    
    def projectedLocationCoordinates(self, locationLatitudeD, locationLongitudeD):
        """
        convert latitude,longitude coordinates to x,y projected coordinates
        """
        outputCRS_EPSG_code, CRS_UTMzone, northOrsouth = self.calculate_CRS_UTMzone(locationLatitudeD, locationLongitudeD)
        
        # set the CRS to WGS 84
        inputCRS = MapWinGIS.GeoProjectionClass()
        inputCRS_EPSG_code = 4326  # WGS 84
        inputCRS.ImportFromEPSG(inputCRS_EPSG_code)
        
        # set the output CRS
        outputCRS = MapWinGIS.GeoProjectionClass()
        outputCRS.ImportFromEPSG(outputCRS_EPSG_code)
        
        successStartTransform = inputCRS.StartTransform(outputCRS)
        
        locationLatitudeD_ref = clr.StrongBox[System.Double](locationLatitudeD)
        locationLongitudeD_ref = clr.StrongBox[System.Double](locationLongitudeD)
        successTransform = MapWinGIS.GeoProjectionClass.Transform(inputCRS, locationLongitudeD_ref, locationLatitudeD_ref)
        
        inputCRS.StopTransform()
        
        originPtProjected = Rhino.Geometry.Point3d(locationLongitudeD_ref.Value, locationLatitudeD_ref.Value, 0)
        
        return originPtProjected
    
    
    def projectedLocationCoordinates2(locationLatitudeD, locationLongitudeD, unitConversionFactor):
        """
        convert latitude,longitude coordinates to x,y projected coordinates2
        this method should be replaced with upper "projectedLocationCoordinates" but only for 4.9.4? > versions of MapWinGIS,
        due to lack of MapWinGIS.GeoProjectionClass.Transform method in those MapWinGIS methods
        """
        outputCRS_EPSG_code, CRS_UTMzone, northOrsouth = self.calculate_CRS_UTMzone(locationLatitudeD, locationLongitudeD)
        
        # create a dummy point with locationLatitudeD, locationLongitudeD coordinates
        dummyShape = MapWinGIS.ShapeClass()
        dummyShape.ShapeType = MapWinGIS.ShpfileType.SHP_POINT
        dummyShape.AddPoint(locationLongitudeD, locationLatitudeD)
        
        # insert a dummy point to the dummyShapefile
        dummyShapefile = MapWinGIS.ShapefileClass()
        openShapefileSuccess2 = MapWinGIS.ShapefileClass.CreateNew(dummyShapefile, "", MapWinGIS.ShpfileType.SHP_POINT)
        shapeIndex2 = clr.StrongBox[System.Int32]()
        success = dummyShapefile.EditInsertShape(dummyShape, shapeIndex2)
        
        # a single field needs to be defined due to inserting of "dummyShape"
        fieldName = "5"  # dummy name
        fieldType = MapWinGIS.FieldType.INTEGER_FIELD
        fieldPrecision = 1
        fieldWidth = 1
        success2 = dummyShapefile.EditAddField(fieldName, fieldType, fieldPrecision, fieldWidth)
        
        # set the CRS of dummyShapefile to WGS 84
        inputCRS = MapWinGIS.GeoProjectionClass()
        inputCRS_EPSG_code = 4326  # WGS 84
        inputCRS.ImportFromEPSG(inputCRS_EPSG_code)
        dummyShapefile.GeoProjection = inputCRS
        
        shapeFileFolderPath = "C:\\gismo\\shapefile_example2"
        if not os.path.exists(shapeFileFolderPath):
            os.makedirs(shapeFileFolderPath)
        shapefileFilePath = shapeFileFolderPath + "\\dummyShapefile_%s.shp" % str(time.time())
        success = MapWinGIS.ShapefileClass.SaveAs(dummyShapefile, shapefileFilePath, None)
        dummyShapefile.Close()
        
        # dummyShapefile2 = dummyShapefile
        dummyShapefile2 = MapWinGIS.ShapefileClass()
        openShapefileSuccess = MapWinGIS.ShapefileClass.Open(dummyShapefile2, shapefileFilePath, None)
        
        # reproject the dummyShapefile2
        outputCRS2 = MapWinGIS.GeoProjectionClass()
        outputCRS2.ImportFromEPSG(outputCRS_EPSG_code)
        numOfsuccessfullyReprojectedShapes = clr.StrongBox[System.Int32]()
        reprojectedShapefile = MapWinGIS.ShapefileClass.Reproject(dummyShapefile2, outputCRS2, numOfsuccessfullyReprojectedShapes)
        if reprojectedShapefile == None:
            reprojectErrorMsg2 = dummyShapefile2.ErrorMsg(dummyShapefile2.LastErrorCode)
            print "reprojectErrorMsg2: ", reprojectErrorMsg2
        dummyShapefile2.Close()
        
        # delete the dummyShapefile_timetime().shp files and whole its folder
        try:
            shutil.rmtree(shapeFileFolderPath)
        except:
            pass
        
        for i in range(reprojectedShapefile.NumShapes):
            shape = reprojectedShapefile.Shape[i]
            for k in range(shape.numPoints):
                pt = shape.Point[k]
                longitudeProjectedMeters = pt.x
                latitudeProjectedMeters = pt.y
                originPtProjected = Rhino.Geometry.Point3d(longitudeProjectedMeters/unitConversionFactor, latitudeProjectedMeters/unitConversionFactor, 0)  # in Rhino document units
         
        return originPtProjected
    
    
    def XYtoLocation(self, pt_req, anchorLocation, anchorOriginPt=rg.Point3d(0,0,0)):
        """calculate latitude and longitude coordinates of the 'pt_req' in Rhino scene.
        output: 'pt_req' converted to latitude, longitude degrees"""
        
        
        # extract latitude, longitude from input 'anchorLocation'
        gismo_prep = Preparation()
        
        locationName, anchor_locationLatitudeD, anchor_locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_prep.checkLocationData(anchorLocation)
        
        unitConversionFactor, unitSystemLabel = gismo_prep.checkUnits()
        anchorOriginPt_meters = rg.Point3d(anchorOriginPt.X*unitConversionFactor, anchorOriginPt.Y*unitConversionFactor, anchorOriginPt.Z*unitConversionFactor)
        pt_req_meters = rg.Point3d(pt_req.X*unitConversionFactor, pt_req.Y*unitConversionFactor, pt_req.Z*unitConversionFactor)
        
        
        
        # inputCRS
        EPSGcode = 4326  # WGS 84
        inputCRS_dummy = self.CRS_from_EPSGcode(EPSGcode)
        # outputCRS
        outputCRS_dummy = self.UTM_CRS_from_latitude(anchor_locationLatitudeD, anchor_locationLongitudeD)
        
        anchor_originProjected_meters = self.convertBetweenTwoCRS(inputCRS_dummy, outputCRS_dummy, anchor_locationLongitudeD, anchor_locationLatitudeD)  # in meters
        
        
        
        
        # inputCRS
        # based on assumption that both anchorLocation_ input and required_location belong to the same UTM zone
        inputCRS = self.UTM_CRS_from_latitude(anchor_locationLatitudeD, anchor_locationLongitudeD, anchor_locationLatitudeD, anchor_locationLongitudeD)
        
        # outputCRS
        EPSGcode = 4326
        outputCRS = self.CRS_from_EPSGcode(EPSGcode)
        
        
        latitudeLongitudePt = self.convertBetweenTwoCRS(inputCRS, outputCRS, (anchor_originProjected_meters.X - anchorOriginPt_meters.X) + pt_req_meters.X, (anchor_originProjected_meters.Y - anchorOriginPt_meters.Y) + pt_req_meters.Y)
        latitude = latitudeLongitudePt.Y
        longitude = latitudeLongitudePt.X
        
        return latitude, longitude
    
    
    def destinationLatLon(self, latitude1D, longitude1D, radiusM):
        """
        calculate latitude-location for cardinal directions around the central latitude1D, longitude1D, for a given geodesic distance (radiusM). By Vincenty solution
        """
        # for WGS84:
        a = 6378137  # equatorial radius, meters
        b = 6356752.314245  # polar radius, meters
        f = 0.00335281066474  # flattening (ellipticity, oblateness) parameter = (a-b)/a, dimensionless
        
        bearingAnglesR = [math.radians(0), math.radians(180), math.radians(270), math.radians(90)]  # top, bottom, left, right
        latitudeLongitudeRegion = []
        for bearingAngle1R in bearingAnglesR:
            latitude1R = math.radians(latitude1D)
            longitude1R = math.radians(longitude1D)
            sinbearingAngle1R = math.sin(bearingAngle1R)
            cosbearingAngle1R = math.cos(bearingAngle1R)
            tanU1 = (1 - f) * math.tan(latitude1R)
            cosU1 = 1 / math.sqrt(1 + tanU1 * tanU1)
            sinU1 = tanU1 * cosU1
            sigma1 = math.atan2(tanU1, cosbearingAngle1R)
            sinBearingAngle1R = cosU1 * sinbearingAngle1R
            cosSqBearingAngle1R = 1 - (sinBearingAngle1R * sinBearingAngle1R)
            uSq = cosSqBearingAngle1R * (a * a - (b * b)) / (b * b)
            A = 1 + uSq / 16384 * (4096 + uSq * (-768 + uSq * (320 - (175 * uSq))))
            B = uSq / 1024 * (256 + uSq * (-128 + uSq * (74 - (47 * uSq))))
            sigma = radiusM / (b * A)  # radiusM in meters
            sigma_ = 0
            while abs(sigma - sigma_) > 1e-12:
                cos2sigmaM = math.cos(2 * sigma1 + sigma)
                sinsigma = math.sin(sigma)
                cossigma = math.cos(sigma)
                deltaSigma = B * sinsigma * (cos2sigmaM + B / 4 * (cossigma * (-1 + 2 * cos2sigmaM * cos2sigmaM) - (B / 6 * cos2sigmaM * (-3 + 4 * sinsigma * sinsigma) * (-3 + 4 * cos2sigmaM * cos2sigmaM))))
                sigma_ = sigma
                sigma = radiusM / (b * A) + deltaSigma
            
            tmp = sinU1 * sinsigma - (cosU1 * cossigma * cosbearingAngle1R)
            latitude2R = math.atan2(sinU1 * cossigma + cosU1 * sinsigma * cosbearingAngle1R, (1 - f) * math.sqrt(sinBearingAngle1R * sinBearingAngle1R + tmp * tmp))
            longitudeR = math.atan2(sinsigma * sinbearingAngle1R, cosU1 * cossigma - (sinU1 * sinsigma * cosbearingAngle1R))
            C = f / 16 * cosSqBearingAngle1R * (4 + f * (4 - (3 * cosSqBearingAngle1R)))
            L = longitudeR - ((1 - C) * f * sinBearingAngle1R * (sigma + C * sinsigma * (cos2sigmaM + C * cossigma * (-1 + 2 * cos2sigmaM * cos2sigmaM))))
            longitude2R = (longitude1R + L + 3 * math.pi) % (2 * math.pi) - math.pi  # normalise to -180...+180
            bearingAngle2R = math.atan2(sinBearingAngle1R, -tmp)
            
            latitude2D = math.degrees(latitude2R)
            longitude2D = math.degrees(longitude2R)
            bearingAngle2D = math.degrees(bearingAngle2R)
            if bearingAngle2D < 0:
                bearingAngle2D = 360-abs(bearingAngle2D)
            
            latitudeLongitudeRegion.append(latitude2D)
            latitudeLongitudeRegion.append(longitude2D)
        
        # latitude positive towards north, longitude positive towards east
        latitudeTopD, longitudeTopD, latitudeBottomD, longitudeBottomD, latitudeLeftD, longitudeLeftD, latitudeRightD, longitudeRightD = latitudeLongitudeRegion
        
        return latitudeTopD, longitudeTopD, latitudeBottomD, longitudeBottomD, latitudeLeftD, longitudeLeftD, latitudeRightD, longitudeRightD
    
    
    def distanceBetweenTwoPoints(self, latitude1D, longitude1D, latitude2D, longitude2D):
        """
        calculate geodesic distance between two locations (given through latitude-location coordinates). By Vincenty solution
        """
        """
        if latitude1D >= 0:
            # northern hemishere:
            latitude2D = 60
        elif latitude1D < 0:
            # southern hemishere:
            latitude2D = -56
        longitude2D = longitude1D
        """
        
        # for WGS84:
        a = 6378137  # equatorial radius, meters
        b = 6356752.314245  # polar radius, meters
        f = 0.00335281066474  # flattening (ellipticity, oblateness) parameter = (a-b)/a, dimensionless
        
        latitude1R = math.radians(latitude1D)
        latitude2R = math.radians(latitude2D)
        longitude1R = math.radians(longitude1D)
        longitude2R = math.radians(longitude2D)
        
        L = longitude2R - longitude1R
        tanU1 = (1-f) * math.tan(latitude1R)
        cosU1 = 1 / math.sqrt((1 + tanU1*tanU1))
        sinU1 = tanU1 * cosU1
        tanU2 = (1-f) * math.tan(latitude2R)
        cosU2 = 1 / math.sqrt((1 + tanU2*tanU2))
        sinU2 = tanU2 * cosU2
        longitudeR = L
        longitudeR_ = 0
        
        for i in range(100):
            sinLongitudeR = math.sin(longitudeR)
            cosLongitudeR = math.cos(longitudeR)
            sinSqSigma = (cosU2*sinLongitudeR) * (cosU2*sinLongitudeR) + (cosU1*sinU2-sinU1*cosU2*cosLongitudeR) * (cosU1*sinU2-sinU1*cosU2*cosLongitudeR)
            sinSigma = math.sqrt(sinSqSigma)
            cosSigma = sinU1*sinU2 + cosU1*cosU2*cosLongitudeR
            sigma = math.atan2(sinSigma, cosSigma)
            sinBearingAngleR = cosU1 * cosU2 * sinLongitudeR / sinSigma
            cosSqBearingAngleR = 1 - sinBearingAngleR*sinBearingAngleR
            if cosSqBearingAngleR == 0:
                # if distanceM is measured along the equator line (latitude1D = latitude2D = 0, longitude1D != longitude2D != 0)
                cos2SigmaM = 0
            else:
                cos2SigmaM = cosSigma - 2*sinU1*sinU2/cosSqBearingAngleR
            C = f/16*cosSqBearingAngleR*(4+f*(4-3*cosSqBearingAngleR))
            longitudeR_ = longitudeR
            longitudeR = L + (1-C) * f * sinBearingAngleR * (sigma + C*sinSigma*(cos2SigmaM+C*cosSigma*(-1+2*cos2SigmaM*cos2SigmaM)))
        
        uSq = cosSqBearingAngleR * (a*a - b*b) / (b*b)
        A = 1 + uSq/16384*(4096+uSq*(-768+uSq*(320-175*uSq)))
        B = uSq/1024 * (256+uSq*(-128+uSq*(74-47*uSq)))
        deltaSigma = B*sinSigma*(cos2SigmaM+B/4*(cosSigma*(-1+2*cos2SigmaM*cos2SigmaM) - B/6*cos2SigmaM*(-3+4*sinSigma*sinSigma)*(-3+4*cos2SigmaM*cos2SigmaM)))
        
        distanceM = b*A*(sigma-deltaSigma)  # in meters
        
        bearingAngleForwardR = math.atan2(cosU2*sinLongitudeR,  cosU1*sinU2-sinU1*cosU2*cosLongitudeR)
        bearingAngleReverseR = math.atan2(cosU1*sinLongitudeR, -sinU1*cosU2+cosU1*sinU2*cosLongitudeR)
        
        bearingAngleForwardD = math.degrees(bearingAngleForwardR)
        bearingAngleReverseD = math.degrees(bearingAngleReverseR)
        
        return distanceM
    
    
    def constructLocationFromShapefileMidExtent(self, shpFilePath):
        """
        get mid extent coordinate from shapefile
        """
        # open shapefile to get its extends
        utils = MapWinGIS.UtilsClass()
        shapefile = MapWinGIS.ShapefileClass()
        openShapefileSuccess = MapWinGIS.ShapefileClass.Open(shapefile, shpFilePath, None)
        if (not shapefile) or (not openShapefileSuccess):
            
            printMsg = "Shapefile reading failed. Check: \n" +\
                       "1) If '_shpFile' file path is correct. If it is: \n" +\
                       "2) In the same folder where the .shp file is, check if there are .shx,.dbf,.prj files with the same file name. These two files are essential, in order to open the .shx file.\n" +\
                       "3) If both upper two checks are fine: post a question about this issue on Gismo forum (grasshopper3d.com/group/gismo) with .shp and its files attached, and a screenshot of the message coming from 'readMe!' output."
            
            print "shapefile.ErrorMsg: ", shapefile.ErrorMsg
            
            utils = MapWinGIS.UtilsClass()
            convertErrorNo = MapWinGIS.GlobalSettingsClass().GdalLastErrorNo
            convertErrorMsg = MapWinGIS.GlobalSettingsClass().GdalLastErrorMsg
            convertErrorType = MapWinGIS.GlobalSettingsClass().GdalLastErrorType
            reprojectErrorMsg = MapWinGIS.GlobalSettingsClass().GdalReprojectionErrorMsg
            print "convertErrorNo: ", convertErrorNo
            print "convertErrorMsg: ", convertErrorMsg
            print "convertErrorType: ", convertErrorType
            print "reprojectErrorMsg: ", reprojectErrorMsg
            print "utils.ErrorMsg: ", utils.ErrorMsg
            print "utils.LastErrorCode: ", utils.LastErrorCode
            
            return None, printMsg
        
        elif openShapefileSuccess:
            # check1
            # if CRS information has been imported as well (this happens when .prj file in the same folder where .shp is missing)
            proj4_str = shapefile.Projection
            
            if (len(proj4_str) == 0):
                printMsg = "'SHP to location' component failed to extract the middle location from a shapefile (.shp).\nThis happens when .prj file does not exist in the same folder as .shp file, or .prj file is defective.\nUse the 'Gismo_Construct Location' component instead."
                return None, printMsg
            
            
            # check2
            # if shapefile .prj is geographic CRS (because we need to create a location at the end of this method, and Gismo's locations are always in geographic coordinates)
            if "+proj=longlat" not in proj4_str:  # geographic coordinate CRS have '+proj=longlat' in proj4_str
                printMsg = "'SHP to location' component can only extract the middle location from a shapefile (.shp) which has geographic coordinate system.\nThis is not the case with the current shapefile.\nUse the 'Gismo_Construct Location' component instead."
                return None, printMsg
            
            
            
            extents = shapefile.Extents
            
            x_dom = Rhino.Geometry.Interval(extents.xMin, extents.xMax)  # latitude degrees or meters, depending on shapefile CRS
            y_dom = Rhino.Geometry.Interval(extents.yMin, extents.yMax)  # longitude degrees or meters, depending on shapefile CRS
            y_dom = Rhino.Geometry.Interval(extents.yMin, extents.yMax)  # longitude degrees or meters, depending on shapefile CRS
            z_dom = Rhino.Geometry.Interval(extents.zMin, extents.zMax)  # longitude degrees or meters, depending on shapefile CRS
            #midLocaction = Rhino.Geometry.Point3d(y_dom.Mid, x_dom.Mid, z_dom.Mid)
            
            # locationName
            shpFolder, shpFileName = os.path.split(shpFilePath)
            shpFileName = shpFileName.replace(".shp", "")  # remove .shp at the end
            
            preparation = Preparation()
            locationStr = preparation.constructLocation(locationName = shpFileName, latitude = y_dom.Mid, longitude = x_dom.Mid, timeZone = 0, elevation = z_dom.Mid)
            
            
            shapefile.Close()
            printMsg = "ok"
            
            return locationStr, printMsg
    
    
    def readSHPfile(self, shpFilePath, locationLatitudeD, locationLongitudeD, northRad=0, originPt=rg.Point3d(0,0,0), unitConversionFactor=1, osm_id_Only=[], osm_way_id_Only=[], osm_id_Remove=[], osm_way_id_Remove=[]):
        """ read shapefile """
        
        # shapefile is always reprojected to UTM in Gismo
        outputCRS = self.UTM_CRS_from_latitude(locationLatitudeD, locationLongitudeD)
        
        
        # fix invalid shapes, overlapping shape issues, shape vertices direction ...
        utils = MapWinGIS.UtilsClass()
        shapefile = MapWinGIS.ShapefileClass()
        openShapefileSuccess = MapWinGIS.ShapefileClass.Open(shapefile, shpFilePath, None)
        
        
        if (not openShapefileSuccess) or (not shapefile):
            # maybe the 'shpFilePath' is incorrect, or shapefile type is not supported (SHP_MULTIPATCH)
            shapefileShapeType = proj4_str = shortenedName_keys = values = shapes = None
            
            validShapes = False
            printMsg = "Shapefile reading failed. Check: \n" +\
                       "1) If '_shpFile' file path is correct. If it is: \n" +\
                       "2) In the same folder where the .shp file is, check if there are .shx,.dbf,.prj files with the same file name. These two files are essential, in order to open the .shx file.\n" +\
                       "3) If both upper two checks are fine: post a question about this issue on Gismo forum (grasshopper3d.com/group/gismo) with .shp and its files attached, and a screenshot of the message coming from 'readMe!' output."
            
            print "shapefile.ErrorMsg: ", shapefile.ErrorMsg
            
            utils = MapWinGIS.UtilsClass()
            convertErrorNo = MapWinGIS.GlobalSettingsClass().GdalLastErrorNo
            convertErrorMsg = MapWinGIS.GlobalSettingsClass().GdalLastErrorMsg
            convertErrorType = MapWinGIS.GlobalSettingsClass().GdalLastErrorType
            reprojectErrorMsg = MapWinGIS.GlobalSettingsClass().GdalReprojectionErrorMsg
            print "convertErrorNo: ", convertErrorNo
            print "convertErrorMsg: ", convertErrorMsg
            print "convertErrorType: ", convertErrorType
            print "reprojectErrorMsg: ", reprojectErrorMsg
            print "utils.ErrorMsg: ", utils.ErrorMsg
            print "utils.LastErrorCode: ", utils.LastErrorCode
            
            return shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, moveVector, validShapes, printMsg
        
        elif openShapefileSuccess:
            
            # direct reprojection
            numOfsuccessfullyReprojectedShapes_sb = clr.StrongBox[System.Int32]()  # instance of clr.StrongBox
            shapefileFixedSuccess, fixedShapefile = MapWinGIS.ShapefileClass.FixUpShapes(shapefile)  # fails on MapWinGIS 4.9.4.2. Does not fail on Map Window Lite 32x
            
            """
            print "shapefileFixedSuccess: ", shapefileFixedSuccess
            print "fixedShapefile: ", fixedShapefile
            """
            
            if shapefileFixedSuccess:
                # shape file has been fixed
                #reprojectedShapefile = MapWinGIS.ShapefileClass.Reproject(shapefile, outputCRS, numOfsuccessfullyReprojectedShapes_sb)
                reprojectedShapefile = MapWinGIS.ShapefileClass.Reproject(fixedShapefile, outputCRS, numOfsuccessfullyReprojectedShapes_sb)
            else:
                # shapefile has NOT been fixed. Use the initial shapefile
                reprojectedShapefile = MapWinGIS.ShapefileClass.Reproject(shapefile, outputCRS, numOfsuccessfullyReprojectedShapes_sb)
            
            numOfsuccessfullyReprojectedShapes = numOfsuccessfullyReprojectedShapes_sb.Value
            
            """
            print "numOfsuccessfullyReprojectedShapes: ", numOfsuccessfullyReprojectedShapes
            print "type(numOfsuccessfullyReprojectedShapes): ", type(numOfsuccessfullyReprojectedShapes)
            print "reprojectedShapefile: ", reprojectedShapefile
            """
            
            """
            # testing fixing of shapes
            print "reprojectedShapefile: ", reprojectedShapefile
            # testing MapWinGIS.ShapefileClass.FixUpShapes
            shpFilePath_saved = shpFilePath[:-4] + "_saved_" + str(int(time.time())) + ".shp"
            print "shpFilePath_saved: ", shpFilePath_saved
            success = MapWinGIS.ShapefileClass.SaveAs(reprojectedShapefile, shpFilePath_saved, None)
            print "success: ", success
            """
        
        
        if (numOfsuccessfullyReprojectedShapes == 0) or (reprojectedShapefile == None):
            # reprojection failed
            print "REPROJECTION FAILED"
            convertErrorNo = MapWinGIS.GlobalSettingsClass().GdalLastErrorNo
            convertErrorMsg = MapWinGIS.GlobalSettingsClass().GdalLastErrorMsg
            convertErrorType = MapWinGIS.GlobalSettingsClass().GdalLastErrorType
            reprojectErrorMsg = MapWinGIS.GlobalSettingsClass().GdalReprojectionErrorMsg
            print "numOfsuccessfullyReprojectedShapes: ", numOfsuccessfullyReprojectedShapes
            print "convertErrorNo: ", convertErrorNo
            print "convertErrorMsg: ", convertErrorMsg
            print "convertErrorType: ", convertErrorType
            print "reprojectErrorMsg: ", reprojectErrorMsg
            print "utils.ErrorMsg: ", utils.ErrorMsg
            print "utils.LastErrorCode: ", utils.LastErrorCode
            
            reprojectionError = fixedShapefile.ErrorMsg(fixedShapefile.LastErrorCode)
            
            shapefileShapeType = proj4_str = shortenedName_keys = values = shapes = None
            validShapes = False
            printMsg = "The following error emerged while processing the data:\n" + \
                       " \n" + \
                       "\"%s\"\n" % reprojectionError + \
                       "numOfsuccessfullyReprojectedShapes: %s\n" % numOfsuccessfullyReprojectedShapes + \
                       " \n" + \
                       "Open new topic about it on: www.grasshopper3d.com/group/gismo/forum, and attached .shp and all its files (.shx, .dbf, .prj)."
            return shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, moveVector, validShapes, printMsg
        
        
        originPtProjected_meters = self.projectedLocationCoordinates(locationLatitudeD, locationLongitudeD)  # in meters!
        originPtProjected = Rhino.Geometry.Point3d(originPtProjected_meters.X/unitConversionFactor, originPtProjected_meters.Y/unitConversionFactor, originPtProjected_meters.Z/unitConversionFactor)  # in Rhino units
        moveVector = originPt - originPtProjected  # later
        
        # rotation due to north angle position
        #transformMatrixRotate = Rhino.Geometry.Transform.Rotation(-northRad, Rhino.Geometry.Vector3d(0,0,1), originPt)  # counter-clockwise
        transformMatrixRotate = Rhino.Geometry.Transform.Rotation(northRad, Rhino.Geometry.Vector3d(0,0,1), originPt)  # clockwise
        
        
        # open reprojectedShapefile
        
        # ShapeType of a whole shapefile (.shp) and also of each 'shape' in the shapefile (.shp)
        shapeShapeType_dict = {}
        shapeShapeType_dict[0] = 'SHP_NULLSHAPE'
        shapeShapeType_dict[1] = 'SHP_POINT'
        shapeShapeType_dict[3] = 'SHP_POLYLINE'
        shapeShapeType_dict[5] = 'SHP_POLYGON'
        shapeShapeType_dict[8] = 'SHP_MULTIPOINT'
        shapeShapeType_dict[11] = 'SHP_POINTZ'
        shapeShapeType_dict[13] = 'SHP_POLYLINEZ'
        shapeShapeType_dict[15] = 'SHP_POLYGONZ'
        shapeShapeType_dict[18] = 'SHP_MULTIPOINTZ'
        shapeShapeType_dict[21] = 'SHP_POINTM'
        shapeShapeType_dict[23] = 'SHP_POLYLINEM'
        shapeShapeType_dict[23] = 'SHP_POLYGONM'
        shapeShapeType_dict[28] = 'SHP_MULTIPOINTM'
        shapeShapeType_dict[31] = 'SHP_MULTIPATCH'
        
        # loop through shortenedName_keys (these are shapefile fields (":" is replaced with "_" and maximal size is 10 characters))
        shortenedName_keys = []
        for i in xrange(reprojectedShapefile.NumFields):
            field = reprojectedShapefile.Field(i)
            shortenedName_keys.append(field.Name)
        
        
        values = Grasshopper.DataTree[object]()
        shapes = Grasshopper.DataTree[object]()
        
        for i in xrange(reprojectedShapefile.NumShapes):
            shape_com = reprojectedShapefile.Shape[i]
            shape = Marshal.CreateWrapperOfType(shape_com, MapWinGIS.ShapeClass)
            if not shape.IsValid:
                fixedShape = MapWinGIS.ShapeClass.FixUp(shape)
                if (fixedShape != None):
                    shape = fixedShape
                
            
            
            if (shape.ShapeType == 0):  # NULL_SHAPE
                # ShapeType: NULL_SHAPE
                
                # values
                subValuesL = []
                for g in xrange(reprojectedShapefile.NumFields):
                    value = reprojectedShapefile.CellValue(g,i)
                    subValuesL.append(value)
                values.AddRange(subValuesL, Grasshopper.Kernel.Data.GH_Path(i))
                
                # pts
                ptsPerShape = [None]
                shapes.AddRange(ptsPerShape, Grasshopper.Kernel.Data.GH_Path(i))
            
            if (shape.ShapeType == 1):  # SHP_POINT
                # ShapeType: POINT
                
                # values
                subValuesL = []
                for g in xrange(reprojectedShapefile.NumFields):
                    value = reprojectedShapefile.CellValue(g,i)
                    if value == "yes": value = True  # for example: "building=yes"
                    subValuesL.append(value)
                
                # pts
                ptsPerShape = []
                for k in xrange(shape.numPoints):
                    pt = shape.Point[k]
                    point3dProjected = Rhino.Geometry.Point3d(pt.x/unitConversionFactor, pt.y/unitConversionFactor, pt.z/unitConversionFactor)
                    point3dMoved = point3dProjected + moveVector
                    succ = point3dMoved.Transform(transformMatrixRotate)
                    ptsPerShape.append(point3dMoved)
                
                subValuesL_filtered, ptsPerShape_filtered = self.filterShapes(shortenedName_keys, subValuesL, ptsPerShape, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove)
                
                values.AddRange(subValuesL_filtered, Grasshopper.Kernel.Data.GH_Path(i))
                shapes.AddRange(ptsPerShape_filtered, Grasshopper.Kernel.Data.GH_Path(i))
                del ptsPerShape
            
            elif (shape.ShapeType == 3) or (shape.ShapeType == 13) or (shape.ShapeType == 5) or (shape.ShapeType == 15):
                # ShapeType: POLYLINE, POLYLINEZ, POLYGON, POLYGONZ
                
                for n in xrange(shape.NumParts):
                    # values
                    subValuesL = []
                    for g in xrange(reprojectedShapefile.NumFields):
                        value = reprojectedShapefile.CellValue(g,i)
                        if value == "yes": value = True  # for example: "building=yes"
                        subValuesL.append(value)
                    
                    
                    # points
                    ptsPerPart = []
                    subShape = shape.PartAsShape(n)
                    for k in xrange(subShape.numPoints):
                        pt = subShape.Point[k]
                        
                        X = pt.x/unitConversionFactor
                        Y = pt.y/unitConversionFactor
                        Z = pt.z/unitConversionFactor
                        
                        """
                        elif (shape.ShapeType != 13):  # POLYLINEZ
                            ## FIX ##
                            #if (k == 0):
                            if (k == subShape.numPoints-1):
                                #Z = subShape.Point[subShape.numPoints-1].z
                                Z = subShape.Point[0].z
                            else:
                                Z = pt.z/unitConversionFactor
                            ## FIX ##
                        """
                        
                        point3dProjected = Rhino.Geometry.Point3d(X, Y, Z)  # in Rhino document units
                        point3dMoved = point3dProjected + moveVector
                        succ = point3dMoved.Transform(transformMatrixRotate)
                        ptsPerPart.append(point3dMoved)
                    polyline = Rhino.Geometry.Polyline(ptsPerPart)
                    
                    subValuesL_filtered, shapesL_filtered = self.filterShapes(shortenedName_keys, subValuesL, [polyline], osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove)
                    
                    values.AddRange(subValuesL_filtered, Grasshopper.Kernel.Data.GH_Path(i,n))
                    shapes.AddRange(shapesL_filtered, Grasshopper.Kernel.Data.GH_Path(i,n))
                    del subValuesL
                    del ptsPerPart
                    del polyline
                    del subValuesL_filtered
                    del shapesL_filtered
                subShape = None
            
            elif (shape.ShapeType == 31):  # MULTI_PATCH
                # ShapeType: MULTI_PATCH
                shapefileShapeType = proj4_str = shortenedName_keys = values = shapes = None
                validShapes = False
                printMsg = "Gismo at the moment does not support MULTI_PATCH shapefile shapes."
                return shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, moveVector, validShapes, printMsg
            
            else:
                shapeShapeType = shapeShapeType_dict[shape.ShapeType]
                
                shapefileShapeType = proj4_str = shortenedName_keys = values = shapes = None
                validShapes = False
                printMsg = "Gismo at the moment does not support {} shapefile type shapes.\nAsk a question on the forum (https://www.grasshopper3d.com/group/gismo/forum) if this type can be added to Gismo.".format(shapeShapeType)
                return shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, moveVector, validShapes, printMsg
        
        
        shapefileShapeType = shapeShapeType_dict[shapefile.ShapefileType]
        proj4_str = shapefile.Projection
        
        shapefile.Close()
        reprojectedShapefile.Close()
        
        
        validShapes = True
        printMsg = "ok"
        
        return shortenedName_keys, values, shapes, shapefileShapeType, proj4_str, moveVector, validShapes, printMsg
    
    
    def filterShapes(self, shortenedName_keys, subValuesL, shapesL, osm_id_Only, osm_way_id_Only, osm_id_Remove, osm_way_id_Remove):
        """
        filter values and shapes for the four inputs from "OSM ids" component
        """
        value__osm_id = "^#-@"  # dummy value, in case for some unknown reason there is no "osm_id" key
        value__osm_way_id = "^#-@"  # dummy value, in case there is no "osm_way_id" key (shapeType = 1,2)
        for shortenedName_keysIndex, key in enumerate(shortenedName_keys):
            if key == "osm_id":
                value__osm_id = subValuesL[shortenedName_keysIndex]  # it will always be a string, not float, because shapefile keeps its values as strings
            if key == "osm_way_id":
                value__osm_way_id = subValuesL[shortenedName_keysIndex]  # it will always be a string, not float, because shapefile keeps its values as strings
        
        
        # removing shapes
        if value__osm_id in osm_id_Remove:
            return [], []
        elif value__osm_way_id in osm_way_id_Remove:
            return [], []
        
        # allowing this shapes
        if value__osm_id in osm_id_Only:
            return subValuesL, shapesL
        elif value__osm_way_id in osm_way_id_Only:
            return subValuesL, shapesL
        else:
            if (len(osm_id_Only) == 0) and (len(osm_way_id_Only) == 0):
                # "osm_id_Only" and "osm_way_id_Only" are empty. Use ALL shapes except ones whos "osm_id" and "osm_way_id" are defined in either "osm_id_Remove" and "osm_way_id_Remove"
                return subValuesL, shapesL
            else:
                # either "osm_id_Only" and "osm_way_id_Only" are NOT empty. Use ONLY those shapes whos "osm_id" and "osm_way_id" are defined in either "osm_id_Only" and "osm_way_id_Only"
                return [], []
    
    
    def tagEqual_to_requiredTag(self, branchIndex, keys, values_shiftedPaths_LL, requiredKeyL, requiredValuesLL, OSMobjectNameL):
        """
        determine if shapes's tags (key=value pairs) correspond to particular requiredTag (key=value pair)
        """
        value = ""  # dummy values in case requiredKey or requiredValues does not exist
        foundShapesSwitch = False  # initial value
        for keyIndex,key in enumerate(keys):
            for requiredKeyIndex,requiredKey in enumerate(requiredKeyL):
                if (key == requiredKey):
                    # requiredKey is found, check if requiredValue can be found
                    
                    # first check if a value is a multi-value or not (example: "commercial;residential")
                    values_unsplitted = values_shiftedPaths_LL[branchIndex][keyIndex]
                    if (type(values_unsplitted) == System.Boolean):  # "OSM shapes" component replaces all "building"="yes"/"no" values with "building"=True/False. This is why it is not possible to split(";") the Boolean value, as it is a string
                        values_stripped = [values_unsplitted]
                    elif (type(values_unsplitted) != System.Boolean):
                        values_splitted = values_unsplitted.split(";")  # in case a value is not a single item but a multiple-value (wiki.openstreetmap.org/wiki/Multiple_values). If it is a single value, then .strip(";") will not be performed
                        values_stripped = [value2.strip()  for value2 in values_splitted]
                    
                    for value in values_stripped:
                        if (value in requiredValuesLL[requiredKeyIndex]) and (value != ""):
                            foundShapesSwitch = True
                            OSMobjectName = OSMobjectNameL[requiredKeyIndex]  # "requiredKeyL" and "OSMobjectNameL" lists have the same number of items
                            
                            del values_shiftedPaths_LL
                            return foundShapesSwitch, value, [OSMobjectName]
                        elif (key == requiredKey) and (requiredValuesLL[requiredKeyIndex] == ["^"]) and (value != ""):
                            foundShapesSwitch = True
                            OSMobjectName = OSMobjectNameL[requiredKeyIndex]  # "requiredKeyL" and "OSMobjectNameL" lists have the same number of items
                            
                            del values_shiftedPaths_LL
                            return foundShapesSwitch, value, [OSMobjectName]
        
        del values_shiftedPaths_LL
        return foundShapesSwitch, value, []
    
    
    def checkIfShapefilesAreValid(self, keys, values):
        """
        check if the .shp files have been created correctly according to the supplied "requiredKeys_" in osmconf.ini file
        """
        max_valuesBranch_length = 0
        for values_branchL in values.Branches:
            if (len(values_branchL) > max_valuesBranch_length):
                max_valuesBranch_length = len(values_branchL)
        
        if (len(keys) > 0) and (max_valuesBranch_length > 0):
            if (len(keys) != max_valuesBranch_length):
                heightPerLevel = randomHeightRange = randomHeightRangeStart = randomHeightRangeEnd = treeType = osm_id_Only = osm_way_id_Only = osm_id_Remove = osm_way_id_Remove = shapeType = None
                validShapefiles = False
                printMsg = "The component generated invalid shapes data.\n" + \
                           " \n" + \
                           "To fix this issue, simply rerun the component (set the \"_runIt\" input to \"False\", and then again to \"True\")."
            else:
                validShapefiles = True
                printMsg = "ok"
        
        del keys; del values
        return validShapefiles, printMsg


class OSM():
    """
    methods for manipulation of OSM and GIS data
    """
    def requiredTag_dictionary(self):
        """
        tags for particular OSM objects
        """
        requiredKeyRequiredValue_dict = {
        """Building""" : ["building", ("^",)],  # "^" means there is no specific value for this key
        """Commercial building""" : ["building", ("commercial", "retail",)],
        """Residential building""" : ["building", ("residential", "apartments", "terrace", "house", "detached")],
        """Office building""" : ["building", ("office",)],
        """Office administrative""" : ["office", ("administrative",)],
        """Office government""" : ["office", ("government",)],
        """Post office""" : ["amenity", ("post_office",)],
        """Hospital""" : ["amenity", ("hospital",)],
        """Ambulance station""" : ["emergency", ("ambulance_station",)],
        """Pharmacy""" : ["amenity", ("pharmacy",)],
        """Police""" : ["amenity", ("police",)],
        """Fire station""" : ["amenity", ("fire_station",)],
        """Museum""" : ["tourism", ("museum",)],
        """Theatre""" : ["amenity", ("theatre",)],
        """Library""" : ["amenity", ("library",)],
        """Book store""" : ["shop", ("books",)],
        """College""" : ["amenity", ("college",)],
        """University""" : ["amenity", ("university",)],
        """School""" : ["amenity", ("school",)],
        """Kindergarten""" : ["amenity", ("kindergarten",)],
        # -----------------
        """Playground""" : ["leisure", ("playground",)],
        """Sports center""" : ["leisure", ("sports_centre",)],
        """Stadium""" : ["leisure", ("stadium",)],
        """Park""" : ["leisure", ("park",)],
        """Garden""" : ["leisure", ("garden",)],
        """Camping site""" : ["tourism", ("camp_site",)],
        """Tree""" : ["natural", ("tree",)],
        """Forest""" : ["natural", ("wood",)],
        """Forest (managed)""" : ["landuse", ("forest",)],
        """Grassland""" : ["natural", ("grassland",)],
        """Waterway""" : ["waterway", ("^",)],  # "^" means there is no specific value for this key
        """Coastline""" : ["natural", ("coastline",)],
        # -----------------
        """Cafe""" : ["amenity", ("cafe",)],
        """Bar""" : ["amenity", ("bar",)],
        """Pub""" : ["amenity", ("pub",)],
        """Winery""" : ["craft", ("winery",)],
        """Restaurant""" : ["amenity", ("restaurant",)],
        """Supermarket""" : ["shop", ("supermarket",)],
        """Public market""" : ["amenity", ("marketplace",)],
        """Mall""" : ["shop", ("mall",)],
        """Hostel""" : ["tourism", ("hostel",)],
        """Hotel""" : ["tourism", ("hotel",)],
        """Casino""" : ["amenity", ("casino",)],
        # -----------------
        """Road""" : ["highway", ("road", "primary", "secondary", "tertiary", "unclassified", "residential", "service", "track", "junction", "trunk", "motorway", "motorway_link", "trunk_link", "primary_link", "secondary_link", "tertiary_link", "living_street", "bus_guideway", "escape")],
        """Railway""" : ["railway", ("rail", "tram", "light_rail", "subway", "narrow_gauge", "funicular")],
        """Footway""" : ["highway", ("footway",)],
        """Steps""" : ["highway", ("steps",)],
        """Pedestrian zone""" : ["highway", ("pedestrian",)],
        """Aeroway""" : ["aeroway", ("aerodrome",)],
        """Bicycle parking""" : ["amenity", ("bicycle_parking",)],
        """Bicycle rental""" : ["amenity", ("bicycle_rental",)],
        """Fuel""" : ["amenity", ("fuel",)],
        """Parking""" : ["amenity", ("parking",)],
        """Garage""" : ["landuse", ("garages",)],
        """Subway entrance""" : ["railway", ("subway_entrance",)],
        # -----------------
        """Construction area""" : ["landuse", ("construction",)],
        """Archaeological site""" : ["historic", ("archaeological_site",)],
        """Fountain""" : ["amenity", ("fountain",)],
        """Wind turbine""" : ["generator:source", ("wind",)],
        """Plant""" : ["power", ("plant",)],
        """Nuclear reactor""" : ["generator:source", ("nuclear",)],
        # -----------------
        """Internet access""" : ["internet_access", ("^",)],  # "^" means there is no specific value for this key
        """Toilet""" : ["amenity", ("toilets",)],
        """Color""" : ["colour", ("^",)]  # "^" means there is no specific value for this key
        }
        
        return requiredKeyRequiredValue_dict


def raiseWarning(booleanValue, printMsg):
    if not booleanValue:
        level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)


# send classes to sticky
sc.sticky["gismo_check"] = Check()
sc.sticky["gismo_mainComponent"] = mainComponent
sc.sticky["gismo_Transfrom"] = Transform
sc.sticky["gismo_Preparation"] = Preparation
sc.sticky["gismo_CreateGeometry"] = CreateGeometry
sc.sticky["gismo_EnvironmentalAnalysis"] = EnvironmentalAnalysis
sc.sticky["gismo_IO"] = IO
sc.sticky["gismo_GIS"] = GIS
sc.sticky["gismo_OSM"] = OSM
sc.sticky["gismo_mapwingisFolder"] = mapFolder_

# check gismoFolder
gismo_mainComponent = mainComponent()
gismoFolder, printMsg = gismo_mainComponent.gismoWorkingFolder(gismoFolder_)
raiseWarning(gismoFolder, printMsg)
sc.sticky["gismo_gismoFolder"] = gismoFolder

# check mapWinGIS
iteropMapWinGIS_dll_folderPath, gdalDataPath_folderPath, validInstallFolder, printMsg = gismo_mainComponent.mapWinGIS(mapFolder_)
raiseWarning(validInstallFolder, printMsg)

if gismoFolder and validInstallFolder:
    print "The Gismo penguin is peeping!! Gismo Gismo component is ran successfully!\n\ngismoFolder_: %s\nmapFolder_: %s" % (gismoFolder, iteropMapWinGIS_dll_folderPath)
if gismoFolder:
    sc.sticky["gismoGismo_released"] = ""  # mapWinGIS might not be used for all components, so validInstallFolder = True is not important for all components
    # online check of Gismo Gismo version from the github repository

# send the Gismo_Gismo component to the back
ghenv.Component.OnPingDocument().SelectAll()
ghenv.Component.Attributes.Selected = False
ghenv.Component.OnPingDocument().BringSelectionToTop()
ghenv.Component.OnPingDocument().DeselectAll()
