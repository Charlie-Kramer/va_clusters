# from https://github.com/mcmanus-git/US-Census-ACS/blob/main/ACS%20Male%20Population%20by%20Age%20US.ipynb
# makes a dataframe from the variable table
import pandas as pd

def get_variable_table_df(year):
    variable_table_url = f'https://api.census.gov/data/{year}/acs/acs5/variables.html'
    v_table = pd.read_html(variable_table_url)
    variable_df = pd.DataFrame(v_table[0])
    variable_df['Label'].replace({"!!": " ", ":": ""}, regex=True, inplace=True)

    return variable_df

df = get_variable_table_df(2021)

df.to_csv('data/acs2021_5yr_label_lookup.csv')