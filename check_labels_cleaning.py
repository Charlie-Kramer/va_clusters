#check labels on ACS data
import pandas as pd

df = pd.read_csv('data/acs2021_5yr_label_lookup.csv')

csv_list = []

def import_codes():

    acs_codes = open('data/variable_codes.txt')
    codes=acs_codes.read()
    acs_codes.close()
    vars=codes.splitlines()

    return vars

vars = import_codes()
#print(vars)

labels = []

f=open('data/varbook.txt','w')
for var in vars:
    varname = str(df['Label'][df.Name == var].item()+" "+df['Concept'][df.Name == var].item())
    labels.append([var,varname])
    print(var[1:3],var,varname)
    f.write(var[1:3]+" "+var+" "+varname+"\n")
f.close()
stobit = 0
