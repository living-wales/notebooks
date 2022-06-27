from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

class cultman_agr_cat(Transformation):
    """
    Generating cultivated ED layer
    """
    def compute(self, data):
        print("running VP: cultman_agr_cat")
        sklearn_cultivated_classification = data.isel(time=0)
        vegetat_veg_cat = data.isel(time=1).fillna(0)
        woody_cat = data.isel(time=2).fillna(0)
        cultman_veg = sklearn_cultivated_classification * vegetat_veg_cat
        cultman_veg_clean = cultman_veg - woody_cat
        cultman_bin = cultman_veg_clean.where(cultman_veg_clean == 2)*0+1
        print("done")
        return (cultman_bin)
    
    def measurements(self, input_measurements):
        return {'cultman_agr_cat': Measurement(name='cultman_agr_cat', dtype='float32', nodata=float('nan'), units='1')}
