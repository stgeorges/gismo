# address to location
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2017, Guillaume Meunier <alliages@gmail.com>
#
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to find coordinates of a specific location using an address.
It uses Nominatim API
-
Provided by Gismo 0.0.2
    
    input:
        _address: A string representing the address for which location (latitude and longitude coordinates) is suppose to be found.
    
    output:
        readMe!: explained result of the query
        location: [address, latitude, longitude coordinates) of the input.
"""

ghenv.Component.Name = "Gismo_Address To Location"
ghenv.Component.NickName = "AddressToLocation"
#ghenv.Component.Message = "VER 0.0.2\nFEB_17_2017"
ghenv.Component.Message = "VER 0.0.1\nFEB_22_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | Gismo"
#compatibleGismoVersion = VER 0.0.1\nFEB_09_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import urllib
import json
import httplib

def main(address):
    timeZone = 0; elevation = 0  # default. These two inputs are not important for OSM and terrain components
    url = "http://nominatim.openstreetmap.org/search"
    address = urllib.quote_plus(address)
    format="jsonv2"
    addressdetails="0"
    polygon_="0"
    limit="1"
    url_totale = url+"?q="+address+"&format="+format+"&addressdetails="+addressdetails+"&polygon_="+polygon_+"&limit="+limit+"&email=https://github.com/Alliages"
    url_check = url+".php?q="+address+"&polygon=1&viewbox="
    try:
        request = urllib.urlopen(url_totale)
    except:
        printMsg = "ERROR\nSeems that there are no internet connection...."
        validInputData = False
        return [],validInputData,printMsg 
    try:
        results = json.load(request)
        if 0 < len(results):
            r = results[0]
            printMsg = "Cool, it worked!\n\nHere is the URL if you want to see the location found :\n"+url_check+"\n\nHere is the URL used :\n"+url_totale
            validInputData = True
            location = "Site:Location,\n" + \
               "%s,\n" % address + \
               "%s,      !Latitude\n" % r['lat'] + \
               "%s,     !Longitude\n" % r['lon'] + \
               "%s,     !Time Zone\n" % timeZone + \
               "%s;       !Elevation" % elevation
            return location,validInputData,printMsg
        else:
            printMsg = "HTTP GET Request failed from adress to coordinates (nominatim). TRY another address\n\nHere is the URL if you want to see what's doing :\n"+url_check
            validInputData = False
            return [],validInputData,printMsg 
    except:
        printMsg = 'JSON decode failed: '+str(request)
        validInputData = False
        return [],validInputData,printMsg 


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        if _address:
            location, validInputData, printMsg = main(_address)
        else:
            printMsg = "Please add an address as a string panel"
            validInputData = False
        print printMsg
        if not validInputData:
            ghenv.Component.AddRuntimeMessage(level, printMsg)
    else:
        print printMsg
        ghenv.Component.AddRuntimeMessage(level, printMsg)
else:
    printMsg = "First please run the Gismo Gismo component."
    print printMsg
    ghenv.Component.AddRuntimeMessage(level, printMsg)