# take variable codes used in PCA
# look up concepts
# plot the elements of the PCs by concept
# write to file so I can categorize them
# or can I categorize from first two digits?
# about table IDs: https://www.census.gov/programs-surveys/acs/data/data-tables/table-ids-explained.html

import pandas as pd
import matplotlib.pyplot as plt

variable_codes = []
with open('data/variable_codes.txt','r') as file:
    variable_codes = file.read().splitlines()
subject_codes = pd.Series([vc[1:3] for vc in variable_codes])

table_ids = pd.read_csv('data/table_ids.csv',header=None)
table_ids.columns = ["ID","Concept"]
table_dictionary = dict(zip(table_ids["ID"].tolist(),table_ids["Concept"].tolist()))
print(table_ids.head())

vcs = pd.DataFrame(subject_codes.value_counts())
vcs.reset_index(inplace=True)
vcs = vcs.rename(columns = {'index':'tablecode'})
vcs['tablecode'] = vcs['tablecode'].astype(int)
vcs["Concept"] = vcs['tablecode'].map(table_dictionary)
print("count of concepts in cleaned data")
print(vcs)

df_components=pd.read_csv('data/df_components.csv')

df_components["ID"] = df_components["variable_codes"].str.slice(1,3)
#https://matplotlib.org/stable/gallery/color/named_colors.html
color_dict = {
    "09": "red",
    "25": "blue",
    "08": "yellow",
    "28": "green",
    "06": "black",
    "11": "orange",
    "19": "purple",
    "01": "brown",
    "07": "gray",
    "27": "teal",
    "05": "springgreen",
    "14": "aqua",
    "23": "violet"
}
df_concept_map = pd.read_csv('data/table_code_concept.csv',dtype=str)
concept_dict = dict(zip(df_concept_map["ID"],df_concept_map["Concept"]))
color_concept_dict = {}
for key in color_dict.keys():
    color_concept_dict[key] = [color_dict[key],concept_dict[key]]
# plot the eigenvectors
for pc in ["PC1", "PC2", "PC3","PC4","PC5"]:
    df_components[pc] = abs(df_components[pc])
    df_sort = df_components.sort_values(by=pc,ascending=False)
    colormap = [color_dict[ID] for ID in df_sort["ID"].tolist()]
    x = list(range(len(df_sort)))
    colors = [v[0] for v in list(color_concept_dict.values())]
    labels = [v[1] for v in list(color_concept_dict.values())]
    l0 = list(color_dict.keys())
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_concept_dict[label][0]) for label in l0]
    #plt.legend(handles, labels)
    plt.bar(x,height=df_sort[pc],color=colormap)
    plt.title(pc+" Categories (All)")
    plt.show()
#truncate to top n components in absolute value
n = 50
for pc in ["PC1", "PC2", "PC3","PC4","PC5"]:
    df_components[pc] = abs(df_components[pc])
    df_sort = df_components.sort_values(by=pc,ascending=False)
    colormap = [color_dict[ID] for ID in df_sort["ID"].tolist()]
    colors = [v[0] for v in list(color_concept_dict.values())]
    labels = [v[1] for v in list(color_concept_dict.values())]
    l0 = list(color_dict.keys())
    handles = [plt.Rectangle((0, 0), 1, 1, color=color_concept_dict[label][0]) for label in l0]
    #plt.legend(handles, labels,loc='upper right')
    x = list(range(n))
    fig,ax = plt.subplots()
    plt.bar(x,height=df_sort[pc].iloc[:n],color=colormap)
    plt.title(pc+" Categories (Largest Abs. Value)")
    plt.show()
# counts of categories in top n
    vcs = pd.DataFrame(df_sort["ID"].iloc[:n].value_counts())
    vcs['tablecode'] = vcs.index.astype(int)
    vcs["Concept"] = vcs['tablecode'].map(table_dictionary)
    print("count of highest-weighted concepts in PC"+pc)
    print(vcs)


pie = plt.pie([1,1], labels=["a","b"])
for group in pie:
    for x in group:
        x.set_visible(False)
plt.legend(handles, labels, loc='upper right')
plt.show()

