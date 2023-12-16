#
# fit kmeans to both acs and yelp data
#
from sklearn.metrics import silhouette_score
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
import numpy as np
import geopandas as gpd
import geoplot.crs as gcrs
import geoplot as gplt

acs_df = pd.read_csv('data/acs_pcs_data.csv')
yelp_df = pd.read_csv('data/yelp_df_components.csv')

print(acs_df.describe())
print(yelp_df.describe())

acs_yelp_df = pd.merge(acs_df,yelp_df,how='left',left_on='GEOID',right_on='geoid')

print(acs_yelp_df.describe())
print(acs_yelp_df.columns)
#kmeans_data = acs_yelp_df[['pc1','pc2','pc3','pc4','pc5','veg','rest']]
arr_unscaled = acs_yelp_df[['pc1','pc2','pc3','pc4','pc5','veg','rest']].to_numpy()
scaler = StandardScaler()
arr = scaler.fit_transform(arr_unscaled)
kmeans_data = pd.DataFrame(arr)
#
# #
# # now do kmeans
# #
sses = []
sils = []
min_k,max_k = 2,10
for k in range(min_k,max_k):

    print("kmeans k = ",k)
    # fit model
    kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto")
    kfit = np.expand_dims(np.array(kmeans.fit_predict(kmeans_data)),axis=1)
    # diagnostics
    sse = kmeans.inertia_
    print("sse",sse)
    sil_coeff = silhouette_score(kmeans_data, kfit.ravel(), metric='euclidean')
    print("sillhouette score",sil_coeff)
    print("Kmeans group counts")
    print(pd.DataFrame(kfit).value_counts())
    sses.append(sse)
    sils.append(sil_coeff)

x_ax = np.transpose(np.arange(min_k,max_k))
plt.plot(x_ax,sses)
#plt.title("ACS+Yelp Kmeans--SSE vs K")
plt.savefig("acs_yelp_pcs_sse.png")
plt.show()
plt.plot(x_ax,sils)
#plt.title("ACS+Yelp Kmeans--Silhouette vs K")
plt.savefig("acs_yelp_pcs_sil.png")
plt.show()

#
# 3 looks good
#
k = 5
kmeans = KMeans(n_clusters=k, random_state=0, n_init="auto")
kfit = np.expand_dims(np.array(kmeans.fit_predict(kmeans_data)), axis=1)
#
# now plot the 5 clusters
#
GEOID = np.expand_dims(np.array(acs_yelp_df["GEOID"]),axis=1)
df_pc_geoid = pd.DataFrame(np.concatenate((kfit,GEOID),axis=1))
df_pc_geoid.columns = ["kfit","GEOID"]
df_gaz = pd.read_csv("data/2021_gaz_tracts_51.txt", sep="\t")

df_merged = df_pc_geoid.merge(df_gaz,how='left',on="GEOID")

df_gpd = gpd.GeoDataFrame(df_merged,geometry=gpd.points_from_xy(df_merged.INTPTLONG,df_merged.INTPTLAT))

ax = gplt.webmap(df_gpd, projection=gcrs.WebMercator())
cmap = matplotlib.colormaps.get_cmap('viridis')
cluster = df_gpd['kfit'].unique()
clusters = [int(i) for i in cluster]
clusters.sort()
for i in clusters:
    gplt.pointplot(df_gpd[df_gpd['kfit']==i],color=cmap(float(i+1)/float(len(clusters))), label=str(clusters[i]),ax=ax)#
plt.legend()
#plt.title("ACS + Yelp Clusters")
plt.savefig("ACS_Yelp_Cluster_Map.png")
plt.show()

#
# now load original data sets
# merge on GEOID, attach kfit
# do stats by cluster
# look for differentiators.

df0 = pd.read_csv('data/acs_data_clean.csv')
# drop tracts with zero population (all water?)
df1 = df0[df0['B01001_001E']>0.0]
# convert long form geoid to short form to prep for merge
GEOID0 = df1["GEO_ID"].tolist()
GEOID1 = [int(x[-11:]) for x in GEOID0]
df1.insert(0,'geoid',GEOID1)

df2 = df1.merge(pd.read_csv('data/yelp_df_data.csv'),on='geoid')
df3 = df2.merge(df_pc_geoid,left_on='geoid',right_on='GEOID')
df_gaz = pd.read_csv("data/2021_gaz_tracts_51.txt", sep="\t")
df4 = df3.merge(df_gaz,how='left',on="GEOID")
# #total pop, male, female
# B01001_001E, B01001_002E, B01001_026E
# foreign born
# B05002_013E
# total below 100 pct poverty line
#B06012_002E
# has one or more types of computing device
#B28001_002E
# total with broadband internet
#B28002_004E
# total medicaid/means tested public coverage
#C27007_001E

cols = ['kfit', 'B01001_001E', 'B01001_002E', 'B01001_026E', 'B05002_013E','B06012_002E',
    'B28001_002E','B28002_004E','C27007_001E','veg','rest','INTPTLAT','INTPTLONG'
        ]

df5 = df4[cols]
print(df5.describe())

df6 = df5.groupby('kfit').mean()
df6.to_csv('data/acs_yelp_kmeans_groupmeans.csv')
df6 = df5.groupby('kfit').median()
df6.to_csv('data/acs_yelp_kmeans_groupmedians.csv')

f=open('data/acs_yelp_kmeans_clusters.txt','w')
cluster_map = zip(df4["GEOID"].tolist(),df4["kfit"].tolist())
for c in cluster_map:
    f.write(str(int(c[0]))+" "+str(int(c[1]))+"\n")
f.close()

