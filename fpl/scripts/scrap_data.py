import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns

url ='https://fantasy.premierleague.com/api/bootstrap-static/'

r = requests.get(url)

response = r.json()
response.keys()

events_df = pd.DataFrame(response['events'])
name = events_df[(events_df['finished'] == True) & (events_df['data_checked'] == True)]['name'].to_list()[-1]
main_df = pd.DataFrame(response['elements'])

main_df.to_csv("csvs/2022_2023/{}.csv".format(name))