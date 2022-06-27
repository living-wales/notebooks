from datacube.virtual import construct, Transformation, Measurement
import xarray as xr
from xarray import DataArray
import numpy as np
import dask
import wales_utils.data_cube_utilities.wdc_bandindices as wdc_index
import pickle

def indices_composite(year_y, start_month, end_month, index, query, x0_min, x0_max, y0_min, y0_max, stat="nanmean"):
    """
    year_y:: a four-charecter string specifying the year to process; e.g., "2020"
    start_month:: a two-charecter string specifying the starting month for the composite; e.g., "02"
    end_month:: a two-charecter string specifying the ending month for the composite; e.g., "04"
    index:: a string specifying the index to calculate. Must be an index from the wdc_index library; e.g., "NDVI"
    stat:: a string specifying the statistic to use for the xarray compositing 
    """
    from datetime import datetime
    import datacube
    dc = datacube.Datacube()
    
    if stat[0:3] != 'nan':
        stat = 'nan'+ stat
    print(stat, index)
    
    if end_month in ["01","03","05","07","08","10","12"]:
        end_day = "31"
    elif end_month in ["04","06","09","11"]:
        end_day = "30"
    elif end_month == "02":
        end_day = "28"
    
    print(year_y+'-'+start_month+'-01', ' to ', year_y+'-'+end_month+'-'+end_day)
    dataset_year_y = dc.load(time = (datetime.strptime(year_y+'-'+start_month+'-01', '%Y-%m-%d'), 
                                    datetime.strptime(year_y+'-'+end_month+'-'+end_day, '%Y-%m-%d')),
                             **query,
                             dask_chunks={'time': 1, 'x': 4000, 'y': 4000})
    dataset_year_y = dataset_year_y.where(
                         (dataset_year_y.x <= x0_max) & 
                         (dataset_year_y.x >= x0_min) &
                         (dataset_year_y.y <= y0_max) & 
                         (dataset_year_y.y >= y0_min), drop=True)
    
    dataset_year_y = dataset_year_y.where(
                            (dataset_year_y.scl != 0) & (dataset_year_y.scl != 1) & (dataset_year_y.scl != 2) & 
                            (dataset_year_y.scl != 3) & (dataset_year_y.scl != 8) & (dataset_year_y.scl != 9) & 
                            (dataset_year_y.scl != 10))
    
    dataset_year_y = wdc_index.calculate_indices(dataset_year_y, index=index, 
                                      platform='SENTINEL_2', normalise=True)
    
    dataset_extent = [dataset_year_y.x.min().values,dataset_year_y.y.min().values,
                      dataset_year_y.x.max().values, dataset_year_y.y.max().values]
    
    print(dataset_extent)
    stack = dask.array.concatenate([dataset_year_y[index]], axis=0)
    
    for pyear in [int(year_y)-1, int(year_y)-2]:
        print(str(pyear)+'-'+start_month+'-01', " to ", str(pyear)+'-'+end_month+'-'+end_day)
        dataset_pyear = dc.load(time = (datetime.strptime(str(pyear)+'-'+start_month+'-01', '%Y-%m-%d'), 
                                    datetime.strptime(str(pyear)+'-'+end_month+'-'+end_day, '%Y-%m-%d')),
                                     **query,
                                     dask_chunks={'time': 1, 'x': 4000, 'y': 4000})
        dataset_pyear = dataset_pyear.where(
                         (dataset_pyear.x <= x0_max) & 
                         (dataset_pyear.x >= x0_min) &
                         (dataset_pyear.y <= y0_max) & 
                         (dataset_pyear.y >= y0_min), drop=True)
        
        dataset_pyear = dataset_pyear.where(
                    (dataset_pyear.scl != 0) & (dataset_pyear.scl != 1) & (dataset_pyear.scl != 2) & 
                    (dataset_pyear.scl != 3) & (dataset_pyear.scl != 8) & (dataset_pyear.scl != 9) & 
                    (dataset_pyear.scl != 10))
        dataset_pyear = wdc_index.calculate_indices(dataset_pyear, index=index, 
                                          platform='SENTINEL_2', normalise=True)
        
        stack = dask.array.concatenate([stack, dataset_pyear[index]], axis=0)
    
    index_array = getattr(dask.array, stat)(stack, axis=0)
    return index_array


def s2_cult_img_prepare(data):
    """
    Calculate index statistics from Sentinel-2 ARD
    """
    from pyproj import Proj, transform

    year = str(data.time[0].dt.year.values)
    #print(year)
    training_inProj = Proj(init='epsg:27700')
    training_outProj = Proj(init='epsg:4326')
    min_x,min_y = transform(training_inProj,training_outProj,data.x.min().values,data.y.min().values)
    max_x,max_y = transform(training_inProj,training_outProj,data.x.max().values,data.y.max().values)
    #print(min_x,min_y,max_x,max_y)
    platform = 'SENTINEL_2'
    product = 'sen2_l2a_gcp'
    query = {'platform': platform,
         'product': product,
         'x': (min_x, max_x),
         'y': (min_y, max_y),
         'output_crs': 'epsg:27700', 
         'resolution': (-10,10)}
    #print(query)
    x0_min = data.x.min().values
    x0_max = data.x.max().values
    y0_min = data.y.min().values
    y0_max = data.y.max().values
    print("Original extent: ", x0_min, x0_max, y0_min, y0_max)
    NDVImax = indices_composite(year, "02", "04", "NDVI", query, x0_min, x0_max, y0_min, y0_max, stat="nanmax")
    VARIgmax = indices_composite(year, "02", "04", "VARIg", query, x0_min, x0_max, y0_min, y0_max, stat="nanmax")
    VARIgmed = indices_composite(year, "02", "04", "VARIg", query, x0_min, x0_max, y0_min, y0_max, stat="nanmedian")
    IRECImax = indices_composite(year, "02", "04", "IRECI", query, x0_min, x0_max, y0_min, y0_max, stat="nanmax")
    CIremax = indices_composite(year, "02", "04", "CIre", query, x0_min, x0_max, y0_min, y0_max, stat="nanmax")
    WDRVImax = indices_composite(year, "02", "04", "WDRVI", query, x0_min, x0_max, y0_min, y0_max, stat="nanmax")
    #
    dataCollection_img = [NDVImax, VARIgmax, VARIgmed, IRECImax, CIremax, WDRVImax]
    dictionary_coordinates = {'x': data.x.values,
                              'y': data.y.values}
    return dataCollection_img, dictionary_coordinates



class sklearn_cultivated_classification(Transformation):
    """
    Takes an existing model saved out as a pickle file to classify cultivated areas
    """
    def __init__(self, model_pickle):
        # Unpickle model
        with open(model_pickle, "rb") as f:
            self.ml_model_dict = pickle.load(f)

    def compute(self, data):
        
        print("Calculating indices ...")
        data_prepared = s2_cult_img_prepare(data)
        
        print("Predicting cultivated ...") 
        flatten_data = [dask.array.Array.flatten(data_prepared[0][index]) for index in range(len(data_prepared[0]))]
        flatten_array = dask.array.transpose(dask.array.asarray(flatten_data)).astype(np.float32)
        filled_flatten_array = dask.array.ma.fix_invalid(flatten_array, fill_value=0)
        classified_array = self.ml_model_dict.predict(filled_flatten_array)
        classified_data = classified_array.reshape(len(data_prepared[1]['y']), len(data_prepared[1]['x']))
        cultivated = DataArray(
                data=classified_data,
                dims=["y", "x"],
                coords=dict(
                    x=(["x"], data_prepared[1]['x']),
                    y=(["y"], data_prepared[1]['y']),
                ),
            )
        return (cultivated.to_dataset(name='band'))

    def measurements(self, input_measurements):
        return {'sklearn_cultivated': Measurement(name='sklearn_cultivated', dtype='float32', nodata=float('nan'), units='1')}


# class cultman_agr_cat(Transformation):
#     """
#     Generating cultivated ED layer
#     """
#     def compute(self, data):
#         sklearn_cultivated_classification = data[0]
#         vegetat_veg_cat = data[1].fillna(0)
#         woody_cat = data[2].fillna(0)
#         cultman_veg = sklearn_cultivated_classification * vegetat_veg_cat
#         cultman_veg_clean = cultman_veg - woody_cat
#         cultman_bin = cultman_veg_clean.where(cultman_veg_clean == 2)*0+1
#         return (cultman_bin)
    
#     def measurements(self, input_measurements):
#         return {'cultman_agr_cat': Measurement(name='cultman_agr_cat', dtype='float32', nodata=float('nan'), units='1')}
