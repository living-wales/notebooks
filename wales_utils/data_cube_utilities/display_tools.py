import numpy as np
import math
from pyproj import Proj, transform
from ipyleaflet import (
    Map,
    basemaps,
    basemap_to_tiles,
    ImageOverlay,
    LayersControl,
    Rectangle
)
from ipywidgets import Layout
from PIL import Image
import matplotlib.cm as mcm
from io import BytesIO
from base64 import b64encode
import rioxarray


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


def da_to_png64(da, cm):
    """
    Description:
      Takes a 2D (latitude/longitude) xarray and create a png image using a matplotlib color scheme.
    -----
    Input:
      da: an xarray of dim latitude/longitude
      cm: str indicating a matplotlib colormap
    Output:
      imgurl: image URL 
    """    
    arr = da.values
    
    # colorise xarray
    colorise = "mcm."+cm+"(arr)"
    arr_colorised = eval(colorise)
    
    # create image from xarray
    arr_im = Image.fromarray(np.uint8(arr_colorised*255))
    im = Image.new('RGBA', arr.shape[::-1], color=None)
    im.paste(arr_im)
    
    # save image to png
    f = BytesIO()
    im.save(f, 'png')
    data = b64encode(f.getvalue())
    data = data.decode('ascii')
    
    # create image URL from PNG_64
    imgurl = 'data:image/png;base64,' + data
    
    return imgurl


def display_da(da, colormap):
    """
    Description:
      Display a colored xarray.DataArray on a map service backgroup
    -----
    Input:
      da: xarray.DataArray
      colormap: str indicating a matplotlib colormap
    Output:
      m: map to interact with
    """

    # Check inputs
    assert 'dataarray.DataArray' in str(type(da)), "da must be an xarray.DataArray"
    if (str(da.rio.crs) != 'EPSG:4326'):
        da = da.rio.reproject("EPSG:4326")
    
    if (da.attrs['_FillValue'] > 0):
        da = da.where(da < da.attrs['_FillValue'])
    else:
        da = da.where(da > da.attrs['_FillValue'])

    
    latitude = (float(da.y.min().values), float(da.y.max().values))
    longitude = (float(da.x.min().values), float(da.x.max().values))
    
    # convert DataArray to png64
    imgurl = da_to_png64(da, colormap)

    
    # Location
    center = [np.mean(latitude), np.mean(longitude)]

    # create a basemap background (Open Street Map background) for the area
    margin = 0
    zoom_bias = 2
    lat_zoom_level = _degree_to_zoom_level(margin = margin, *latitude ) + zoom_bias
    lon_zoom_level = _degree_to_zoom_level(margin = margin, *longitude) + zoom_bias
    zoom = min(lat_zoom_level, lon_zoom_level)

    m = Map(center=center, zoom=zoom, scroll_wheel_zoom = True,
       layout=Layout(width='800px', height='800px'))
    
    # add other basemaps to the background
    # ESRI satellite imagy
    esri = basemap_to_tiles(basemaps.Esri.WorldImagery)
    m.add_layer(esri)

    io = ImageOverlay(name = 'DataArray', url=imgurl, bounds=[(latitude[0],longitude[0]),(latitude[1], longitude[1])])
    m.add_layer(io)

    m.add_control(LayersControl())

    return m

