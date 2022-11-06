'''
Description: This file contains a set of python functions for computing
remote sensing burnt area mapping with WDC data.
'''

habitat_dict = {3:'SemiNatural grass',
4:'Juncus communities',
5:'Molinia communities',
10:'Woodland and scrub',
12:'Broadleaved woodland',
16:'Coniferous woodland',
23:'Scrub',
35:'Acid grassland',
38:'Neutral grassland',
41:'Calcareous grassland',
44:'Improved grassland',
45:'Marsh/marshy grassland',
50:'Bracken',
58:'Dry dwarf shrub heath',
61:'Wet dwarf shrub heath',
70:'Blanket sphagnum bog',
71:'Raised sphagnum bog',
72:'Wet modified bog',
73:'Dry modified bog',
78:'Fen',
85:'Peat - bare',
86:'Swamp',
90:'Open Water',
106:'Intertidal vegetation Generic',
107:'Intertidal Bare Generic',
116:'Intertidal - boulders/rocks',
119:'Saltmarsh',
128:'Sand dune',
130:'Dune grassland',
131:'Dune heath',
132:'Dune scrub',
134:'Maritime cliff and slope',
135:'Hard cliff',
136:'Soft cliff',
142:'Natural rock exposure and waste',
143:'Inland cliff',
146:'Scree',
150:'Other rock exposure',
155:'Quarry',
159:'Cultivated (arables)',
200:'Artificial bare surfaces',
201:'Natural bare surfaces'}

def load_habitat_map(year, geom_extent):
    import datacube
    dc = datacube.Datacube()
    query = {'product': 'lw_habitats_lw',
             'geopolygon': geom_extent,
             'time': ("2020-01-01","2020-12-31"),
             'output_crs': 'epsg:27700',
             'resolution': (-10,10)}
    habitat_map = dc.load(**query)
    habitat_map = habitat_map.where(habitat_map != 0)
    # # When using epsg other than 4326, latitude and longitude are renames y and x.
    # # Let's correct that then the notebook run more smoothly
    habitat_map = habitat_map.rename({'x': 'longitude', 'y': 'latitude'})
    habitat_map = habitat_map.squeeze(dim='time')
    return habitat_map
