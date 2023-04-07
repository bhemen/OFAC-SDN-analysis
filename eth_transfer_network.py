# Goal: get some basic info and make a network

import pandas as pd
import networkx as nx
from matplotlib.pyplot import figure
import matplotlib.pyplot as plt

tag_df = pd.read_csv('data/tagged_addresses.csv')

# Have the list handy
eth_list = list(set(tag_df.loc[(tag_df['ethereum']==True) | 
                  (tag_df['ethereum-classic']==True) |
                  (tag_df['ether-zero']==True)]['address'].values.tolist()))

df = pd.read_csv('data/eth_AssetTransfers_date.csv')

################################
# Basic info
downstream = df.loc[df['from'].isin(eth_list)]
upstream = df.loc[df['to'].isin(eth_list)]
print(f'numbers of transfers: {len(df)}\nnumber of downstream: {len(downstream)}\nnumber of upstream: {len(upstream)}')
# ???This does not make sense, downstream and upstream does not add up???


#################################
# Network 

# Create the graph from dataframe
g = nx.from_pandas_edgelist(df, "from", "to")

# Specify the layout
pos=nx.spring_layout(g)

# Assign colors to these 71 SDN
color_map = []
for node in g:
    if node in eth_list:
        color_map.append('red')
    else:
        color_map.append('blue')

# Set node sizes based on their numbers of transfers
node_sizes = []
for node in g.nodes():
    node_sizes.append(df['from'].values.tolist().count(node))

node_sizes = [i*2+1 for i in node_sizes]


# Draw the network
plt.figure(figsize=(50,50)) 
nx.draw_networkx_nodes(g,pos,node_color=color_map, node_size=node_sizes)
nx.draw_networkx_edges(g,pos)

plt.box(False)
plt.show()
