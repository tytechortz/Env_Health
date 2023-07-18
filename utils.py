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

def get_restaurants():
    df = pd.read_csv('/Users/jamesswank/Downloads/Geocoded_restaurants_test.csv')
    # print(df['lat'].isna().sum())
    # print(df)
    return df

# get_restaurants()

def get_housing_units():
    df1 = pd.read_csv('assets/data/HousingUnits.csv')
    df1 = df1.iloc[1:]
    df1.drop(['H1_001NA', 'Unnamed: 4', 'NAME'], axis=1, inplace=True)
    df1['GEO_ID'] = df1['GEO_ID'].apply(lambda x: x[9:])
    # print(df1['GEO_ID'])
    geo_arap = block_geo_data
    df1 = df1.rename(columns={'H1_001N':'Total_HU', 'GEO_ID': 'GEOID'})
    # print(df1.columns)
    df1['GEOID'] = df1['GEOID'].astype(int)
    geo_arap['GEOID'] = geo_arap['GEOID'].astype(int)
    df1['Total_HU'] = df1['Total_HU'].str.replace(',', '').astype(int)
    df_HU = block_geo_data.merge(df1, on="GEOID")
    # print(df_HU)

    return df_HU

def get_tract_data():
    df1 = pd.read_csv('assets/data/TractPop.csv')
    
    df1['Total'] = df1['Total'].str.replace(',', '').astype(int)
   
    df = tract_geo_data.merge(df1, on="GEOID")
    # print(df)
    
    return df

def get_block_group_data():
   
    df1 = pd.read_csv('assets/data/BlockGroupPop.csv')
   
    geo_data = gpd.read_file('assets/data/tl_2022_08_bg (1)/tl_2022_08_bg.shp')

    geo_arap = geo_data[geo_data['COUNTYFP'] == "005"]
   
    df1['Total'] = df1['Total'].str.replace(',', '').astype(int)
   
    geo_arap['GEOID'] = geo_arap['GEOID'].astype(int)
    
    df = geo_arap.merge(df1, on="GEOID")
    

    return df

def get_block_data():
    block_df1 = pd.read_csv('assets/data/BlockPop.csv')
    
    df_HU = get_housing_units()
    
    block_df1 = block_df1.merge(df_HU, on="GEOID")
    block_df1['STATEFP'] = 5
    
    geo_arap = block_geo_data
    
    geo_arap['GEOID'] = geo_arap['GEOID'].astype(int)
   
    block_df1['Total'] = block_df1['Total'].str.replace(',', '').astype(int)
    
    df1 = block_geo_data.merge(block_df1, on=["GEOID", "TRACTCE20", "BLOCKCE20", "GEOID20", "NAME20", "ALAND20", "AWATER20", "INTPTLAT20", "INTPTLON20", "Shape_Leng", "Shape_Area", "geometry"])
    # print(df1)

    return df1












