from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

## Water classes
class s1_water(Transformation):
    """
    Generate a water product from Sentinel-1 ARD
    """
    def compute(self, data):
        print("s1_water...")
        numDates = data.VH.where(data.VH !=0).count(dim='time')
        watper = data.VH.where(data.VH < -22.).count(dim='time')
        watper_mths = watper / numDates *12
        water_bin = watper_mths.where(watper_mths > 8)*0+1
        print("done")
        return (water_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'s1_water': Measurement(name='s1_water', dtype='float32', nodata=float('nan'), units='1')}

    
class water(Transformation):
    """
    Combining water products into a water layer
    """
    def compute(self, data):
        print("water...")
        data_combined = data.sum(dim="time")
        water = data_combined.where(data_combined > 0)*0+1
        print("done")
        return (water)
    
    def measurements(self, input_measurements):
        return {'water': Measurement(name='water', dtype='float32', nodata=float('nan'), units='1')}
