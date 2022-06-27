from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

class water_cat(Transformation):
    """
    Combining water products into a water layer
    """
    def compute(self, data):
        print("running VP: water_cat")
        water = data.isel(time=0).fillna(0)
        artific_urb_cat = data.isel(time=1).fillna(0)
        water_clean = water - artific_urb_cat
        water_clean_bin = water_clean.where(water_clean > 0)*0+1
        print("done")
        return (water_clean_bin)
    
    def measurements(self, input_measurements):
        return {'water_cat': Measurement(name='water_cat', dtype='float32', nodata=float('nan'), units='1')}
