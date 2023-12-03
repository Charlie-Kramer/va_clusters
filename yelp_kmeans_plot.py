# run kmeans on yelp data

from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt

df_r = pd.read_csv('data/yelp_restrooms.csv')
df_v = pd.read_csv('data/yelp_vegetarian.csv')
#
# merge the two datasets
#
df_rv0 = df_r.merge(df_v,on='geoid')
#
# import the census dataset so I can drop the ones with no population

df_acs = pd.read_csv('data/acs_data_clean.csv')
# drop tracts with zero population (all water?)
geoid_temp = df_acs['GEO_ID'].tolist()
geoid = [int(x[-11:]) for x in geoid_temp]
df_acs['geoid'] = geoid
df_rv = df_rv0.merge(df_acs)
df_rv = df_rv[df_rv['B01001_001E']>0.0]
#
# strip down to only variables needed for kmeans
#
final_table_columns = ['geoid','lat_x','long_x','avgd_x','avgd_y']
df_rv.drop(columns=[col for col in df_rv if col not in final_table_columns], inplace=True)
#
# rename cols
#
df_rv.rename(columns = {'lat_x':'lat','long_x':'long','avgd_x':'rest','avgd_y':'veg'},inplace=True)
# replace NaNs with max
geoid0 = df_rv['geoid'].tolist()
max_r = df_rv.max()[3]
max_v = df_rv.max()[4]
replace_values = {'rest':max_r,'veg':max_v}
df_rv.fillna(value=replace_values,inplace=True)
# skip pca
#
stob = 1
#load the cleaned data

arr_unscaled = df_rv[['rest','veg']].to_numpy()
# scale the data
scaler = StandardScaler()
arr = scaler.fit_transform(arr_unscaled)
pc5 = arr
df_components = pd.DataFrame(arr)
df_components.rename(columns={0:'rest',1:'veg'},inplace=True)
df_components['geoid'] = geoid0
print(df_components.head())
df_components.to_csv('data/yelp_df_data.csv',index=False)
#
# now do kmeans
#
sses = []
sils = []

min_k,max_k = 2,10

for k in range(min_k,max_k):
    print("kmeans k = ",k)
    # fit model
    kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto")
    kfit = np.expand_dims(np.array(kmeans.fit_predict(pc5)),axis=1)
    # diagnostics
    sse = kmeans.inertia_
    print("sse",sse)
    sil_coeff = silhouette_score(pc5, kfit.ravel(), metric='euclidean')
    print("sillhouette score",sil_coeff)
    print("Kmeans group counts")
    print(pd.DataFrame(kfit).value_counts())
    sses.append(sse)
    sils.append(sil_coeff)

x_ax = np.transpose(np.arange(min_k,max_k))
plt.plot(x_ax,sses)
plt.title("Yelp Kmeans--SSE vs K")
plt.savefig("yelp_sse.png")
plt.show()
plt.plot(x_ax,sils)
plt.savefig("yelp_sil.png")
plt.title("Yelp Kmeans--Silhouette vs K")
plt.savefig("yelp_sil.png")
plt.show()
#
# 3 looks good
#
k = 3
kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto")
kfit = np.expand_dims(np.array(kmeans.fit_predict(pc5)), axis=1)
#
# map the results
# reattach GEO_ID and join the Gazeteer file based on GEO_ID
# can then use lat long to map
#
# first add back GEO_ID and convert to dataframe
geoid1 = np.expand_dims(np.array(geoid0),axis=1)
df_pc_geoid = pd.DataFrame(np.concatenate((kfit,pc5,geoid1),axis=1))
df_pc_geoid.columns = ['kfit', 'veg', 'rest','GEOID']
# bring in geolocation data from gazeteer
df_gaz = pd.read_csv("data/2021_gaz_tracts_51.txt", sep="\t")

df_merged = df_pc_geoid.merge(df_gaz,how='left',on="GEOID")
df_merged.to_csv('data/yelp_df_merged.csv')

df_gpd = gpd.GeoDataFrame(df_merged,geometry=gpd.points_from_xy(df_merged.INTPTLONG,df_merged.INTPTLAT))

ax = gplt.webmap(df_gpd, projection=gcrs.WebMercator())

cmap = matplotlib.colormaps.get_cmap('viridis')
cluster = df_gpd['kfit'].unique()
clusters = [int(i) for i in cluster]
clusters.sort()
for i in clusters:
    gplt.pointplot(df_gpd[df_gpd['kfit']==i],color=cmap(float(i+1)/float(len(clusters))), label=str(clusters[i]),ax=ax)#
plt.legend()
plt.title("Yelp clusters")
plt.savefig("Yelp_Cluster_Map.png")
plt.show()


f=open('data/yelp_kmeans_clusters.txt','w')
cluster_map = zip(df_merged["GEOID"].tolist(),df_merged["kfit"].tolist())
for c in cluster_map:
    f.write(str(int(c[0]))+" "+str(int(c[1]))+"\n")
f.close()


