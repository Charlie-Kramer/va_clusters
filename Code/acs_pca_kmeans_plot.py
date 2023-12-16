# calculate PCA from cleaned ACS data, run kmeans

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



#load the cleaned data
df0 = pd.read_csv('data/acs_data_clean.csv')
# drop tracts with zero population (all water?)
df1 = df0[df0['B01001_001E']>0.0]
GEOID0 = df1["GEO_ID"].tolist()
# drop NAME, GEO_ID, state, county, tract
df = df1.drop(columns=['NAME','GEO_ID','state','county','tract'],inplace=False)
variable_codes = df.columns
#save these for analysis later
with open('data/variable_codes.txt','w') as file:
    for code in variable_codes:
        file.write("%s\n" % code)
#convert to numpy
arr_unscaled = df.to_numpy()
# scale the data
scaler = StandardScaler()
arr = scaler.fit_transform(arr_unscaled)
#fit PCA
pca = PCA(n_components=10)
pca.fit(arr)
#PCA diagnostics
vr = pca.explained_variance_ratio_
print(vr[0]+vr[1]+vr[2]+vr[3]+vr[4])
x = np.arange(len(vr))
#plt.title("PCA of ACS Data: Variance Ratios")
plt.plot(x,vr)
plt.savefig("acs_pcs_var_ratio.png")
plt.show()
#
# based on plot, use 3 PCs
#
pca5 = PCA(n_components=5)
pc5 = pca5.fit_transform(arr)
#
# save var codes and components to file for analysis elsewhere
#
components = pca5.components_
df_components = pd.DataFrame(np.transpose(components))
df_components['variable_codes'] = pd.Series(variable_codes)
df_components.rename(columns={0:"PC1",1:"PC2",2:"PC3",3:"PC4",4:"PC5"},inplace=True)
print(df_components.head())
df_components.to_csv('data/acs_df_components.csv',index=False)
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
plt.title("ACS Kmeans--SSE vs K")
plt.savefig("acs_pcs_sse.png")
plt.show()
plt.plot(x_ax,sils)
plt.title("ACS Kmeans--Silhouette vs K")
plt.savefig("acs_pcs_sil.png")
plt.show()

#
# 2 looks good
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
#GEO_ID = np.expand_dims(df0["GEO_ID"].to_numpy(),axis=1)
GEOID1 = [int(x[-11:]) for x in GEOID0]
GEOID2 = np.expand_dims(np.array(GEOID1),axis=1)
df_pc_geoid = pd.DataFrame(np.concatenate((kfit,pc5,GEOID2),axis=1))
df_pc_geoid.columns = ['kfit', 'pc1', 'pc2', 'pc3', 'pc4','pc5','GEOID']
df_pc_geoid.to_csv('data/acs_pcs_data.csv',index=False)
# bring in geolocation data from gazeteer
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
plt.title("ACS Data Clusters")
plt.savefig("ACS_Cluster_Map.png")
plt.show()


plt.show()

f=open('data/acs_kmeans_clusters.txt','w')
cluster_map = zip(df_merged["GEOID"].tolist(),df_merged["kfit"].tolist())
for c in cluster_map:
    f.write(str(int(c[0]))+" "+str(int(c[1]))+"\n")
f.close()

