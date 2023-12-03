# bonks in PyCharm--see notebook version
import pandas as pd
import matplotlib.pyplot as plt
import time

df = pd.read_csv('data/acs_data.csv')

print(df.describe())

for col in df.columns:
    fig, axis = plt.subplots(1, 1)
    df[col].hist()
    plt.title(col)
    plt.show()
