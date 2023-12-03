# read gazeteer, check which tracts are only water
import pandas as pd

df = pd.read_csv("data/2021_gaz_tracts_51.txt", sep="\t")

print(df.head())

df2 = df[df["ALAND"]!=0]
print(df.shape)
print(df2.shape)