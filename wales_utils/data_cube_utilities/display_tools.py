import numpy as np
import math
from pyproj import Proj, transform
from ipyleaflet import (
    Map,
    basemaps,
    basemap_to_tiles,
    LayersControl,
    Rectangle
)
from ipywidgets import Layout

def _degree_to_zoom_level(l1, l2, margin = 0.0):
    
    degree = abs(l1 - l2) * (1 + margin)
    zoom_level_int = 0
    if degree != 0:
        zoom_level_float = math.log(360/degree)/math.log(2)
        zoom_level_int = int(zoom_level_float)
    else:
        zoom_level_int = 18
    return zoom_level_int


def map_extent(extent = None):
    """
    Description:
      Takes the latitude/longitude (EPSG:27700, i.e., official wales projection system) 
      of an area and create a map service backgroup with a red rectangle of given lat/lon.
    -----
    Input:
      extent: tuple with (min_lon, min_lat, max_lon, max_lat)
    Output:
      m: the background map/service provided by ipyleaflet
      dc: draw control
    """
    
    # check options combination
    assert not(extent is None), \
           'lat_ext and lon_ext are required'
    assert extent[1] < extent[3], 'extent values are in the wrong order must be (min_lon, min_lat, max_lon, max_lat)'
    assert extent[0] < extent[2], 'extent values are in the wrong order must be (min_lon, min_lat, max_lon, max_lat)'
    
    # reproject extent from national system to WGS84
    training_inProj = Proj(init='EPSG:27700')
    training_outProj = Proj(init='EPSG:4326')
    min_lon,min_lat = transform(training_inProj,training_outProj,extent[0],extent[1])
    max_lon,max_lat = transform(training_inProj,training_outProj,extent[2],extent[3])
    
    lat_ext = (min_lat, max_lat)
    lon_ext = (min_lon, max_lon)
    
    # Location
    center = [np.mean(lat_ext), np.mean(lon_ext)]

    # create a basemap background (Open Street Map background) for the area
    margin = 0
    zoom_bias = 2
    lat_zoom_level = _degree_to_zoom_level(margin = margin, *lat_ext ) + zoom_bias
    lon_zoom_level = _degree_to_zoom_level(margin = margin, *lon_ext) + zoom_bias
    zoom = min(lat_zoom_level, lon_zoom_level)

    m = Map(center=center, zoom=zoom, scroll_wheel_zoom = True,
       layout=Layout(width='800px', height='800px'))
    
    # add other basemaps to the background
    # ESRI satellite imagy
    esri = basemap_to_tiles(basemaps.Esri.WorldImagery)
    m.add_layer(esri)

    # add red rectangle with extent of the ROI
    rectangle = Rectangle(bounds = ((lat_ext[0], lon_ext[0]),
                                   (lat_ext[1], lon_ext[1])),
                          color = 'red', weight = 2, fill = False)

    m.add_layer(rectangle)
    m.add_control(LayersControl())

    return m
