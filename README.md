![Logo](https://github.com/stgeorges/gismo/blob/master/resources/images/gismo_logo.png)

# Gismo
Gismo is a free and open source Grasshopper plugin for GIS environmental analysis.



# Description:
Gismo enables automatic generation of urban environment and terrain geometry based on location's latitude-longitude coordinates and radius. This includes connection with openstreetmap website and generation of buildings, trees, roads, rivers and other map elements. 3d building elements can also be used as a context for further analysis types: isovist (visibility), solar radiation, thermal/wind comfort, cfd analysis...


<p align="center">
  <img src="https://github.com/stgeorges/gismo/blob/master/resources/images/3D_Acropolis.jpg" width="350"/>
</p>

[more screemshots...](https://github.com/stgeorges/gismo/tree/master/resources/images)



# Requirements:

- McNeel [Rhinoceros 5](http://www.rhino3d.com/download/rhino/5/latest) 32bit or 64bit SR9 or higher .
- [Grasshopper](http://www.rhino3d.com/download/grasshopper/1.0/wip) 0.9.0075 or 0.9.0076.
- [Ghpython](http://www.food4rhino.com/app/ghpython) plugin 0.6.0.3
- [MapWinGIS](https://github.com/MapWindow/MapWinGIS/releases) 32bit or 64bit 4.9.4.2 or higher
- Active internet connection.



# Installation
- 1) Install the upper mentioned requirements (Rhino 5, Grasshopper, Ghpython, MapWinGIS).
- 2) Download the latest Gismo plugin files as a single .zip file from here:
https://github.com/stgeorges/gismo/zipball/master
- 3) Check if downloaded .zip file has been blocked: right click on it, and choose "Properties". If there is an "Unblock" button click on it, and then click on "OK". If there is no "Unblock" button, just click on "OK".
- 4) Unpack the .zip file.
- 5) Copy the content of its "userObjects" folder file into your Grasshopper's: "File->Special Folders->User Object Folder" folder.



# Additional info
- [Discussion group](http://www.grasshopper3d.com/group/gismo)
- [Facebook](https://www.facebook.com/GismoTools)
- [Twitter](https://www.twitter.com/gismo_tools)

Gismo is heavily influenced by [Ladybug](https://github.com/mostaphaRoudsari/ladybug) a free and open source environmental plugin for Grasshopper. It is using its code template, and follows the Labybug code organization. Some methods from Ladybug may have also been copied.
Gismo is [licensed](https://github.com/stgeorges/gismo/blob/master/LICENSE.md) under GPL-3.0+ license: <http://spdx.org/licenses/GPL-3.0+>



# Contributors
[Djordje Spasic](https://github.com/stgeorges)

Support on various issues and questions has been given by: Alec Bennett, Andrew T. Young, Christopher Crosby, Dragan Milenkovic, Even Rouault, Graham Dawson, Izabela Spasic, Jonathan de Ferranti, Menno Deij-van Rijswijk, Michal Migurski, Mostapha Sadeghipour Roudsari, Paul Meems, Ulrich Deuschle, Vladimir Elistratov, OSM and GDAL communities.
