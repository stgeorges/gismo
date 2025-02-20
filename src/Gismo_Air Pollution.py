# air pollution
#
# Gismo is a plugin for GIS Environmental Analysis (GPL) started by Djordje Spasic.
# 
# This file is part of Gismo.
# 
# Copyright (c) 2025, Djordje Spasic <djordjedspasic@gmail.com>
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to calculate the following current air pollution indices/gases at 32 meters height above the ground:
-
- Air Quality index (AQI)
- Nitrogen dioxide (NO2)
- Particulate matter 10<=μm (PM10)
- Ozone (O3)
- Particulate matter 2.5<=μm (PM2.5)
- Sulphur dioxide (SO2)
- Ammonia (NH3)
- Carbon monoxide (CO)
- Nitrogen monoxide (NO)
------
Component mainly based on:
https://openweathermap.org/api/air-pollution
-
Provided by Gismo 0.0.3
    
    input:
        _analysisType: Choose one of the terrain analysis types:
                       0 - Air Quality Index (AQI)
                       1 - Nitrogen dioxide (NO2)
                       2 - Particulate matter 10<=μm (PM10)
                       3 - Ozone (O3)
                       4 - Particulate matter 2.5<=μm (PM2.5)
                       5 - Sulphur dioxide (SO2)
                       6 - Ammonia (NH3)
                       7 - Carbon monoxide (CO)
                       8 - Nitrogen monoxide (NO)
        _location: The output from the "Create Location" or "Address to Location" component.  This is essentially a list of text summarizing a location on the Earth.
        _APIkey: Openweathermap key in order to download current air pollution data. It represents a text with numbers.
                 To obtain this key for free:
                 1) go to:  https://home.openweathermap.org/users/sign_in.
                 2) create a new account, and log in.
                 3) click on "API" and copy your API key.
                 4) paste that API key to "_APIkey" input of this component, and rerun the component.
        radius_: Radius of the finall analysis rectangle ('airPollution' output of this component)
                 Allowed values are: 1000 meters to 100000 meters (1 kilomeer to 100 kilometers)
                 -
                 By default, it is set to 4000 meters (4 kilometers)
        numOfCell_: Number of analysis cells in U and V direction of the final 'airPollution' output.
                    Allowed values are from 2 to 200.
                    -
                    By default it is 4
        current_: if set to True, then this component will always show the current pollution data.
                  if set to False, the previously downloaded data will be used, and not current data.
                  -
                  By default this input is set to True
        origin_: Origin for the final 'airPollution' output.
                 -
                 If not supplied, default point of (0,0,0) will be used.
        legendBakePar_: Optional legend bake parameters from the Gismo "Legend Parameters" component.
                        -
                        Use this input to change the color of the "airPollution" output, or edit the "legend" and "title" outputs.
        bakeIt_: Set to "True" to bake the output geometry into the Rhino scene.
                 -
                 If not supplied default value "False" will be used.
        _runIt: ...
    
    output:
        readMe!: ...
        airPollution: resulting rectangular mesh showing the air pollution data.
        values: Air pollution value for each mesh vertex of 'airPollution' mesh. Depending on '_analysisType' input.
               The units of the value depend on the chosen '_analysisType' input.
        title: Title mesh
        titleOriginPt: Starting point of 'title' mesh.
        legend: Legend mesh
        legendPlane: Legend's starting plane, which can be used to move the "legend" geometry with grasshopper's "Move" component.
                     -
                     Connect this output to a Grasshopper's "Plane" parameter in order to preview the point in the Rhino scene.
"""

ghenv.Component.Name = "Gismo_Air Pollution"
ghenv.Component.NickName = "AirPollution"
ghenv.Component.Message = "VER 0.0.3\nFEB_20_2025"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.3\nFEB_10_2025
try: ghenv.Component.AdditionalHelpFromDocStrings = "3"
except: pass

import rhinoscriptsyntax as rs
import Rhino.Geometry as rg
import scriptcontext as sc
import Grasshopper
import datetime
import System
import time
import json
import os



def checkInputData(_analysisType, _APIkey, _radius, _numOfCell, _origin):
    # check inputs
    
    # analysisType
    if (_analysisType == None):
        origin = None
        validInputData = False
        printMsg = '"_analysisType" input is empty. Input a number from 0 to 8.'
        return origin, validInputData, printMsg
    
    elif (_analysisType < 0) or (_analysisType > 8):
        origin = None
        validInputData = False
        printMsg = '"_analysisType" input only accepts values from 0 to 8. Currently inputted value is "{}"'.format(_analysisType)
        return origin, validInputData, printMsg
    
    
    
    # APIkey
    if (_APIkey == None):
        origin = None
        validInputData = False
        printMsg = '"_APIkey" input has not been added. To obtain it for free:\n' + \
            '1) go to:  https://home.openweathermap.org/users/sign_in \n' + \
            '2) create a new account, and log in\n' + \
            '3) click on "API" and copy your API key\n' + \
            '4) paste that API key to "_APIkey" input of this component, and rerun the component.'
        return origin, validInputData, printMsg
    
    
    
    # radius
    if (_radius == None):
        origin = None
        validInputData = False
        printMsg = '"radius_" input is empty. Input a number (in meters) from 1000 to 100000.'
        return origin, validInputData, printMsg
    
    elif (_radius < 1000) or (_radius > 100000):
        origin = None
        validInputData = False
        printMsg = '"radius_" input only accepts values from 1000 meters to 100000 meters (1 kilomeer to 100 kilometers).\n' +\
                   'Input a number (in meters) from 1000 to 100000.'
        return origin, validInputData, printMsg
    
    
    
    # numOfCell
    if (_numOfCell == None):
        origin = None
        validInputData = False
        printMsg = '"numOfCell_" input is empty. Input a number from 2 to 200.'
        return origin, validInputData, printMsg
    
    elif (_numOfCell < 2) or (_numOfCell > 200):
        origin = None
        validInputData = False
        printMsg = '"numOfCell_" input only accepts values from 2 to 200. Currently inputted value is "{}"'.format(_numOfCell)
        return origin, validInputData, printMsg
    
    
    if (_origin == None):
        origin = rg.Point3d(0,0,0)
    
    
    validInputData = True
    printMsg = "ok"
    
    return origin, validInputData, printMsg


def main(_analysisType, _location, _APIkey, _radiusInMeter, _numOfCell, _current, _origin, _sleepInSecondPerAPIcall, _legendBakePar):
    # download/load existing (from CSV) air pollution data
    
    
    # a) process inputs
    
    # deconstruct the location again
    locationName, locationLatitudeD, locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_prep.checkLocationData(_location)
    
    # radius in RhinoUnits
    unitConversionFac, unitSystemLabel = gismo_prep.checkUnits()
    radius_InRhinoUnits = _radiusInMeter/unitConversionFac
    
    # radius in KM
    radiusKM = _radiusInMeter/1000
    radiusKM_int = int(radiusKM)  # only for filename
    
    # date, time
    date_now = gismo_prep.dateNow('.')
    time_now = gismo_prep.timeNow(':')
    dateTime_now1 = '{}   {}'.format(date_now, time_now)
    
    
    
    
    
    
    
    # b) analysis rectangular (square) srf
    pln = rg.Plane(_origin, rg.Vector3d(0,0,1))
    domain = rg.Interval(-radius_InRhinoUnits, radius_InRhinoUnits)
    
    rect = rg.Rectangle3d(pln, domain, domain)
    rect_crv = rect.ToNurbsCurve()
    
    
    
    # b)2) analysis srf divPts
    analysis_srf_temp_L = rg.Brep.CreatePlanarBreps( [rect_crv] )
    analysis_srf = analysis_srf_temp_L[0]
    analysis_srf_BF0 = analysis_srf.Faces[0]
    
    divPt_L, divPtNormal_L__dumm, UV_LL__dumm = gismo_geo.srfDivide(analysis_srf_BF0, _numOfCell, _numOfCell)
    
    
    
    # b)3) get latitude,longitude for each divPt
    latitude_L = []
    longitude_L = []
    
    for divPt in divPt_L:
        latitude, longitude = gismo_gis.XYtoLocation(divPt, _location, _origin)
        
        latitude_L.append(latitude)
        longitude_L.append(longitude)
    
    
    
    
    
    # c) get pollution data for each upper latitude, longitude divPt
    ## EXPLAIN ## if input 'current_=False', then use previosuly downloaded .json files (which are saved in .csv file), and a data from it (instead of downloading new .json files via 'http://api.openweathermap.org')
    
    openweathermap_AirPollut_CSV_filename = '{}_{}_{}_radius={}KM_numOfCellInUVdir={}'.format(locationName, locationLatitudeD, locationLongitudeD, radiusKM_int, _numOfCell)
    openweathermap_AirPollut_CSV_filenameWithEXT = '{}.csv'.format(openweathermap_AirPollut_CSV_filename) # example: openweathermap_AirPollut_CSV_filenameWithEXT = 'USA_Lower_West_Side_33.789876_-118.226875_radius=10KM_numOfCellInUVdir=10.csv'
    
    airPollut_folder = R'C:\gismo\weather\openweathermap\air_pollution'  # default. Do not change
    airPollut_folder_final = os.path.join( airPollut_folder, openweathermap_AirPollut_CSV_filename )
    
    openweathermap_AirPollut_CSV_filefull = os.path.join( airPollut_folder_final, openweathermap_AirPollut_CSV_filenameWithEXT )
    openweathermap_AirPollut_CSV_exists = os.path.isfile(openweathermap_AirPollut_CSV_filefull)
    
    
    if (not openweathermap_AirPollut_CSV_exists):
        downloadJSONfile = True
    
    elif openweathermap_AirPollut_CSV_exists:
        if (_current == False):
            downloadJSONfile = False
            print '1)b) Air pollution data NOT downloaded BUT read from an existing CSV FILE (because input "current_ = {}".'.format(current_)
            
            # c)2) read the previously created CSV file, from downloaded JSON files
            csvValue_LL = gismo_IO.readCSV(openweathermap_AirPollut_CSV_filefull, _delimiter)
            
            csvValue_values_LL = csvValue_LL[3:]  # [:3] are header and location data
            csvValue_values_flipped_LL = gismo_prep.LLtranspose(csvValue_values_LL)  # convert CSV rows lists, to CSV column lists
            
            
            
            dateTime_L = csvValue_values_flipped_LL[1]
            
            
            airQualityInx_str_L = csvValue_values_flipped_LL[5]
            airQualityInx_L = [gismo_prep.strToNum(str2)    for str2 in airQualityInx_str_L]
            
            
            NO2_str_L = csvValue_values_flipped_LL[6]
            NO2_L = [gismo_prep.strToNum(str2)    for str2 in NO2_str_L]
            
            PM10_str_L = csvValue_values_flipped_LL[7]
            PM10_L = [gismo_prep.strToNum(str2)    for str2 in PM10_str_L]
            
            O3_str_L = csvValue_values_flipped_LL[8]
            O3_L = [gismo_prep.strToNum(str2)    for str2 in O3_str_L]
            
            PM2_5_str_L = csvValue_values_flipped_LL[9]
            PM2_5_L = [gismo_prep.strToNum(str2)    for str2 in PM2_5_str_L]
            
            
            SO2_str_L = csvValue_values_flipped_LL[10]
            SO2_L = [gismo_prep.strToNum(str2)    for str2 in SO2_str_L]
            
            NH3_str_L = csvValue_values_flipped_LL[11]
            NH3_L = [gismo_prep.strToNum(str2)    for str2 in NH3_str_L]
            
            CO_str_L = csvValue_values_flipped_LL[12]
            CO_L = [gismo_prep.strToNum(str2)    for str2 in CO_str_L]
            
            NO_str_L = csvValue_values_flipped_LL[13]
            NO_L = [gismo_prep.strToNum(str2)    for str2 in NO_str_L]
            
            
            csvValue_values_flipped_final_LL = [airQualityInx_L,   NO2_L, PM10_L, O3_L, PM2_5_L,   SO2_L, NH3_L, CO_L, NO_L]
        
        else:
            downloadJSONfile = True
    
    
    
    
    if downloadJSONfile:
        # d) download the new (current) air pollution data from 'https://openweathermap.org/api/air-pollution'
        print '1)a) Air pollution data started to be downloaded from OPENWEATHERMAP.ORG.'
        
        dateTime_L = []
        
        airQualityInx_L = []
        
        NO2_L = []
        PM10_L = []
        O3_L = []
        PM2_5_L = []
        
        SO2_L = []
        NH3_L = []
        CO_L = []
        NO_L = []
        
        # d)1) create OpenweathermapApi url
        for i in range(latitude_L.Count):
            latitude = latitude_L[i]
            longitude = longitude_L[i]
            
            # based on: https://openweathermap.org/api/air-pollution
            jsonLink = 'http://api.openweathermap.org/data/2.5/air_pollution?lat={}&lon={}&appid={}'.format(latitude, longitude, _APIkey)
            
            # d)2) download OpenweathermapApi json from 'd)1)'
            JSON_asStr = gismo_prep.urlReader(jsonLink)
            
            if (JSON_asStr == 'file failed'):
                # JSON file failed to be accessed via 'jsonLink'
                
                validPollutData = False
                printMsg = 'The component failed to access pollution data from api.openweathermap.org website. Do the following:\n' +\
                           '1) Copy-paste the link from below into your internet browser, and hit Enter:\n' +\
                           '{}\n'.format(jsonLink) +\
                           'If pollution data is successfully shown, then this means that your Rhino app is blocked inside Windows Firewall. Unlbock Rhino, restart your PC, and then rerun this .gh file.\n' +\
                           ' \n' +\
                           '2) If upper link results in an "Error page", then save this .gh file. Open a new topic about this problem on "www.grasshopper3d.com/group/gismo/forum".\n' +\
                           'In that topic: attach the .gh file, and screenshot of this error message.'
                
                final_value_L = colored_analysisMeshRect = titleMesh = titleStartPt = legendMesh = legendPln = None
                return final_value_L, colored_analysisMeshRect, titleMesh, titleStartPt, legendMesh, legendPln, validPollutData, printMsg
            
            
            
            
            # d)3) JSON file successfull accessed via 'jsonLink'. Now try to see if the JSON file is correct
            
            # d)3)I) create dict from dict_str:
            JSON_dict = json.loads(JSON_asStr)
            
            if JSON_dict.has_key('cod'):  # example: JSON_dict = {'cod': 401, 'message': 'Invalid API key. Please see https://openweathermap.org/faq#error401 for more info.'}
                validPollutData = False
                printMsg = 'The component failed to access pollution data from api.openweathermap.org website. Do the following:\n' +\
                           '1) Copy-paste the link from below into your internet browser, and hit Enter:\n' +\
                           '{}\n'.format(jsonLink) +\
                           'If pollution data is successfully shown, then this means that your Rhino app is blocked inside Windows Firewall. Unlbock Rhino, restart your PC, and then rerun this .gh file.\n' +\
                           ' \n' +\
                           '2) Double-check if your "_APIkey" input is correct, by signing in to your account on this page: https://home.openweathermap.org/api_keys.\n' +\
                           ' \n' +\
                           '3) If upper "_APIkey" input is correct, then save this .gh file. Open a new topic about this problem on "www.grasshopper3d.com/group/gismo/forum".\n' +\
                           'In that topic: attach the .gh file, and screenshot of this error message.'
                
                final_value_L = colored_analysisMeshRect = titleMesh = titleStartPt = legendMesh = legendPln = None
                return final_value_L, colored_analysisMeshRect, titleMesh, titleStartPt, legendMesh, legendPln, validPollutData, printMsg
            
            else:
                # example:
                # JSON_dict = {'coord':{'lon':2.3768,'lat':48.8732},'list':[{'main':{'aqi':1},'components':{'co':320.44,'no':0,'no2':20.91,'o3':57.94,'so2':4.41,'pm2_5':5.78,'pm10':8.49,'nh3':1.14},'dt':1672080592}]}
                
                JSON_dict = json.loads(JSON_asStr)
            
            
            
            
            # d)4) extract data from JSON dict
            
            # d)4)I) convert "dt" variable inside the 'JSON_asStr' (which represents unix time) to a readable time string
            unixtime_int = JSON_dict['list'][0]['dt']
            dateTime = datetime.datetime.utcfromtimestamp(unixtime_int)  # returns python datetime.datetime objs (not string!)
            dateTime_str = dateTime.ToString()
            dateTime_L.append(dateTime_str)
            
            
            # d)5) air quality index
            airQualityIndex = JSON_dict['list'][0]['main']['aqi']
            airQualityInx_L.append( airQualityIndex )
            
            
            # d)6) other components
            components_dict = JSON_dict['list'][0]['components']
            
            NO2__microGram_m3 = components_dict['no2']
            PM10__microGram_m3 = components_dict['pm10']
            O3__microGram_m3 = components_dict['o3']
            PM2_5__microGram_m3 = components_dict['pm2_5']
            
            SO2__microGram_m3 = components_dict['so2']
            NH3__microGram_m3 = components_dict['nh3']
            CO__microGram_m3 = components_dict['co']
            NO__microGram_m3 = components_dict['no']
            
            
            NO2_L.append( NO2__microGram_m3 )
            PM10_L.append( PM10__microGram_m3 )
            O3_L.append( O3__microGram_m3 )
            PM2_5_L.append( PM2_5__microGram_m3 )
            
            SO2_L.append( SO2__microGram_m3 )
            NH3_L.append( NH3__microGram_m3 )
            CO_L.append( CO__microGram_m3 )
            NO_L.append( NO__microGram_m3 )
            
            time.sleep(_sleepInSecondPerAPIcall)  # sleep one second
        print '1)c) Air pollution data successfully DOWNLOADED from OPENWEATHERMAP.ORG'
        
        
        
        # d)7) put all lists (from each JSON file) into final 'dowloadedJSONdata_value_LL' list
        dowloadedJSONdata_value_LL = []
        
        dowloadedJSONdata_value_LL.extend( [ 
            airQualityInx_L,
            
            NO2_L,
            PM10_L,
            O3_L,
            PM2_5_L,
            
            SO2_L,
            NH3_L,
            CO_L,
            NO_L  ] )
        
        
        
        
        
        # d)8) create a CSV file from the downloaded JSONs data
        CSVexport_value_LL = []
        CSVexport_value_LL.append( ['pt inx', 'date time', 'latitude', 'longitude', 'pt coord', 'air quality inx', 'NO2', 'PM10', 'O3', 'PM2_5',   'SO2', 'NH3', 'CO', 'NO'] )  # header
        CSVexport_value_LL.append( ['Openweathermap air pollution result'] )
        CSVexport_value_LL.append( ['Location name: {}'.format(locationName)] )
        
        for g in range(latitude_L.Count):
            dateTime = dateTime_L[g]
            
            latitude = latitude_L[g]
            longitude = longitude_L[g]
            
            divPt = divPt_L[g]
            divPt_str = '{}_{}_{}'.format(divPt.X, divPt.Y, divPt.Z)  # using ',' as a decimal separator (instead of '_'), may creator some issues
            
            airQualityInx = airQualityInx_L[g]
            
            NO2 = NO2_L[g]
            PM10 = PM10_L[g]
            O3 = O3_L[g]
            PM2_5 = PM2_5_L[g]
            
            SO2 = SO2_L[g]
            NH3 = NH3_L[g]
            CO = CO_L[g]
            NO = NO_L[g]
            
            row_L = [g,  dateTime,  latitude, longitude,  divPt_str,  airQualityInx,  NO2, PM10, O3, PM2_5,  SO2, NH3, CO, NO]
            CSVexport_value_LL.append( row_L )
        
        
        CSV_filefull = gismo_IO.exportCSV(CSVexport_value_LL, openweathermap_AirPollut_CSV_filename, airPollut_folder_final, _delimiter, _decimal, _encode)
    
    
    
    
    # e) legend, title
    
    # e)1) color the output mesh
    if downloadJSONfile:
        final_value_L = dowloadedJSONdata_value_LL[_analysisType]
    else:
        final_value_L = csvValue_values_flipped_final_LL[_analysisType]
    
    
    # deconstruct the "_legendBakePar" input to color the 'colored_analysisMeshRect', title, legend
    legendStyle, legendPlane, maxValue, minValue, customColor_L, numLegendCells, legendFontName, legendFontSize, numDecimals, legendUnit, customTitle, scale, layerName, layerColor, layerCategoryName = gismo_prep.read_legendBakePar(_legendBakePar)
    
    
    # ceate final 'colored_analysisMeshRect'
    meshColor_L = gismo_prep.numberToColor(final_value_L, customColor_L, minValue, maxValue, _airPollutionValue_tol)
    colored_analysisMeshRect = gismo_geo.meshFromPoints(_numOfCell+1, _numOfCell+1, divPt_L, meshColor_L)
    
    
    
    
    # e)2) title
    # units based on: https://openweathermap.org/weather-data
    
    # remove seconds from dateTime variable, and include it into 'title' string
    first_dateTime = dateTime_L[0]  # example: '2025-02-09 12:03:04'
    
    split_L = first_dateTime.split(':')
    split_L2 = split_L[:-1]
    first_dateTime_withoutSecond = ':'.join(split_L2)  # example: '2025-02-09 12:03'
    
    
    if (_analysisType == 0):
        titleLabelTxt = 'Air Quality Index (AQI)'
        legendUnit = 'unitless'
    
    elif (_analysisType == 1):
        titleLabelTxt = 'Nitrogen dioxide (NO2) concentration'
        legendUnit = 'μg/m3'
    elif (_analysisType == 2):
        titleLabelTxt = 'Particulate matter 10<=μm (PM10) concentration'
        legendUnit = 'μg/m3'
    elif (_analysisType == 3):
        titleLabelTxt = 'Ozone (O3) concentration'
        legendUnit = 'μg/m3'
    elif (_analysisType == 4):
        titleLabelTxt = 'Particulate matter 2.5<=μm (PM2.5) concentration'
        legendUnit = 'μg/m3'
    
    elif (_analysisType == 5):
        titleLabelTxt = 'Sulphur dioxide (SO2) concentration'
        legendUnit = 'μg/m3'
    elif (_analysisType == 6):
        titleLabelTxt = 'Ammonia (NH3) concentration'
        legendUnit = 'μg/m3'
    elif (_analysisType == 7):
        titleLabelTxt = 'Carbon monoxide (CO) concentration'
        legendUnit = 'μg/m3'
    elif (_analysisType == 8):
        titleLabelTxt = 'Nitrogen monoxide (NO) concentration'
        legendUnit = 'μg/m3'
    
    titleLabelTxt2 = titleLabelTxt + '\n' +\
                     'on {}'.format(first_dateTime_withoutSecond) + '\n' +\
                     'Location: {}, lat:{}, lon:{}'.format(locationName, locationLatitudeD, locationLongitudeD) + '\n' +\
                     'Radius: {}KM'.format(radiusKM_int)
    
    titleMesh, titleStartPt, titleTextSize = gismo_prep.createTitle('mesh', [colored_analysisMeshRect], [titleLabelTxt2], customTitle, textSize=legendFontSize, fontName=legendFontName)
    
    
    
    
    # e)3) legend
    legendMesh, legendPln = gismo_geo.createLegend([colored_analysisMeshRect], final_value_L, _legendBakePar, legendUnit)
    
    
    
    
    
    # f) baking, grouping
    if bakeIt_:
        lay = "{}_{}_{}_radiusKM={}_numOfCell={}_dateTime={}".format( locationName, locationLatitudeD, locationLongitudeD,  radiusKM_int, _numOfCell, first_dateTime_withoutSecond )
        
        layParentName = "GISMO"; laySubName = "WEATHER"; layerCategoryName = "AIR_POLLUTION"; newLayerCategory = False
        laySubName_color = System.Drawing.Color.FromArgb(181,230,29)  # green
        layerColor = System.Drawing.Color.FromArgb(0,0,0)  # black
        
        layerIndex, lay_dummy = gismo_prep.createLayer(layParentName, laySubName, layerCategoryName, newLayerCategory, lay, laySubName_color, layerColor, legendBakePar_) 
        
        geometryToBakeL = [colored_analysisMeshRect, titleMesh, legendMesh]
        
        geometry_id_L = gismo_prep.bakeGeometry(geometryToBakeL, layerIndex)
        
        
        # grouping
        groupIndex = gismo_prep.groupGeometry(lay, geometry_id_L)
    
    
    
    # hide origin, legendPlane output
    ghenv.Component.Params.Output[5].Hidden = True
    ghenv.Component.Params.Output[7].Hidden = True
    
    
    
    
    # g) print on console
    print titleLabelTxt
    print 'Location: \'{}\' {},{}'.format(locationName, locationLatitudeD, locationLongitudeD)
    print 'Radius [KM]: {}'.format(radiusKM_int)
    print 'NumOfCell: {}'.format(_numOfCell)
    
    
    
    validPollutData = True
    printMsg = 'ok'
    
    return final_value_L, colored_analysisMeshRect, titleMesh, titleStartPt, legendMesh, legendPln, validPollutData, printMsg


def createOutputDescriptions(_analysisType):
    # create '' and '' output descriptions
    
    if _runIt:
        outputDescriptions = [
        ["Air Quality Index (AQI) analysis mesh.\n" +\
        "Hower over 'values' output to see the description of AQI.", #airPollution
        
        "Current Air Quality Index (AQI) values  at 32 meters above the ground.\n" +\
        "It ranges from 1 (Good) to 5 (Very Poor).\n" +\
        "AQI is calculated based on the following values of pollutant concentrations:\n" +\
        "-\n" +\
        "category   Index  Pollutant concentration [in μg/m3]\n" +\
        "                  SO2      NO2      PM10     PM2.5   O3      CO\n" +\
        "------------------------------------------------------------------------\n" +\
        "Good       1      0-20     0-40     0-20     0-10   0-60     0-4400\n" +\
        "Fair       2      20-80    40-70    20-50    10-25  60-100   4400-9400\n" +\
        "Moderate   3      80-250   70-150   50-100   25-50  100-140  9400-12400\n" +\
        "Poor       4      250-350  150-200  100-200  50-75  140-180  12400-15400\n" +\
        "Very Poor  5      >350     >200     >200     >75    >180     >15400\n"
        "-\n" +\
        "NO and NH3 do not affect the upper AQI.\n" +\
        "-\n" +\
        "Based on: https://openweathermap.org/air-pollution-index-levels\n" +\
        "-\n" +\
        "Unitless."]  #values
        
        ,
        
        ["Nitrogen dioxide (NO2) analysis mesh.\n" +\
        "-\n" +\
        "NO2 primarily gets in the air from the burning of fuel. It forms from emissions from cars, trucks and buses, power plants, and off-road equipment.\n" +\
        "NO2 damages the human respiratory system and contribute to acid rain.",  #airPollution
        
        "Current Nitrogen dioxide (NO2) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        
        ,
        
        ["Particulate matter 10<=μm (PM10) analysis mesh.\n" +\
        "-\n" +\
        "PM10 describes fine inhalable airborne particles measuring less than 10 micrometers in aerodynamic diameter, and is most often produced as a result of wild files, power plants, industries and combustion automobiles.\n" +\
        "Unlike PM2.5, PM10 also includes: dust from construction sites, landfills and agriculture, brush/waste burning, wind-blown dust from open lands, pollen and fragments of bacteria.\n" +\
        "PM10 can increase the risk of health problems like heart disease, asthma, low birth weight and reduced life expectancy. Unhealthy levels can also reduce visibility and cause the air to appear hazy.",  #airPollution
        
        "Current Particulate matter 10<=μm (PM10) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        
        ,
        
        ["Ozone (O3) concentration analysis mesh.\n" +\
        "-\n" +\
        "This is ground level Ozone. Which is a harmful air pollutant. Not the stratospheric Ozone, which protects Earth from sun's harmful ultraviolet rays.\n" +\
        "Ground level Ozone is created when pollutants from power plants, industries, combustion automobiles, and other sources chemically react in the presence of sunlight."
        "Ozone damages the human respiratory system.",  #airPollution
        
        "Current Ozone (O3) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        
        ,
        
        ["Particulate matter 2.5<=μm (PM2.5) analysis mesh.\n" +\
        "-\n" +\
        "PM2.5 describes fine inhalable airborne particles measuring less than 2.5 micrometers in aerodynamic diameter, and is most often produced as a result of wild fires, power plants, industries and combustion automobiles.\n" +\
        'PM2.5 poses greater risk to health than PM10.\n' +\
        "PM2.5 can increase the risk of health problems like heart disease, asthma, low birth weight and reduced life expectancy. Unhealthy levels can also reduce visibility and cause the air to appear hazy.",  #airPollution
        
        "Particulate matter 2.5<=μm (PM2.5) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        
        ,
        
        ["Sulphur dioxide (SO2) concentration analysis mesh.\n" +\
        "-\n" +\
        "It is produced from the burning of fossil fuels and the smelting of mineral ores (aluminum, copper, zinc, lead, and iron) that contain sulfur.\n" +\
        "SO2 damages the human respiratory system, and can severely irrite eyes and skin. It causes acid rain.",  #airPollution
        
        "Current Sulphur dioxide (SO2) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        
        ,
        
        ["Ammonia (NH3) concentration analysis mesh.\n" +\
        "-\n" +\
        "It originates from both natural and human-made sources, with the main source being agriculture, e.g. manures, slurries and fertiliser application.\n" +\
        "Amonia has its benefits: it can purify water, used in cleaning products and for printing in textile industry.\n" +\
        "However, it also a major pollutant.\n" +\
        "When in air in high concenrations it damages the human respiratory system, and can severely irrite eyes.\n" +\
        "When it reaches ground, it impacts soil acidification, even though it is originally a natural process.\n" +\
        "When it reaches freshwater it is causing acidification of rivers and lakes, eutrophication, and direct toxicity to aquatic organisms.",  #airPollution
        
        "Current Ammonia (NH3) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        
        ,
        
        ["Carbon monoxide (CO) concentration analysis mesh.\n" +\
        "-\n" +\
        "It is produced from the burning of fossil fuels, power plants, but also naturally - by Volcanos.\n" +\
        "Depending on concentration, they can cause headache, dizziness, heart issues, brain damage or death.",  #airPollution
        
        "Current Carbon monoxide (CO) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        
        ,
        
        ["Nitrogen monoxide (NO) concentration analysis mesh.\n" +\
        "-\n" +\
        "It is produced from the burning of fossil fuels.\n" +\
        "NO can cause damage to the human respiratory tract and increase a person's vulnerability to respiratory infections and asthma.",  #airPollution
        
        "Current Nitrogen monoxide (NO) concentration values  at 32 meters above the ground.\n" +\
        "-\n" +\
        "In μg/m3."]  #values
        ]
        
        chosenOutputDescription = outputDescriptions[_analysisType]
    
    else:
        chosenOutputDescription = \
        ["Analysed air pollution mesh for chosen '_analysisType' input.",  #airPollution
        
        "Values correspond to each 'airPollution' vertex, for the chosen '_analysisType'.\n" +\
        "Each value is evaluated at 32 meters height, above the ground level."]  #values
    
    
    ghenv.Component.Params.Output[1].Description = chosenOutputDescription[0]  # assing description to 'airPollution' output
    ghenv.Component.Params.Output[2].Description = chosenOutputDescription[1]  # assign description to 'values' output



level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_prep = sc.sticky["gismo_Preparation"]()
        gismo_geo = sc.sticky["gismo_CreateGeometry"]()
        gismo_IO = sc.sticky["gismo_IO"]()
        gismo_gis = sc.sticky["gismo_GIS"]()
        
        _sleepInSecondPerAPIcall = 1
        _delimiter = ';'
        _decimal = ','
        _encode = 'utf-8'
        _airPollutionValue_tol = 0.001
        
        locationName, locationLatitudeD, locationLongitudeD, timeZone, elevation, validLocationData, printMsg = gismo_prep.checkLocationData(_location)
        if validLocationData:
            origin, validInputData, printMsg = checkInputData(_analysisType, _APIkey, radius_, numOfCell_, origin_)
            if validInputData:
                createOutputDescriptions(_analysisType)
                if _runIt:
                    values, airPollution, title, titleOriginPt, legend, legendPln, validPollutData, printMsg = main(_analysisType, _location, _APIkey, radius_, numOfCell_, current_, origin, _sleepInSecondPerAPIcall, legendBakePar_)
                    if not validPollutData:
                        print ' \n \n', printMsg
                        ghenv.Component.AddRuntimeMessage(level, printMsg)
                else:
                    print "All inputs are ok. Please set \"_runIt\" to True, in order to run the Air pollution component"
            else:
                print printMsg
                ghenv.Component.AddRuntimeMessage(level, printMsg)
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

