#
# fixing the legend so it shows categorical
#
import pandas as pd
import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt
import matplotlib.pyplot as plt
import matplotlib #


df_merged = pd.read_csv('data/yelp_df_merged.csv')
df_gpd = gpd.GeoDataFrame(df_merged,geometry=gpd.points_from_xy(df_merged.INTPTLONG,df_merged.INTPTLAT))


ax = gplt.webmap(df_gpd, projection=gcrs.WebMercator())
cmap = matplotlib.colormaps.get_cmap('viridis')
#
# make cluster list--will plot by cluster assignment
#
cluster = df_gpd['kfit'].unique() #
clusters = [int(i) for i in cluster]
clusters.sort()
for i in clusters:
    gplt.pointplot(df_gpd[df_gpd['kfit']==i],color=cmap(float(i+1)/float(len(clusters))), label=str(clusters[i]),ax=ax)#
plt.legend()
plt.title("Yelp clusterssssss")
plt.show()

