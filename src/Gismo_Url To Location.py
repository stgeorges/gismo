# url to location
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
Use this component to find coordinates of a specific location using an url from openstreetmap, google maps, bing maps, wego.here and waze.
-
Provided by Gismo 0.0.3
    
    input:
        _url: Openstreetmap, google maps, bing maps, wego.here, waze link from which address will be extracted.
        openweb_: if True open the link in web browser.
                  -
                  If nothing added to this input, it is set to False by the default.
    output:
        readMe!: ...
        location: Location (latitude, longitude coordinates) of the _point input.
"""

ghenv.Component.Name = "Gismo_Url To Location"
ghenv.Component.NickName = "UrlToLocation"
ghenv.Component.Message = "VER 0.0.3\nJAN_29_2019"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | Gismo"
#compatibleGismoVersion = VER 0.0.3\nJAN_29_2019
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

import scriptcontext as sc
import Grasshopper
import webbrowser


def main(url, openweb):
    
    # check inputs
    if (url == None):
        required_location = None
        validInputData = False
        printMsg = "Please add an openstreetmap/google maps/bing maps/wego.here/waze link to the \"_url\" input."
        return required_location, validInputData, printMsg
    else:
        if ("htt" not in url):
            required_location = None
            validInputData = False
            printMsg = "The link added to the \"_url\" input is invalid."
            return required_location, validInputData, printMsg
    
    if ("openstreetmap" in url):
        """
        # url examples:
        https://www.openstreetmap.org/directions?from=48.8666%2C2.3335&to=#map=11/48.8072/2.4804
        https://www.openstreetmap.org/#map=11/48.8072/2.4804
        https://www.openstreetmap.org/search?query=paris#map=12/48.8589/2.3469
        """
        url_splitted = url.split("/")
        latitude = url_splitted[-2]
        longitude = url_splitted[-1]
    
    elif ("google.com/maps" in url):
        """
        # url examples:
        https://www.google.com/maps/@47.696472,11.1045472,7z
        https://www.google.com/maps/place/Paris,+France/@48.8588377,2.2770201,12z/data=!3m1!4b1!4m5!3m4!1s0x47e66e1f06e2b70f:0x40b82c3688c9460!8m2!3d48.856614!4d2.3522219
        https://www.google.com/maps/dir/48.9604074,2.2797754/Cr%C3%A9teil,+France/@48.8678084,2.2275165,11z/data=!3m1!4b1!4m9!4m8!1m0!1m5!1m1!1s0x47e60caf330272df:0x4573b9315445d467!2m2!1d2.455572!2d48.790367!3e3
        """
        url_splitted1 = url.split("@")[1]
        #print "url_splitted1: ", url_splitted1
        url_splitted2 = url_splitted1.split(",")
        #print "url_splitted2: ", url_splitted2
        latitude = url_splitted2[0]
        longitude = url_splitted2[1]
    
    elif ("bing.com/maps" in url):
        """
        # url examples:
        https://www.bing.com/maps?osid=d386909d-4f71-40f8-a100-2f784f6effca&cp=48.213799~16.305401&lvl=11&v=2&sV=2&form=S00027
        https://www.bing.com/maps?osid=e4016006-1ce2-48fd-ad27-79426f6ec6fe&cp=48.892133~2.31327&lvl=11&v=2&sV=2&form=S00027
        https://www.bing.com/maps?osid=257fa7fa-f75d-4c21-b662-473856621d96&cp=48.853701~2.33737&lvl=16&imgid=4650638f-6b2a-45d1-864b-700756cb52e9&v=2&sV=2&form=S00027
        """
        url_splitted1 = url.split("&cp=")[1]
        #print "url_splitted1: ", url_splitted1
        url_splitted2 = url_splitted1.split("~")
        #print "url_splitted2: ", url_splitted2
        latitude = url_splitted2[0]
        url_splitted_forLongitude = url_splitted2[1].split("&lvl=")
        longitude = url_splitted_forLongitude[0]
    
    elif ("wego" in url):
        """
        # url examples:
        https://wego.here.com/?map=48.84691,2.35213,15,normal
        https://wego.here.com/directions/mix/14-Impasse-Carnot,-92240-Malakoff,-France:48.81591,2.30060/Saint-Denis,-France:loc-dmVyc2lvbj0xO3RpdGxlPVNhaW50LURlbmlzO2xhbmc9ZnI7bGF0PTQ4LjkzOTkzO2xvbj0yLjM1NTQ3O2NpdHk9U2FpbnQtRGVuaXM7Y291bnRyeT1GUkE7c3RhdGU9SWxlLWRlLUZyYW5jZTtjb3VudHk9U2VpbmUtU2FpbnQtRGVuaXM7Y2F0ZWdvcnlJZD1jaXR5LXRvd24tdmlsbGFnZTtzb3VyY2VTeXN0ZW09aW50ZXJuYWw7cGRzQ2F0ZWdvcnlJZD05MDAtOTEwMC0wMDAw/16-Rue-Auguste-Gervais,-92130-Issy-les-Moulineaux,-France:48.82264,2.27322?map=48.87793,2.30557,12,normal&msg=74B%20Avenue%20du%20Pr%C3%A9sident%20Wilson
        https://wego.here.com/france/saint-denis/city-town-village/saint-denis--loc-dmVyc2lvbj0xO3RpdGxlPVNhaW50LURlbmlzO2xhbmc9ZnI7bGF0PTQ4LjkzOTkzO2xvbj0yLjM1NTQ3O2NpdHk9U2FpbnQtRGVuaXM7Y291bnRyeT1GUkE7c3RhdGU9SWxlLWRlLUZyYW5jZTtjb3VudHk9U2VpbmUtU2FpbnQtRGVuaXM7Y2F0ZWdvcnlJZD1jaXR5LXRvd24tdmlsbGFnZTtzb3VyY2VTeXN0ZW09aW50ZXJuYWw7cGRzQ2F0ZWdvcnlJZD05MDAtOTEwMC0wMDAw?map=48.93993,2.35547,15,normal&msg=Saint-Denis
        """
        url_splitted1 = url.split("map=")[1]
        #print "url_splitted1: ", url_splitted1
        url_splitted2 = url_splitted1.split(",")
        #print "url_splitted2: ", url_splitted2
        latitude = url_splitted2[0]
        longitude = url_splitted2[1]
    elif ("waze" in url):
        """
        # url example
        https://www.waze.com/ul?ll=48.85661400%2C2.35222190&navigate=yes&zoom=16
        https://www.waze.com/en-GB/livemap?ll=48.856614%2C2.3522219&from=48.936181%2C2.357443&at=now
        """
        url_splitted1 = url.split("?ll=")[1]
        #print "url_splitted1: ", url_splitted1
        url_splitted2 = url_splitted1.split("%2C")
        #print "url_splitted2: ", url_splitted2
        latitude = url_splitted2[0]
        url_splitted_forLongitude = url_splitted2[1].split("&")
        longitude = url_splitted_forLongitude[0]
    
    
    locationName = "Unknown location"
    timeZone = 0
    elevation = 0
    
    location = gismo_preparation.constructLocation(locationName, latitude, longitude, timeZone, elevation)
    
    if openweb:
        webbrowser.open(url,new=2, autoraise=True)
    
    validInputData = True
    printMsg = "ok"
    
    return location, validInputData, printMsg


level = Grasshopper.Kernel.GH_RuntimeMessageLevel.Warning
if sc.sticky.has_key("gismoGismo_released"):
    validVersionDate, printMsg = sc.sticky["gismo_check"].versionDate(ghenv.Component)
    if validVersionDate:
        gismo_preparation = sc.sticky["gismo_Preparation"]()
        
        location, validInputData, printMsg = main(_url, openweb_)
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
