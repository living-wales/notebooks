## wdc_datahandling.py

'''
Description: This file contains a set of python functions for handling
satellite data.
License: The code in this notebook is licensed under the Apache License,
Version 2.0 (https://www.apache.org/licenses/LICENSE-2.0). Aberystwyth
University data is licensed under the Creative Commons by Attribution 4.0
license (https://creativecommons.org/licenses/by/4.0/).
Contact: If you need assistance, please contact Richard Lucas or
Carole Planque from Aberystwyth University.

Functions included:
    array_to_geotiff
    download_unzip
    dilate
    pan_sharpen_brovey
    RSGISSharpenLowResImagery
Last modified: September 2021
'''

# Import required packages
import os
import gdal
import zipfile
import numexpr
import math
import requests
import warnings
import numpy as np
import pandas as pd
import xarray as xr
from scipy.ndimage import binary_dilation
from sklearn.linear_model import LinearRegression





def array_to_geotiff(fname, data, geo_transform, projection,
                     nodata_val=0, dtype=gdal.GDT_Float32):
    """
    Create a single band GeoTIFF file with data from an array.
    Because this works with simple arrays rather than xarray datasets
    from DEA, it requires geotransform info ("(upleft_x, x_size,
    x_rotation, upleft_y, y_rotation, y_size)") and projection data
    (in "WKT" format) for the output raster. These are typically
    obtained from an existing raster using the following GDAL calls:
        import gdal
        gdal_dataset = gdal.Open(raster_path)
        geotrans = gdal_dataset.GetGeoTransform()
        prj = gdal_dataset.GetProjection()
    ...or alternatively, directly from an xarray dataset:
        geotrans = xarraydataset.geobox.transform.to_gdal()
        prj = xarraydataset.geobox.crs.wkt
    Parameters
    ----------
    fname : str
        Output geotiff file path including extension
    data : numpy array
        Input array to export as a geotiff
    geo_transform : tuple
        Geotransform for output raster; e.g. "(upleft_x, x_size,
        x_rotation, upleft_y, y_rotation, y_size)"
    projection : str
        Projection for output raster (in "WKT" format)
    nodata_val : int, optional
        Value to convert to nodata in the output raster; default 0
    dtype : gdal dtype object, optional
        Optionally set the dtype of the output raster; can be
        useful when exporting an array of float or integer values.
        Defaults to gdal.GDT_Float32
    """

    # Set up driver
    driver = gdal.GetDriverByName('GTiff')

    # Create raster of given size and projection
    rows, cols = data.shape
    dataset = driver.Create(fname, cols, rows, 1, dtype)
    dataset.SetGeoTransform(geo_transform)
    dataset.SetProjection(projection)

    # Write data to array and set nodata values
    band = dataset.GetRasterBand(1)
    band.WriteArray(data)
    band.SetNoDataValue(nodata_val)

    # Close file
    dataset = None


def download_unzip(url,
                   output_dir=None,
                   remove_zip=True):
    """
    Downloads and unzips a .zip file from an external URL to a local
    directory.
    Parameters
    ----------
    url : str
        A string giving a URL path to the zip file you wish to download
        and unzip
    output_dir : str, optional
        An optional string giving the directory to unzip files into.
        Defaults to None, which will unzip files in the current working
        directory
    remove_zip : bool, optional
        An optional boolean indicating whether to remove the downloaded
        .zip file after files are unzipped. Defaults to True, which will
        delete the .zip file.
    """

    # Get basename for zip file
    zip_name = os.path.basename(url)

    # Raise exception if the file is not of type .zip
    if not zip_name.endswith('.zip'):
        raise ValueError(f'The URL provided does not point to a .zip '
                         f'file (e.g. {zip_name}). Please specify a '
                         f'URL path to a valid .zip file')

    # Download zip file
    print(f'Downloading {zip_name}')
    r = requests.get(url)
    with open(zip_name, 'wb') as f:
        f.write(r.content)

    # Extract into output_dir
    with zipfile.ZipFile(zip_name, 'r') as zip_ref:
        zip_ref.extractall(output_dir)
        print(f'Unzipping output files to: '
              f'{output_dir if output_dir else os.getcwd()}')

    # Optionally cleanup
    if remove_zip:
        os.remove(zip_name)


def dilate(array, dilation=10, invert=True):
    """
    Dilate a binary array by a specified nummber of pixels using a
    disk-like radial dilation.
    By default, invalid (e.g. False or 0) values are dilated. This is
    suitable for applications such as cloud masking (e.g. creating a
    buffer around cloudy or shadowed pixels). This functionality can
    be reversed by specifying `invert=False`.
    Parameters
    ----------
    array : array
        The binary array to dilate.
    dilation : int, optional
        An optional integer specifying the number of pixels to dilate
        by. Defaults to 10, which will dilate `array` by 10 pixels.
    invert : bool, optional
        An optional boolean specifying whether to invert the binary
        array prior to dilation. The default is True, which dilates the
        invalid values in the array (e.g. False or 0 values).
    Returns
    -------
    An array of the same shape as `array`, with valid data pixels
    dilated by the number of pixels specified by `dilation`.
    """

    y, x = np.ogrid[
        -dilation: (dilation + 1),
        -dilation: (dilation + 1),
    ]

    # disk-like radial dilation
    kernel = (x * x) + (y * y) <= (dilation + 0.5) ** 2

    # If invert=True, invert True values to False etc
    if invert:
        array = ~array

    return ~binary_dilation(array.astype(np.bool),
                            structure=kernel.reshape((1,) + kernel.shape))


def pan_sharpen_brovey(band_1, band_2, band_3, pan_band):
    """
    Brovey pan sharpening on surface reflectance input using numexpr
    and return three xarrays.
    Parameters
    ----------
    band_1, band_2, band_3 : xarray.DataArray or numpy.array
        Three input multispectral bands, either as xarray.DataArrays or
        numpy.arrays. These bands should have already been resampled to
        the spatial resolution of the panchromatic band.
    pan_band : xarray.DataArray or numpy.array
        A panchromatic band corresponding to the above multispectral
        bands that will be used to pan-sharpen the data.
    Returns
    -------
    band_1_sharpen, band_2_sharpen, band_3_sharpen : numpy.arrays
        Three numpy arrays equivelent to `band_1`, `band_2` and `band_3`
        pan-sharpened to the spatial resolution of `pan_band`.
    """
    # Calculate total
    exp = 'band_1 + band_2 + band_3'
    total = numexpr.evaluate(exp)

    # Perform Brovey Transform in form of: band/total*panchromatic
    exp = 'a/b*c'
    band_1_sharpen = numexpr.evaluate(exp, local_dict={'a': band_1,
                                                       'b': total,
                                                       'c': pan_band})
    band_2_sharpen = numexpr.evaluate(exp, local_dict={'a': band_2,
                                                       'b': total,
                                                       'c': pan_band})
    band_3_sharpen = numexpr.evaluate(exp, local_dict={'a': band_3,
                                                       'b': total,
                                                       'c': pan_band})

    return band_1_sharpen, band_2_sharpen, band_3_sharpen


def RSGISSharpenLowResImagery(dataset, loRes=None, hiRes=None, WinSize=7):
    """
    RGISLib pan sharpening on surface reflectance input.
    Parameters
    ----------
    dataset : xarray.Dataset of dimensions latitude*longitude containing
        the high resolution and low resolution bands
    loRes : list of the name(s) of the low resolution bands to pan-sharpen
    hiRes : list of the name(s) of the high resolution bands that will be
        used to pan-sharpen the data.
    WinSize : integer, which must be an odd number, specifying the window
        size (in pixels) used for the analysis (Default = 7). Recommend that
        the window size values fits at least 9 low resolution image pixels.
        For example, if the high resolution image is 10 m and the low 20 m
        then a 7 x 7 window will include 12.25 low resolution pixels.
    Returns
    -------
    panSharped : xarray.Dataset of dimensions latitude*longitude containing
        the same bands as dataset (input) but with low resolution bands
        pansharped to the resolution of the high resolution bands.
    """
    
    def get_pixels(a,b):
        return a,b
    
    def window(data, pixelX, pixelY, WinSize):
        Xmin = pixelX - math.trunc(WinSize/2)
        Xmax = pixelX + math.trunc(WinSize/2) + 1
        Ymin = pixelY - math.trunc(WinSize/2)
        Ymax = pixelY + math.trunc(WinSize/2) + 1
        datapx = data[Ymin:Ymax,Xmin:Xmax]
        return datapx
    
    def test_regr_coeff(highBand):
        X = window(data=dataset[highBand], pixelX=x, pixelY=y, WinSize=WinSize)
        Y = window(data=dataset[lowBand], pixelX=x, pixelY=y, WinSize=WinSize)
        X = np.array(X).reshape(-1, 1)
        Y = np.array(Y).reshape(-1, 1)
        regr = LinearRegression() 
        regr.fit(X, Y)
        train_score = regr.score(X, Y)
        return train_score
    
    def apply_regr(xy_coord):
        global x
        global y
        y = xy_coord[0]
        x = xy_coord[1]
        WinSize_test = window(data=dataset[lowBand], pixelX=x, pixelY=y, WinSize=WinSize)
        if (WinSize_test.shape[0]==WinSize and WinSize_test.shape[1]==WinSize):
            coeffs = list(map(test_regr_coeff, hiRes))
            largest_coeff = max(coeffs)
            bandHigh_index = coeffs.index(largest_coeff)
            bandHigh_pan = hiRes[bandHigh_index]
            X = window(data=dataset[bandHigh_pan], pixelX=x, pixelY=y, WinSize=WinSize)
            Y = window(data=dataset[lowBand], pixelX=x, pixelY=y, WinSize=WinSize)
            X = np.array(X).reshape(-1, 1)
            Y = np.array(Y).reshape(-1, 1)
            regr = LinearRegression() 
            regr.fit(X, Y)
            train_score = regr.score(X, Y)
            # In RGISLib regr.score must be > 0.5,
            # this was removed in the DC version of the pan-sharpening
            #if train_score > 0.5:
            loPx_pan = regr.predict(X)
            center = math.trunc(X.shape[0]/2)
            panSharped[lowBand][y,x] = loPx_pan[center,0]
            #else:
            #    panSharped[lowBand][y,x] = dataset[lowBand][y,x]
        else:
            panSharped[lowBand][y,x] = dataset[lowBand][y,x]
       
    if loRes is None:
        
        raise ValueError("List of the low resolution band(s) to pan-sharp is required.")
    
    elif hiRes is None:
        
        raise ValueError("List of the high resolution band(s) to use for pan-sharpening is required.")
    
    elif (WinSize % 2) == 0:
        raise ValueError("WinSize must be an odd integer.")
    
    elif isinstance(dataset, xr.Dataset):
        
        panSharped = dataset.copy(deep=True)
        dimData = panSharped[loRes[0]].shape
        yList = list(range(0,dimData[0])) * dimData[1]
        xList = sorted(list(range(0,dimData[1])) * dimData[0])
        coord = list(map(get_pixels, yList, xList))
        for lowBand in loRes:
            testMap = list(map(apply_regr, coord))
    
    else:
        
        raise ValueError(f"Verify that your input data is a xarray.Dataset and "
                         "low and high resolution bands are within the dataset. \n"
                         "Please refer to the function documentation to verify your parameters \n"
                         "meet all the format requirements.")
    
    return panSharped