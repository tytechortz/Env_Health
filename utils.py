import geopandas as gpd
import pandas as pd

#Read block group data
bg_geo_data = gpd.read_file('assets/data/tl_2022_08_bg (1)/tl_2022_08_bg.shp')
bg_geo_arap = bg_geo_data[bg_geo_data['COUNTYFP'] == "005"]
bg_geo_arap['GEOID'] = bg_geo_arap['GEOID'].astype(int)

#Read block data
block_geo_data = gpd.read_file('assets/data/blocks4.json')
block_geo_data['GEOID'] = block_geo_data['GEOID'].astype(int)

#Read tract data
tract_geo_data = gpd.read_file('assets/data/2020_CT/ArapahoeCT.shp')
tract_geo_data = tract_geo_data.rename(columns={'FIPS':'GEOID'})
tract_geo_data['GEOID'] = tract_geo_data['GEOID'].astype(int)

print(tract_geo_data)


