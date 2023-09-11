from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

class lifeform_veg_cat(Transformation):
    """
    Combining woody products into a woody layer
    """
    def compute(self, data):
        woody_cat = data.isel(time=0).fillna(0)
        vegetat_veg_cat = data.isel(time=1).fillna(0)
        lifeform = (woody_cat.where(woody_cat >= 1)*0+1).fillna(0) + (
            vegetat_veg_cat.where((vegetat_veg_cat > 0) & (woody_cat < 1))*0+2).fillna(0)
        return (lifeform)
    
    def measurements(self, input_measurements):
        return {'lifeform_veg_cat': Measurement(name='lifeform_veg_cat', dtype='float32', nodata=float('nan'), units='1')}
