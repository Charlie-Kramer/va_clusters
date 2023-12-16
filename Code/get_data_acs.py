# get census data--use version 2
# todo: join to lat long data (see data/)
# need age by sex figures, commuting time, work from home, education, languages, disability, income, occupation? is there a better way to find data codes
# how to print out descriptions for below?
# stopped here B26001_001E 10/10 4 pm
# economists B24114_117E

# https://api.census.gov/data.html
# https://www.census.gov/content/dam/Census/library/publications/2020/acs/acs_api_handbook_2020.pdf
# https://www.census.gov/data/what-is-data-census-gov/guidance-for-data-users/how-to-materials-for-using-the-census-api.html
# https://www.census.gov/programs-surveys/acs/library/handbooks/researchers.html
# https://www.census.gov/programs-surveys/acs/guidance/statistical-software.html
# https://api.census.gov/data/2021/acs/acs5/variables.html # find data here
# https://medium.com/@mcmanus_data_works/using-the-u-s-census-bureau-api-with-python-5c30ad34dbd7

import requests
import pandas as pd
import time
import config

key = config.acs_key
# open dataframe with labels

df = pd.read_csv('data/acs2021_5yr_label_lookup.csv')

host = 'https://api.census.gov/data'
year = '/2021'
dataset_acronym = '/acs/acs5'
g = '?get='
location = '&for=tract:*&in=state:51'
usr_key = f"&key={key}"

def import_codes(filename):

    acs_codes = open(filename)
    codes=acs_codes.read()
    acs_codes.close()
    codes = "".join(codes.splitlines())
    vars = codes.split(',')

    return vars

vars = import_codes('data/ACS_bad_variables.txt')

labels = []

acs_data = pd.DataFrame()

for var in vars:
    print("variable",var)
    query_url = f"{host}{year}{dataset_acronym}{g}{var}{location}{usr_key}"
    try:
        time.sleep(.25)
        response = requests.get(query_url)
    except:
        print("exception with variable", var)
    a = response.json()
    geoid = response.json()[1][1]+response.json()[1][2]+response.json()[1][3] # this will match geoid in location data from gazeteer
    varname = str(var+df['Label'][df.Name == var].item()+" "+df['Concept'][df.Name == var].item())
    if (len(df[df.Name==var]) != 1):
        print('multiple or zero matches for ',var,len(df[df.Name==var]))
    labels.append([var,varname])
    dat = [ai[0] for ai in a[1:]]
    if (len(dat)!=2198):
        print("warning len dat = ",len(dat))
    acs_data[varname] = dat

print(acs_data.shape)

print(labels)

print(len(vars))
print(len(labels))



acs_data.to_csv('data/acs_data.csv',index=False)
