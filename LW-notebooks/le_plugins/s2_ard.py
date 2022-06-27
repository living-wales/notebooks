from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

# ARD recipes 
class s2_ard(Transformation):
    """
    Prepare S2_L2A data into ARD format (real reflectance values & nodata and cloud masked)
    """
    def compute(self, data):
        data_clean = data.where((data.scl == 4) | (data.scl == 5) | 
                                (data.scl == 6) | (data.scl == 7) | 
                                (data.scl == 11))
        data_clean = data_clean.drop('scl')
        return (data_clean/10000)
    
    def measurements(self, input_measurements):
        return {'s2_ard': Measurement(name='s2_ard', dtype='float32', nodata=float('nan'), units='1')}
