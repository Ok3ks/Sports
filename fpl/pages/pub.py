import streamlit as st
import json
import pandas as pd
from os.path import realpath,dirname

#BASE_DIR = realpath(__file__)
#print(BASE_DIR)

with open('/Users/max/Desktop/Sports/fpl/json/mod_gw_8_downtown.json', 'r') as ins:
    obj = json.load(ins)
    
with open('/Users/max/Desktop/Sports/fpl/json/transfer_history.json', 'r') as ins_2:
    transfer_obj = json.load(ins_2)

with open('/Users/max/Desktop/Sports/fpl/json/epl_players.json', 'r') as ins_3:
    epl_players = json.load(ins_3)

#with open('/Users/max/Desktop/Sports/fpl/json/transfer_history.json', 'r') as ins_4:
    #transfer = json.load(ins_4)

#transfer_df
st.write("FPL Downtown")

league_table = st.checkbox('League table')
statistics = st.checkbox('Weekly statistics')

if league_table:
    st.write(pd.DataFrame(obj))

if statistics:
    st.title('Transfer stats')
    #load from json
