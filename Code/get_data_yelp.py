#
# download data from yelp reviews
# movies?
# drag shows?
#
#https://docs.developer.yelp.com/reference/v3_business_search
#http://nealcaren.github.io/sushi_bars.html
#
# keywords:
#       liked_by_vegetarians
#       gender_neutral_restrooms
#
#       have tags for LGBTQ friendly, gun friendly?
#       can lookup by FIPS? see data from Harvard
# use geolocations from gazeteer
import requests
import pandas as pd
import json
import time
import config

#df = pd.read_csv('data/www2.census.gov_geo_docs_maps-data_data_gazetteer_2021_Gazetteer_2021_gaz_tracts_51.txt.old', sep='\t')
df = pd.read_csv('data/2021_gaz_tracts_51.txt', sep='\t')
print(df.head())

Client_ID = config.yelp_client_id
API_Key = config.yelp_client_id

attrib='liked_by_vegetarians'
latlong = list(zip(df['INTPTLAT'].tolist(),df['INTPTLONG'].tolist(),df["GEOID"].tolist()))

remainders = [51003010100]

latlong2 = [x for x in latlong if x[2] in remainders]

print("latlong2",latlong2)

latlong = latlong2

n_records = 5

headers = {
    "accept": "application/json",
    "Authorization": "Bearer o_SOXmsNme29Tlq0Q3J7y2gp0FchUbewvZkjJWNkb2D6VHojc55ekNy_SOc2rcqf6FgOGpGT-0ld5vb1NkQl75SdfFvGCmxMU45gzz6LPcLghVTXCK1YiwJzMeEaZXYx"
}
print("len latlong",len(latlong))
with open('data/yelp_vegetarian.csv','a+') as f:

    for i in range(len(latlong)):
        lat = latlong[i][0]
        long = latlong[i][1]
        geoid = latlong[i][2]
        url = f"https://api.yelp.com/v3/businesses/search?latitude={lat}&longitude={long}&attributes={attrib}&sort_by=best_match&limit={n_records}"
        time.sleep(3)
        response = requests.get(url, headers=headers)

        print("i, status code, lat, long, geoid", i, response.status_code, lat, long,geoid)

        if (response.status_code == 200): #if valid response
            response_json = json.loads(response.text)['businesses']

            if len(response_json) > 0: # if at least one business returned
                avgd = 0
                for j in range(len(response_json)):
                    avgd += (response_json[j]["distance"])/len(response_json)
                print("i, lat, long, geoid, avgd", i, lat, long, geoid, avgd)
            else:
                avgd = None
            out_str = str(geoid)+","+str(lat)+","+str(long)+","+str(avgd)+"\n"
            f.write(out_str)

f.close()