# get census data using census package

from census import Census
import pandas as pd
import config

key = config.acs_key

c = Census(key)

def import_codes(filename):

    acs_codes = open(filename)
    codes=acs_codes.read()
    acs_codes.close()
    codes = "".join(codes.splitlines())
    vars = codes.split(',')

    vars.insert(0,"NAME")

    return vars

namelist = import_codes('data/ACS_variables.txt')

va_census = c.acs5.state_county_tract(fields = namelist,
                                      state_fips = "51",
                                      county_fips = "*",
                                      tract = "*",
                                      year = 2021)
# Create a dataframe from the census data
va_df = pd.DataFrame(va_census)

# Show the dataframe
print(va_df.head(2))
print('Shape: ', va_df.shape)

va_df.to_csv('data/acs_data.csv',index=False)