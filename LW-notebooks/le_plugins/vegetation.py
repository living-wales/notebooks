from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

## Vegetation classes
class s2_veg(Transformation):
    """
    Generate a vegetated/non-vegetated product from Sentinel-2 ARD
    """
    def compute(self, data):
        print("running VP: s2_veg")
        s2_apr_oct = data.where((data.time.dt.month >= 4) & 
                                (data.time.dt.month <= 10), 
                                drop=True)
        s2_apr_oct["ndvi"] = (s2_apr_oct.nir - s2_apr_oct.red) / (s2_apr_oct.nir + s2_apr_oct.red)
        max_apr_oct_ndvi = s2_apr_oct.ndvi.max(dim='time')
        veg_ndvi_bin = max_apr_oct_ndvi.where(max_apr_oct_ndvi > (0.4))*0+1
        print("done")
        return (veg_ndvi_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'s2_veg': Measurement(name='s2_veg', dtype='float32', nodata=float('nan'), units='1')}
