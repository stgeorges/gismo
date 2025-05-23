![Logo](https://github.com/stgeorges/gismo/blob/master/resources/images/gismo_logo.png)

# Gismo
Gismo is a free and open source Grasshopper plugin for GIS environmental analysis.



# Description:
Gismo enables automatic generation of 2D and 3D urban environment and terrain geometry based on location's latitude-longitude coordinates/or address and radius. This includes connection with openstreetmap and opentopography websites and generation of buildings, terrain, trees, roads, rivers and other map elements - based only on upper two inputs.

Additionally Gismo posseses the following functionalities:
Air pollution analysis, tree CO2 sequestering, greenness index analysis, terrain and water flow analysis, terrain shading mask creation and its export to climate and PV software (Meteonorm, PV*SOL, PVsyst).

<p align="center">
  <img src="https://github.com/stgeorges/gismo/blob/master/resources/images/gismo_components_tabs.png" width="350"/>
</p>

<p align="center">
  <img src="https://github.com/stgeorges/gismo/blob/master/resources/images/3D_Acropolis.jpg" width="350"/>
</p>

[* more screenshots...](https://github.com/stgeorges/gismo/tree/master/resources/images)



# Requirements:

- McNeel [Rhino 5](http://www.rhino3d.com/download/rhino/5/latest) or [Rhino 6](https://www.rhino3d.com/download/rhino-for-windows/6/latest) or [Rhino 7](https://www.rhino3d.com/download/rhino-for-windows/evaluation) or [Rhino 8](https://www.rhino3d.com/download/rhino-for-windows/evaluation).
- [MapWinGIS v4.9.6.1 x64](https://github.com/MapWindow/MapWinGIS/releases/download/v4.9.6.0/MapWinGIS-only-v4.9.6.1-x64.exe)
- Active internet connection.



# Installation
- 1) Install the upper mentioned requirements (Rhino 5/6/7/8, Grasshopper, Ghpython, MapWinGIS).
  Always unblock the ```MapWinGIS-only-v4.9.6.1-x64.exe``` file after download!!! (right click on it, and check ```Unblock```).
- 2) Download the latest Gismo plugin files as a single .zip file from here:
https://github.com/stgeorges/gismo/zipball/master
- 3) Check if downloaded .zip file has been blocked: right click on it, and choose ```Properties```. If there is an ```Unblock``` button click on it, and then click on ```OK```. If there is no ```Unblock``` button, just click on ```OK```.
- 4) Unpack the .zip file.
- 5) Copy the content from ```userObjects``` folder to your Grasshopper's: ```File->Special Folders->User Object Folder``` folder.



# Additional info
- [Discussion group](http://www.grasshopper3d.com/group/gismo)
- [Facebook](https://www.facebook.com/GismoTools)
- [Twitter](https://twitter.com/gismo_tools)

Gismo is heavily influenced by [Ladybug](https://github.com/mostaphaRoudsari/ladybug) a free and open source environmental plugin for Grasshopper. It is using its code template, and follows the Labybug code organization. Some methods from Ladybug may have also been copied.

Gismo is [licensed](https://github.com/stgeorges/gismo/blob/master/LICENSE.md) under GPL-3.0+ license: <http://spdx.org/licenses/GPL-3.0+

The latest version is 0.0.3.


# Contributors
[Antonello Di Nunzio](https://github.com/AntonelloDN)

[Djordje Spasic](https://github.com/stgeorges)

[Guillaume Meunier](https://github.com/Alliages)

[Mathieu Venot](https://github.com/MathieuVenot)

Support on various issues and questions has been given by: Alec Bennett, Andrew T. Young, Bojan Savric, Christopher Crosby, Dragan Milenkovic, Even Rouault, Graham Dawson, Izabela Spasic, Jonathan de Ferranti, Jukka Rahkonen, Menno Deij-van Rijswijk, Michal Migurski, Mostapha Sadeghipour Roudsari, Paul Meems, Sergei Leschinsky, Timothy Logan, Ulrich Deuschle, Vladimir Elistratov, OSM and GDAL communities.
