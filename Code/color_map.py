#
# draw color map for census codes as a table
#https://matplotlib.org/stable/gallery/color/named_colors.html#sphx-glr-gallery-color-named-colors-py
#
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import pandas as pd
import math
import time

df = pd.read_csv('data/table_code_concept.csv', header=None, dtype=str)

cmap = plt.get_cmap('plasma')

ID = [int(i) for i in df.loc[:,0].tolist()]

ax, ppl = plt.subplots(5,2)
for i in ID:

    x = [0,1]
    y = [0,1]
    plt.plot(x,y)
    plt.text(.5,.5,ID)
    ax.set_facecolor(cmap(i/30.))
    print(cmap(i))

plt.show()
