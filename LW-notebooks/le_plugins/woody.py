from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

class s1_woody(Transformation):
    """
    Generate an woody product from Sentinel-1 ARD
    """
    def compute(self, data):
        data_combined = data.sum(dim="time")
        s1_woody = data_combined.where(data_combined > 0)*0+1
        return (s1_woody)
    
    def measurements(self, input_measurements):
        return {'s1_woody': Measurement(name='s1_woody', dtype='float32', nodata=float('nan'), units='1')}


class woody_s1_cat(Transformation):
    """
    Cleaning the Sentinel1-based woody product
    """
    def compute(self, data):
        s1_woody = data.isel(time=0)
        vegetat_veg_cat = data.isel(time=1).fillna(0)
        woody_s1_clean = s1_woody * vegetat_veg_cat
        woody_s1_bin = woody_s1_clean.where(woody_s1_clean > 0)*0+1
        return (woody_s1_bin)
    
    def measurements(self, input_measurements):
        return {'woody_s1_cat': Measurement(name='woody_s1_cat', dtype='float32', nodata=float('nan'), units='1')}


class woody_nfi(Transformation):
    """
    Creating woody mask from NFI woodland types.
    """
    def compute(self, data):
        data = data.squeeze(dim='time').drop_vars('time')
        woody = data.type.where((data.type > 0) & (data.type <= 4))
        woody_nfi_bin = woody.where(woody > 0)*0+1
        return (woody_nfi_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'woody_nfi': Measurement(name='woody_nfi', dtype='float32', nodata=float('nan'), units='1')}
    

class clear_cuts_s2(Transformation):
    """
    Generating a non-woody product from Sentinel-2 ARD
    """
    def compute(self, data):
        print("running VP: clear_cuts_s2")
        s2_mar_oct = data.where((data.time.dt.month >= 4) & 
                                (data.time.dt.month <= 10), 
                                drop=True)
        s2_mar_oct["ndvi"] = (s2_mar_oct.nir - s2_mar_oct.red) / (s2_mar_oct.nir + s2_mar_oct.red)
        mean_ndvi = s2_mar_oct.ndvi.mean(dim='time')
        non_woody_ndvi_bin = mean_ndvi.where(mean_ndvi <= (0.5))*0+1
        return (non_woody_ndvi_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'clear_cuts_s2': Measurement(name='clear_cuts_s2', dtype='float32', nodata=float('nan'), units='1')}


class woody_cat(Transformation):
    """
    Combining woody products into a woody layer
    """
    def compute(self, data):
        print("running VP: woody_cat")
        woody_s1_cat = data.isel(time=0).fillna(0)
        woody_nfi = data.isel(time=1).fillna(0)
        clear_cuts_s2 = data.isel(time=2)
        woody = woody_s1_cat + woody_nfi
        woody_clean = woody.where(clear_cuts_s2!=1)
        woody_clean_bin = woody_clean.where(woody_clean > 0)*0+1
        print("done")
        return (woody_clean_bin)
    
    def measurements(self, input_measurements):
        return {'woody_cat': Measurement(name='woody_cat', dtype='float32', nodata=float('nan'), units='1')}
