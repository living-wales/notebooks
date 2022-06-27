from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

class s1_ard(Transformation):
    """
    Prepare S1 data into ARD format (nodata masked)
    """
    def compute(self, data):
        data_clean = data.where(data != 0)
        return (data_clean)
    
    def measurements(self, input_measurements):
        return {'s1_ard': Measurement(name='s1_ard', dtype='float32', nodata=float('nan'), units='1')}
