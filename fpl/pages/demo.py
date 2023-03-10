import streamlit as st
import requests
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt 
import seaborn as sns


url ='https://fantasy.premierleague.com/api/bootstrap-static/'

st.title("FPL Data visualisation")

@st.cache_data
def load(url):
    r = requests.get(url)
    json = r.json()
    elements_df = pd.DataFrame(json['elements']) #Creating data frame for element
    teams_df = pd.DataFrame(json['teams'])

    elements_df['name'] = elements_df['first_name'] + " " + elements_df['second_name']

    temp_df = elements_df[['name', 'ep_next', 'ep_this', 'event_points',
       'expected_goal_involvements','expected_goals_conceded',
       'form','goals_conceded','assists','goals_scored','ict_index', 
       'influence', 'now_cost', 'saves', 'starts', 'team', 'value_season']]
    
    for i in temp_df.columns[1:]:
       temp_df[i] = temp_df[i].astype(float)

    temp_df.loc[:,['delta_xgi']] = temp_df['expected_goal_involvements'] - (temp_df['goals_scored'] + temp_df['assists'])
    temp_df.loc[:,['delta_xgc']] = temp_df['expected_goals_conceded'] - temp_df['goals_conceded']
    temp_df.loc[:,['team']] = temp_df.team.map(teams_df.set_index('id').name) 
    
    return temp_df

current_df = load(url)
st.write(current_df)

if st.checkbox("Investigate team"):
    team = st.selectbox("Teams", set(list(current_df['team'])))
    current_df.loc[current_df['team'] == team]

if st.checkbox("Compare players"):
    players = st.multiselect("Players", list(current_df["name"]))
    cond = current_df['name'].isin(players)
    current_df[cond]
