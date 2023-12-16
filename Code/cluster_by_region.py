import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt

#

# open county shapefiles
#
df_counties = gpd.read_file('data/VirginiaAdministrativeBoundary.shp/VirginiaCounty.shp')
#
# open cluster classification by census tract
#
df_clusters = pd.read_csv('data/acs_yelp_kmeans_clusters.txt', sep = " ",header=None)
df_clusters.columns=['FIPS','cluster']
county_name = df_counties['NAMELSAD']
#
# can match on first five digits of FIPS?
#
cluster_fips = df_clusters["FIPS"].to_list()

cluster_fips_short = [int(str(f)[:5]) for f in cluster_fips]
df_clusters["cluster_fips_short"] = cluster_fips_short

df_county_to_region = pd.read_csv('data/county_to_region.csv')

county_fips = df_county_to_region['fips'].to_list()
county_region = df_county_to_region['region'].to_list()
region_dict = dict(zip(county_fips,county_region))


df_clusters['region'] = df_clusters['cluster_fips_short'].map(region_dict)

vc = df_clusters['cluster'].value_counts()
x=vc.index

plt.bar(x,vc)
plt.show()

cmap = matplotlib.colormaps['viridis']

colors = [cmap(float(i+1)/5.) for i in range(5)]

regions = df_county_to_region['region'].unique().tolist()
fig,ax = plt.subplots(nrows=4,ncols=2,sharex=False)
regions.sort()

for i,region in enumerate(regions):
    df = df_clusters[df_clusters['region']==region]
    vc = df['cluster'].value_counts()
    vc.sort_index(inplace=True)

    x=vc.index
    ax[i%4,i//4].set_title(region,fontsize='small')
    ax[i%4,i//4].bar(x,vc,label=['0','1','2','3','4'],color=colors)

plt.subplots_adjust(hspace=2)
plt.show()

df_gaz = pd.read_csv('data/2021_gaz_tracts_51.txt',sep='\t')
df_c2 = df_clusters.merge(df_gaz,left_on='FIPS',right_on='GEOID')
print(df_c2.head())
print(df_c2[(df_c2['region']=="NORTHERN")&(df_clusters['cluster']==2)])
print(df_c2[(df_c2['region']=="SOUTHSIDE")&(df_clusters['cluster']==4)])

#
# function to set boundaries on small maps
#
def set_extent(df,tweak):
    xt = df.total_bounds
    xt[0] *= 1./tweak
    xt[1] *= 1./tweak
    xt[2] *= tweak
    xt[3] *= tweak
    return xt

df_gpd = gpd.GeoDataFrame(df_c2,geometry=gpd.points_from_xy(df_c2.INTPTLONG,df_c2.INTPTLAT))

ax = gplt.webmap(df_gpd, projection=gcrs.WebMercator())
df0 = df_gpd[(df_gpd['region']=="SOUTHSIDE")&(df_gpd['cluster']==3)]
xt = set_extent(df=df0,tweak=1.04)
gplt.pointplot(df0,ax=ax,s=12.,extent=xt)#
plt.savefig('cluster_3_southside')
plt.show()

ax = gplt.webmap(df_gpd, projection=gcrs.WebMercator())

df1 = df_gpd[(df_gpd['region']=="NORTHERN")&(df_gpd['cluster']==2)]
xt = set_extent(df=df1,tweak=1.03)
gplt.pointplot(df1,ax=ax,s=12.,extent=xt)
plt.savefig('cluster_2_northern')
plt.show()

ax = gplt.webmap(df_gpd, projection=gcrs.WebMercator())

df2 = df_gpd[(df_gpd['region']=="SOUTHWEST")&(df_gpd['cluster']==3)]
xt = set_extent(df=df2,tweak=1.03)
gplt.pointplot(df2,ax=ax,s=12.,extent=xt)#
plt.savefig('cluster_3_southwest')
plt.show()







