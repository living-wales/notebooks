from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

class vegetat_veg_cat(Transformation):
    """
    Cleaning vegetation product in order to produce the vegetated/non-vegetated ED layer
    """
    def compute(self, data):
        print("running VP: vegetat_veg_cat")
        s2_veg = data.isel(time=0)
        water_cat = data.isel(time=1).fillna(0)
        artific_urb_cat = data.isel(time=2).fillna(0)
        veg_clean = s2_veg - water_cat - artific_urb_cat
        veg_bin = veg_clean.where(veg_clean > 0)*0+1
        print("done")
        return (veg_bin)
    
    def measurements(self, input_measurements):
        return {'vegetat_veg_cat': Measurement(name='vegetat_veg_cat', dtype='float32', nodata=float('nan'), units='1')}
