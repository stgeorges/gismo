# OSM objects
#
# Gismo is a plugin for GIS environmental analysis (GPL) started by Djordje Spasic.
#
# This file is part of Gismo.
#
# Copyright (c) 2017, Djordje Spasic <djordjedspasic@gmail.com>
# Component icon based on free OSM icon from: <https://icons8.com/web-app/13398/osm>
#
# Gismo is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
# Gismo is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this program. If not, see http://www.gnu.org/licenses/.
#
# The GPL-3.0+ license <http://spdx.org/licenses/GPL-3.0+>

"""
Use this component to chose an OSM object.
-
Provided by Gismo 0.0.2
    
    input:
    
    output:
        OSMobjectName: name of the OSM object
"""

ghenv.Component.Name = "Gismo_OSM Objects"
ghenv.Component.NickName = "OSMobjects"
ghenv.Component.Message = "VER 0.0.2\nMAR_02_2017"
ghenv.Component.IconDisplayMode = ghenv.Component.IconDisplayMode.application
ghenv.Component.Category = "Gismo"
ghenv.Component.SubCategory = "1 | OpenStreetMap"
#compatibleGismoVersion = VER 0.0.2\nMAR_01_2017
try: ghenv.Component.AdditionalHelpFromDocStrings = "2"
except: pass

Post office           = "Post office"
Office administrative = "Office administrative"
Office government     = "Office government"
Residential building  = "Residential building"
Hospital              = "Hospital"
Ambulance station     = "Ambulance station"
Pharmacy              = "Pharmacy"
Police                = "Police"
Fire station          = "Fire station"
Museum                = "Museum"
Theatre               = "Theatre"
Library               = "Library"
Book store            = "Book store"
College               = "College"
University            = "University"
School                = "School"
Kindergarten          = "Kindergarten"
-----------------     = ""
Playground            = "Playground"
Sports center         = "Sports center"
Stadium               = "Stadium"
Park                  = "Park"
Garden                = "Garden"
Camping site          = "Camping site"
Forest                = "Forest"
Grassland             = "Grassland"
-----------------     = ""
Cafe                  = "Cafe"
Bar                   = "Bar"
Pub                   = "Pub"
Winery                = "Winery"
Restaurant            = "Restaurant"
Supermarket           = "Supermarket"
Public market         = "Public market"
Mall                  = "Mall"
Hostel                = "Hostel"
Hotel                 = "Hotel"
Casino                = "Casino"
-----------------     = ""
Road                  = "Road"
Railway               = "Railway"
Footway               = "Footway"
Pedestrian zone       = "Pedestrian zone"
Aeroway               = "Aeroway"
Bicycle parking       = "Bicycle parking"
Bicycle rental        = "Bicycle rental"
Fuel                  = "Fuel"
Parking               = "Parking"
Garage                = "Garage"
Subway entrance       = "Subway entrance"
-----------------     = ""
Construction area     = "Construction area"
Archaeological site   = "Archaeological site"
Fountain              = "Fountain"
Wind turbine          = "Wind turbine"
Plant                 = "Plant"
Nuclear reactor       = "Nuclear reactor"
-----------------     = ""
Internet access       = "Internet access"
Toilet                = "Toilet"
Building              = "Building"
Tree                  = "Tree"
Color                 = "Color"
