# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 12:46:15 2025

@author: coline.mathias
"""

import os # This is is needed in the pyqgis console also
import urllib
import pathlib
from qgis.core import (
    QgsVectorLayer, QgsVectorFileWriter
)

# set QGIS path prefix
qgis_prefix = r"C:\Program Files\QGIS 3.34.14\apps\qgis-ltr"
QgsApplication.setPrefixPath(qgis_prefix, True) 
QgsApplication.initQgis()

project = QgsProject.instance()

# %%
def load_delimtext(path, delim, latfield, lonfield, use_header=True, crs='EPSG:4326', skiplines=0):
    """
    Load delimited text vector layer.
    path : str
        Path of the file to load
    delim: str 
        Column delimiter
    latfield : str
        Field containing latitude data
    lonfield : str
        Field containing longitude data
    use_header: bool, default True
        Names of the fields are included in the first line of the file
    crs: str, 'EPSG:' + EPSG code
        EPSG code defining layer's CRS
    skiplines: int, default 0
        Lines to skip at the top of the file.
    """
    if not use_header:
        useheader = 'No'
    else:
        useheader='Yes'
        
    abspath = os.path.abspath(path)
    params = {'detectTypes':'yes',
            'xField': lonfield,
            'delimiter': delim,
            'yField': latfield,
            'crs':crs,
            'skipLines':skiplines
            }
              
    # encode path as readable by QGIS
    uri = "%s?%s" %(pathlib.Path(abspath).as_uri(),
                    urllib.parse.unquote(urllib.parse.urlencode(params)))
                
    return QgsVectorLayer(uri, "Deployment_points", "delimitedtext")


def save_csv(layer, output_file, fields=[]):
    """ 
    Save vector layer as csv file. Specify fields in var fields, empty means all
    attributes will be exported
    """
    #define saving options (fields to export + type of file)
    sav_opt = QgsVectorFileWriter.SaveVectorOptions()
    attrib = [sampled_layer.fields().indexFromName(f) for f in fields]
    sav_opt.attributes=attrib
    sav_opt.driverName = 'CSV'
    QgsVectorFileWriter.writeAsVectorFormatV3(sampled['OUTPUT'],
                                            output_file,
                                            project.transformContext(),
                                            sav_opt)

#%%
#import layers
# #### USER DEFINED : fill in your paths here
path_pts = r'\\jalapeno\Projects\ESB-Malin Sea WF\00 - Project Management\Maps\QGIS\Spatial Data\ESB_Malin_Deployment_Locations.csv'
path_bathy = r'\\jalapeno\Projects\ESB-Malin Sea WF\00 - Project Management\Maps\QGIS\Spatial Data\GEBCO_Bathymetry.tif'
output_file = path_pts.replace('.csv', '_with_depths.csv')

fields_to_export = ['field_1', 'Latitude', 'Longitude', 'depth_1']

layer_pts = load_delimtext(path_pts, ',', 'latitude', 'longitude', skiplines=1)
# ####

project.addMapLayer(layer_pts)
layer_ras = QgsRasterLayer(path_bathy, path_bathy.split('\\')[-1].replace('.tif', '')
project.addMapLayer(layer_ras)

# %% sampling
sampled = processing.run("native:rastersampling",
                        {'INPUT': layer_pts,
                        'RASTERCOPY': layer_ras,
                        'COLUMN_PREFIX':'depth_',
                        'OUTPUT':'TEMPORARY_OUTPUT'})

if not(sampled):
    print('/!\ Sampling failed')
else:
    print(sampled)
    sampled_layer = sampled['OUTPUT']
    project.addMapLayer(sampled_layer)
    # save layer to csv
    save_csv(sampled_layer, output_file,
            fields_to_export)