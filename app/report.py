one_results_list = []
gw = 9

for item in participants_json['entry'].values():
    one_results_list.append(get_participant_entry(item, gw))

one_df = pd.DataFrame(one_results_list)
o_df = one_df[~one_df['players'].isna()]
o_df

o_df['points_breakdown'] = o_df['players'].map(lambda x: [get_points(y, gw, df) for y in x.split(",")])
o_df['captain_points'] = o_df['captain'].map(lambda x: get_points(x, gw, df) * 2)
o_df['vice_captain_points'] = o_df['vice_captain'].map(lambda x: get_points(x, gw, df))
o_df['rank'] = o_df['total_points'].rank(ascending=False)
o_df['rank'] = o_df['rank'].map(int)

row = get_gw_transfers(participants_json['entry'].values(), 9)
f = pd.DataFrame(row)
f = f.T

#f.reset_index()
#f.drop(axis ='Index', index= 'entry_id', inplace= True)

f['transfer_points_in'] = f['element_in'].map(lambda x: sum([get_points(y, gw,df) for y in x]))
f['transfer_points_out'] = f['element_out'].map(lambda x:sum([get_points(y, gw,df) for y in x]))


o_df['entry'] = o_df['entry'].astype(int)
o_df.rename(columns={'entry':'entry_id'}, inplace= True)

f['transfers'] = f['element_out'].map(lambda x: len(x))
f['delta'] = f['transfer_points_in'] - f['transfer_points_out']
f.reset_index(inplace= True)
f.rename(columns= {'index': 'entry_id'}, inplace= True)

f = o_df.merge(f, on='entry_id', how='right')


counts = f['element_out'].value_counts().reset_index().to_dict('list')
most_transf_out = [(counts['element_out'][i], counts['index'][i]) for i in range(3)]
least_transf_out = [(counts['element_out'][-i], counts['index'][-i]) for i in range(1,4)]

counts = f['element_in'].value_counts().reset_index().to_dict('list')

most_transf_in = [(counts['element_in'][i], counts['index'][i]) for i in range(3)]
least_transf_in = [(counts['element_in'][-i], counts['index'][-i]) for i in range(1,4)] #because -0 == 0

captain = o_df['captain'].value_counts().to_dict()
chips = o_df['active_chip'].value_counts().to_dict()


best_transf_in = get_player(no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_out'].values[0][0])
best_transf_out = get_player(no_chips[no_chips['delta'] == max(no_chips['delta'])]['element_in'].values[0][0])
best_transf_points = max(no_chips['delta'])

worst_transf_in = get_player(no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_out'].values[0][0])
worst_transf_out = get_player(no_chips[no_chips['delta'] == min(no_chips['delta'])]['element_in'].values[0][0])
worst_transf_points = min(no_chips['delta'])

#write to json

