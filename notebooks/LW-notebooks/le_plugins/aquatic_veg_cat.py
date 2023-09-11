from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask


class aquatic_peats(Transformation):
    """
    Creating peat mask from WG Unified peat map.
    """
    def compute(self, data):
        data = data.squeeze(dim='time').drop_vars('time')
        peats = data.peats.where(data.peats > 0)
        peats_bin = peats.where(peats > 0)*0+1
        return (peats_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'aquatic_peats': Measurement(name='aquatic_peats', dtype='float32', nodata=float('nan'), units='1')}

class aquatic_saltmarshes(Transformation):
    """
    Creating saltmarsh mask from NRW saltmarsh map.
    """
    def compute(self, data):
        data = data.squeeze(dim='time').drop_vars('time')
        saltmarshes = data.saltmarshes.where(data.saltmarshes > 0)
        saltmarshes_bin = saltmarshes.where(saltmarshes > 0)*0+1
        return (saltmarshes_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'aquatic_saltmarshes': Measurement(name='aquatic_saltmarshes', dtype='float32', nodata=float('nan'), units='1')}

# class aquatic_vegetation(Transformation):
#     """
#     Combining 5species, peat and saltmarsh products to build an aquatic vegetation layer
#     """
#     def compute(self, data):
#         species5 = data[0]
#         peats = data[1]
#         salmarshes = data[2]
#         aquatic_sp = species5.where((species5 == 2) | (species5 == 4))
#         heather_bog = species5.where((species5 == 3) & (peats == 1))
#         aqu_veg = aquatic_sp.fillna(0) + heather_bog.fillna(0) + salmarshes.fillna(0)
#         aqu_veg_bin = aqu_veg.where(aqu_veg > 0)*0+1
#         return (aqu_veg_bin)
    
#     def measurements(self, input_measurements):
#         return {'aquatic_vegetation': Measurement(name='aquatic_vegetation', dtype='float32', nodata=float('nan'), units='1')}

class aquatic_veg_cat(Transformation):
    """
    Creating saltmarsh mask from NRW saltmarsh map.
    """
    def compute(self, data):
        print("running VP: aquatic_veg_cat")
        #aquatic_vegetation
        species5 = data.isel(time=0)
        peats = data.isel(time=1)
        salmarshes = data.isel(time=2)
        aquatic_sp = species5.where((species5 == 2) | (species5 == 4))
        heather_bog = species5.where((species5 == 3) & (peats == 1))
        aqu_veg = aquatic_sp.fillna(0) + heather_bog.fillna(0) + salmarshes.fillna(0)
        aquatic_vegetation = aqu_veg.where(aqu_veg > 0)*0+1
        
        #aquatic_veg_cat
        #aquatic_vegetation = data[0]
        vegetat_veg_cat = data.isel(time=3).fillna(0)
        woody_cat =data.isel(time=4).fillna(0)
        cultman_agr_cat = data.isel(time=5).fillna(0)
        aqu_veg = (aquatic_vegetation * vegetat_veg_cat) - woody_cat - cultman_agr_cat
        aqu_veg_bin = aqu_veg.where(aqu_veg > 0)*0+1
        print("done")
        return (aqu_veg_bin)
    
    def measurements(self, input_measurements):
        return {'aquatic_veg_cat': Measurement(name='aquatic_veg_cat', dtype='float32', nodata=float('nan'), units='1')}
