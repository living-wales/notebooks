from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

class aquatic_wat_cat(Transformation):
    """
    Creating aquatic layer.
    """
    def compute(self, data):
        print("running VP: aquatic_wat_cat")
        water_cat = data.isel(time=0).fillna(0)
        aquatic_veg_cat = data.isel(time=1).fillna(0)
        aquatic = water_cat + aquatic_veg_cat
        aquatic_bin = aquatic.where(aquatic > 0)*0+1
        print("done")
        return (aquatic_bin)
    
    def measurements(self, input_measurements):
        return {'aquatic_wat_cat': Measurement(name='aquatic_wat_cat', dtype='float32', nodata=float('nan'), units='1')}

    
class le_aquatic_wat_cat(Transformation):
    """
    Renaming aquatic_wat_cat dataset's measurement name
    """
    def compute(self, data):
        print("USING aquatic_wat_cat in LivingEarth...")
        aquatic_wat_cat_dataset = data.rename(name_dict={"band":"aquatic_wat_cat"})
        aquatic_wat_cat_dataset = aquatic_wat_cat_dataset.fillna(0)
        return (aquatic_wat_cat_dataset)
    
    def measurements(self, input_measurements):
        return {'aquatic_wat_cat': Measurement(name='aquatic_wat_cat', dtype='float32', nodata=float('nan'), units='1')}
