QGIS Polygon Splitting
--------------------------------------

QGIS 3 script to split a polygon into sub-polygons of more-or-less equal areas

![QGIS Polygon Splitting Model](QGISPolygonSplitting.png)

Based on Paul Ramsey's post "PostGIS Polygon Splitting": http://blog.cleverelephant.ca/2018/06/polygon-splitting.html

### How to install the script

Just copy the QGISPolygonSplitting.py to the scripts folder, inside your QGIS3 profile folder (https://docs.qgis.org/testing/en/docs/user_manual/introduction/qgis_configuration.html#working-with-user-profiles) -> processing -> scripts. 

On Windows, scripts folder should be in the path: C:\Users\YourUser\AppData\Roaming\QGIS\QGIS3\profiles\YourProfile\processing\scripts.

The easiest way to find your profile folder is, start QGIS, go to Settings -> User Profiles -> Open Active Profile Folder.

### How to use the script

 * Split one polygon from a layer:
 
![Split one polygon from a layer](split_one_polygon.gif)

 * Split all polygons from a layer:
 
![Split all polygons from a layer](split_all_polygons.gif)
