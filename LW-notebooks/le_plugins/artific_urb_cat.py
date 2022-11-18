from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask

def osm_artif_features(query):
    from datetime import datetime
    import datacube
    dc = datacube.Datacube()
    
    dataset_osm = dc.load(**query,
                             dask_chunks={'time': 1, 'x': 4000, 'y': 4000})    
    dataset_osm = dataset_osm.isel(time=0)
    valid_road_codes = [5111, #motorway
                        5112, #trunk
                        5113, #primary
                        5114, #secondary
                        5115, #tertiary
                        5121, #unclassified
                        5122, #residential
                        5123, #living_street
                        5131, #motorway_link
                        5132, #trunk_link
                        5133, #primary_link
                        5134, #secondary_link
                        5135, #tertiary_link
                        5141, #service
                        5152] #cycleway
    valid_roads = dataset_osm.roads.where(dataset_osm.roads.isin(valid_road_codes))
    valid_roads_bin = dataset_osm.roads.where(valid_roads>0)*0+1
    #railways = dataset_osm.railways.where(dataset_osm.railways>0)*0+1
    buildings = dataset_osm.buildings.where(dataset_osm.buildings>0)*0+1
    #art_osm = valid_roads_bin.fillna(0) + railways.fillna(0) + buildings.fillna(0)
    art_osm = valid_roads_bin.fillna(0) + buildings.fillna(0)
    art_osm = (art_osm.where(art_osm > 0)*0+1).drop_vars('time')
    return (art_osm)

## Artificial Surfaces classes
class s1_artiwoody(Transformation):
    """
    Generate an artificial (or woody) product from Sentinel-1 ARD
    """
    def compute(self, data):
        numDates = data.VH.where(data.VH !=0).count(dim='time')
        artwoo_vh = data.VH.where(data.VH > -15.).count(dim='time')
        artwoo_vh_mths = artwoo_vh / numDates *12
        artiwoody_bin = artwoo_vh_mths.where(artwoo_vh_mths > 8)*0+1
        return (artiwoody_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'art': Measurement(name='art', dtype='float32', nodata=float('nan'), units='1')}


class s2_artif(Transformation):
    """
    Generate an artificial product from Sentinel-2 ARD
    """
    def compute(self, data):
        data["ndbi"] = (data.swir1 - data.nir) / (data.nir + data.swir1)
        mean_annual_ndbi = data.ndbi.mean(dim='time')
        artif_ndbi_bin = mean_annual_ndbi.where(mean_annual_ndbi > (-0.1))*0+1
        return (artif_ndbi_bin.to_dataset(name='band'))
    
    def measurements(self, input_measurements):
        return {'art': Measurement(name='art', dtype='float32', nodata=float('nan'), units='1')}


class artific_urb_cat(Transformation):
    """
    Combining artificial products into an artificial surface layer
    """
    def compute(self, data):
        print("running VP: artific_urb_cat")
        from pyproj import Proj, transform, CRS
        
        data_combined = data.sum(dim="time")
        artif_sentinel = data_combined.where(data_combined == 3)*0+1
        
        #print("1")
# #         training_inProj = Proj(init='epsg:27700')
#         training_inProj = CRS('EPSG:27700')
#         print("2")
#         training_outProj = CRS('EPSG:4326')
#         training_outProj = Proj(init='epsg:4326')
#         print("3")
#         min_x,min_y = transform(training_inProj,training_outProj,data.x.min().values,data.y.min().values)
#         print("4")
#         max_x,max_y = transform(training_inProj,training_outProj,data.x.max().values,data.y.max().values)
        #print(min_x,min_y,max_x,max_y)

        product = 'osm_free_geofabrik'
        query = {'product': product,
                 'x': (data.x.min(), data.x.max()),
                 'y': (data.y.min(), data.y.max()),
                 'crs': 'epsg:27700',
                 'time': ('2019-03-25', '2019-03-26'),
                 'output_crs': 'epsg:27700', 
                 'resolution': (-10,10)}
        #print(query)
        art_osm = osm_artif_features(query)
        
        art_all = artif_sentinel.fillna(0) + art_osm.fillna(0)
        artif = art_all.where(art_all > 0)*0+1
        print("done")
        return (artif)
    
    def measurements(self, input_measurements):
        return {'artific_urb_cat': Measurement(name='artific_urb_cat', dtype='float32', nodata=float('nan'), units='1')}

    
class le_artific_urb_cat(Transformation):
    """
    Combining artificial products into an artificial surface layer
    """
    def compute(self, data):
        print("USING artific_urb_cat in LivingEarth...")
        artific_urb_cat_dataset = data.rename(name_dict={"band":"artific_urb_cat"})
        artific_urb_cat_dataset = artific_urb_cat_dataset.fillna(0)
        return (artific_urb_cat_dataset)
    
    def measurements(self, input_measurements):
        return {'artific_urb_cat': Measurement(name='artific_urb_cat', dtype='float32', nodata=float('nan'), units='1')}
