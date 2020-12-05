# Project Proposal

## An open source Tethys Web App for infiltration modeling

Calculating curve numbers is something that either takes ArcGIS experience or the back-and-forth use of spreadsheets and GIS. I propose an app which allows the user to calculate curve numbers and percent impervious for a group of subwatersheds to make the SCS curve number method even faster and simpler.

## Background

While learning how to use XP-SWMM, a stormwater modeling software, one of the first things I was tasked with was routing a system of subwatersheds and assigning each subwatershed a weighted curve number. My coworkers used a combination of ArcGIS and excel spreadsheets to calculate the weighted curve numbers and assign them to a subwatershed shapefile. Though this process can all be completed within ArcGIS, it is a long process for the simple curve number approach. It also requires the expensive spatial analyst extension.

To solve this problem, I propose to develop a Tethys web application to calculate curve numbers and assign them to subwatersheds all using open source GIS packages (geopandas, shapely, and fiona). The Tethys platform was designed by BYU to "lower the bar" needed to program web apps. It provides different GIS tools and resources specifically for water resources engineers to speed up the app making process. 

Within this infiltration app, the user would first either upload a shapefile with subwatershed polygons or draw subwatersheds on a map, then upload land cover and soil data polygons. The app would intersect the land cover polygons, soil data polygons, and subwatershed polygons to create subpolygons with unique combinations of landcover, percent impervious HSG, and subwatershed ID. A CN and area would be assigned to each subpolygon, and a new field with the product of the CN and area would be added. The subpolygons would be aggreated by subwatershed ID, and then a weighted curve number would be calculated for each subwatershed.


## Data and Parameters

A few shapefiles and parameters would be required by the web app:
1. Subwatersheds polygon shapefile and ID field (Optional)
2. Contours shapefile (Optional)
3. Land cover polygon shapefile and landuse field
4. Soil data polygon shapefile and hydrologic soil group field
5. Curve number classification by landcover and HSG (Optional)

## Limitations

1. Tethys apps only run on a Linux machine
2. The curve number method is not the most accurate infiltration method
3. It can be difficult to work with multiple projections, especially because openlayers usually requires EPSG:4326

## Solutions

1. The app can be produced on a Linux machine and hosted on a Linux server
2. Future versions of the app can include other infiltration methods
3. Explicitly convert each file to a known coordinate system and require a prj file
