import pandas as pd

df = pd.read_csv('data/yelp_restrooms.csv')
print(df.shape)
df2 = df.drop_duplicates(subset='geoid')
print(df2.shape)
df2.to_csv('data/yelp_restrooms_dedup.csv')