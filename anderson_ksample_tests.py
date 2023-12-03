#
# anderson ksample tests over all vars by cluster
# apply bonferroni correction
#

import pandas as pd
from scipy.stats import anderson_ksamp
import matplotlib.pyplot as plt
import matplotlib
import warnings
warnings.filterwarnings('ignore')
#
#load cluster assignment data per geoid
#
df_acs_clusters = pd.read_csv('data/acs_kmeans_clusters.txt', sep = ' ')
df_acs_clusters.columns = ["GEOID","acs_cluster"]
df_yelp_clusters = pd.read_csv('data/yelp_kmeans_clusters.txt', sep = ' ')
df_yelp_clusters.columns = ["GEOID","yelp_cluster"]
df_acs_yelp_clusters = pd.read_csv('data/acs_yelp_kmeans_clusters.txt', sep = ' ')
df_acs_yelp_clusters.columns = ["GEOID","acs_yelp_cluster"]
#
# load original raw data
#
# df0 = pd.read_csv('data/acs_data_clean.csv')
# # drop tracts with zero population (all water?)
# df1 = df0[df0['B01001_001E']>0.0]
# GEOID0 = df1["GEO_ID"].tolist()
# # drop NAME, GEO_ID, state, county, tract
# df_acs = df1.drop(columns=['NAME','state','county','tract'],inplace=False)

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
max_r = df_rv.max().iloc[3]
max_v = df_rv.max().iloc[4]
replace_values = {'rest':max_r,'veg':max_v}
df_rv.fillna(value=replace_values,inplace=True)
#
# join all databases
#
GEOID0 = df_acs["GEO_ID"].tolist()
GEOID1 = [int(x[-11:]) for x in GEOID0]
df_acs['geoid'] = GEOID1
df_acs_rv = df_rv.merge(df_acs,on='geoid')
df_acs_rv = df_acs_rv.merge(df_acs_clusters,left_on='geoid',right_on='GEOID')
df_acs_rv = df_acs_rv.merge(df_acs_yelp_clusters,left_on='geoid',right_on='GEOID')
df_acs_rv = df_acs_rv.merge(df_yelp_clusters,left_on='geoid',right_on='GEOID')
#
# subset variables for testing
#
cols = set(df_acs_rv.columns)

not_test_vars = set(["geoid","lat","long","NAME","GEO_ID","state","county","tract","GEOID_x","acs_cluster",
                "acs_yelp_cluster","yelp_cluster","GEOID_y","acs_yelp_cluster_x","GEOID","acs_yelp_cluster_y"])

test_vars = sorted(list(cols-not_test_vars))
#
# now loop over clusters, test vars and test, save results
#
cluster_ps = {"acs_cluster":[], "yelp_cluster":[], "acs_yelp_cluster":[]}
noseps =  {"acs_cluster":[], "yelp_cluster":[], "acs_yelp_cluster":[]}
#
# loop here over list of clusters
#
cluster_mod_list = ["acs_cluster",'acs_yelp_cluster','yelp_cluster']
for cluster_mod in cluster_mod_list:
#
#loop here over list of vars
#
    print("*****************",cluster_mod,"*****************")
    for var in test_vars:

        df_test = df_acs_rv[[var,cluster_mod]]

        try:
            clusters = sorted(list(set(df_test[cluster_mod].tolist())))
        except AttributeError:
            print('>>>>>>>>>>>>>>>> attrib error',cluster_mod,var)

        test_list = []
        for i in clusters:
            df_test_i = df_test.loc[df_test[cluster_mod]==i]
            test_list.append(df_test_i[var].tolist())

        #
        # now run test
        #
        pv = anderson_ksamp(test_list).pvalue
        cluster_ps[cluster_mod].append(pv)
        if (pv > .01):
            noseps[cluster_mod].append(var)

acs_pvals = cluster_ps["acs_cluster"]
yelp_pvals = cluster_ps["yelp_cluster"]
acs_yelp_pvals = cluster_ps["acs_yelp_cluster"]
x = range(len(acs_pvals))
fig, ax = plt.subplots()
plt.plot(x,acs_pvals,label='acs')
plt.plot(x,yelp_pvals,label='yelp')
plt.plot(x,acs_yelp_pvals,label='acs_yelp')
ax.legend()
plt.show()

acs_pvals.sort()
yelp_pvals.sort()
acs_yelp_pvals.sort()
x = range(len(acs_pvals))
fig, ax = plt.subplots()
plt.plot(x,acs_pvals,label='acs')
plt.plot(x,yelp_pvals,label='yelp')
plt.plot(x,acs_yelp_pvals,label='acs_yelp')
ax.legend()
plt.savefig('anderson_pvals.png')
plt.show()

for key in noseps.keys():
    print(key,noseps[key])

noseps_list = [noseps[key] for key in noseps.keys()]

print(noseps_list)
print('common')
print(set(noseps_list[0]) & set(noseps_list[1]))
print(set(noseps_list[0]) & set(noseps_list[2]))
print(set(noseps_list[1]) & set(noseps_list[2]))
commons = (set(noseps_list[1]) & set(noseps_list[2]))

df = pd.read_csv('data/varbook.csv',sep='^')
varlookup = dict(zip(df['Code'].tolist(),df['Concept'].tolist()))

for var in commons:
    print(var,varlookup[var])

#
# now map a few distributions for combo
#
#"B28002_004E Broadband of any type
#"C27007_001E Medicaid-means tests public coverage
#"C27012_008E Worked full time no health insurance coverage
#"B25003_002E Owner occupied
#"B06012_002E below 100 pct poverty level
#"B06010_011E income >= 75K
#"B09019_011E same sex spouse
varlist = [ ["B01001_001E","Population",10000,100],
            ["B28002_004E","Broadband Of Any Type",3500,110],
            ["C27007_001E","Medicaid Coverage",10000,110],
            ["C27012_008E", "Worked Full Time, No Health Insurance Coverage",1600,520],
            ["B25003_002E", "Owner Occupied Housing",3750,120],
            ["B06012_002E", "Below Poverty Level",3000,400],
            ["B06010_011E", "Income >= 75K",3750,120],
            ["B09019_011E", "Same Sex Spouse",160,600]
    ]

cmap = matplotlib.cm.get_cmap('viridis')

df_acs_rv['bband'] = df_acs_rv['B28002_004E']/df_acs_rv['B01001_001E']
df_acs_rv['medicaid'] = df_acs_rv['C27007_001E']/df_acs_rv['B01001_001E']
df_acs_rv['worked'] = df_acs_rv['C27012_008E']/df_acs_rv['B01001_001E']
df_acs_rv['housing'] = df_acs_rv['B25003_002E']/df_acs_rv['B01001_001E']
df_acs_rv['poverty'] = df_acs_rv['B06012_002E']/df_acs_rv['B01001_001E']
df_acs_rv['income'] = df_acs_rv['B06010_011E']/df_acs_rv['B01001_001E']
df_acs_rv['samesex'] = df_acs_rv['B09019_011E']/df_acs_rv['B01001_001E']

# update for relative rather than absolute #s

varlist = [ ["bband","Broadband Of Any Type",1,110],
            ["medicaid","Medicaid Coverage",1,110],
            ["worked", "Worked Full Time, No Health Insurance Coverage",.4,520],
            ["housing", "Owner Occupied Housing",1,120],
            ["poverty", "Below Poverty Level",.6,400],
            ["income", "Income >= 75K",1,120],
            ["samesex", "Same Sex Spouse",.02,600]
    ]


for var_ in varlist:
    var = var_[0]
    var_title = var_[1]
    cluster_mod = 'acs_yelp_cluster' #'acs_cluster','yelp_cluster','acs_yelp_cluster'
    n_bins = 20
    cluster_nos = list(set(df_acs_rv[cluster_mod].tolist()))

    fig,ax = plt.subplots(len(cluster_nos),1)
    fig.suptitle(var_title)
    x_min = 0 #df_acs_rv[var].min()
    x_max = var_[2] #df_acs_rv[var].max()
    y_min = 0
    y_max = var_[3]
    for i,cluster_no in enumerate(cluster_nos):
        ax[i].set_ylim([y_min,y_max])
        plot_data = df_acs_rv[var].loc[df_acs_rv[cluster_mod]==cluster_no]
        ax[i].hist(plot_data,n_bins,color=cmap(float(i+1)/float(len(cluster_nos))),label='cluster'+str(cluster_no),range=(x_min,x_max))
        ax[i].legend()

    plt.subplots_adjust(wspace=.5,hspace=.5)
    plt.savefig("distribs_"+cluster_mod+"_"+var)
    plt.show()
#
#  anderson test on normalized vars
#

varlist = ['bband','medicaid','worked','housing','poverty']

cluster_mod = 'acs_yelp_cluster'

fig, ax = plt.subplots(nrows=len(varlist),ncols=5)

for var in varlist:
    df_test = df_acs_rv[[var, cluster_mod]]

    try:
        clusters = sorted(list(set(df_test[cluster_mod].tolist())))
    except AttributeError:
        print('>>>>>>>>>>>>>>>> attrib error', cluster_mod, var)

    test_list = []
    for i in clusters:
        df_test_i = df_test.loc[df_test[cluster_mod] == i]
        test_list.append(df_test_i[var].tolist())

    #
    # now run test
    #
    pv = anderson_ksamp(test_list).pvalue
    print(var,"pv = ", pv)

    cluster_nos = list(set(df_acs_rv[cluster_mod].tolist()))


print(df_acs_rv[['B28002_004E','acs_yelp_cluster']].loc[df_acs_rv['B28002_004E']==0])
