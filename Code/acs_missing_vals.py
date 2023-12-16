# check missing values and drop cols with missing vals from ACS data
import pandas as pd
import matplotlib.pyplot as plt
import time


df = pd.read_csv('/Users/charleskramer/Documents/ISYE6740/Project/data/acs_data.csv')

print(df.describe())
print(df.shape)

# find nulls
nulls = df.isnull().sum()
nulls = pd.DataFrame(nulls[nulls!=0])
#look up codes
null_codes = nulls.index.values.tolist()
print("nullcodes",null_codes)

lookup_table = pd.read_csv('data/acs2021_5yr_label_lookup.csv')

null_df = lookup_table[lookup_table['Name'].isin(null_codes)]

print(null_df['Label'])

#replace annotation values
annlist = [-666666666,-999999999,-222222222,-333333333,-555555555]

df2 = df.replace(annlist,None)

#df3 = df2.dropna(axis=0)
#print("df3 shape",df3.shape)
df4 = df2.dropna(axis=1)
print("df4 shape",df4.shape)
df4.to_csv("data/acs_data_clean.csv",index=False)

# for col in df.columns:
#     fig, axis = plt.subplots(1, 1)
#     df[col].hist()
#     plt.title(col)
#     plt.show()
#     time.sleep(.25)


