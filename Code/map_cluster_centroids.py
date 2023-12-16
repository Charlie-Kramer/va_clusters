# plot cluster centroids
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt
import mapclassify as mc
#
# load GEOID and cluster assigments
#
df_yelp = pd.read_csv('data/yelp_kmeans_clusters.txt', sep = ' ')
df_yelp.columns = ["GEOID","yelp_cluster"]
df_acs = pd.read_csv('data/acs_kmeans_clusters.txt', sep = ' ')
df_acs.columns = ["GEOID","acs_cluster"]
df_acs_yelp = pd.read_csv('data/acs_yelp_kmeans_clusters.txt', sep = ' ')
df_acs_yelp.columns = ["GEOID","acs_yelp_cluster"]
#
# load location data for each GEOID
#
df_gaz = pd.read_csv("data/2021_gaz_tracts_51.txt", sep="\t")

df_yelp = df_yelp.merge(df_gaz,on="GEOID")
df_acs = df_acs.merge(df_gaz,on="GEOID")
df_acs_yelp = df_acs_yelp.merge(df_gaz,on="GEOID")
#
# calculate median lat/long
#
med_yelp = df_yelp[["INTPTLAT","INTPTLONG","yelp_cluster"]].groupby("yelp_cluster").median()
med_acs = df_acs[["INTPTLAT","INTPTLONG","acs_cluster"]].groupby("acs_cluster").median()
med_acs_yelp = df_acs_yelp[["INTPTLAT","INTPTLONG","acs_yelp_cluster"]].groupby("acs_yelp_cluster").median()
#
# map median lat/long for each
#
# merge all three into one map
#
med_acs['variables'] = 'ACS'
med_yelp['variables'] = 'Yelp'
med_acs_yelp['variables'] = 'ACS+Yelp'
df_combo = pd.concat([med_acs,med_yelp,med_acs_yelp])
#plot em
df_gpd = gpd.GeoDataFrame(df_combo,geometry=gpd.points_from_xy(df_combo.INTPTLONG,df_combo.INTPTLAT))
ax = gplt.webmap(df_gpd, projection=gcrs.WebMercator())
gplt.pointplot(df_gpd[df_gpd['variables']=='ACS'],color='blue', alpha=.5,ax=ax,label="ACS")
gplt.pointplot(df_gpd[df_gpd['variables']=='Yelp'],color='red', alpha=.9,ax=ax,label="Yelp")
gplt.pointplot(df_gpd[df_gpd['variables']=='ACS+Yelp'],color='yellow', alpha=.5, ax=ax, label="ACS+Yelp")
plt.legend()
plt.savefig('cluster_centroid.png')
plt.show()

