# Goal: we want to process ETH transfer data 
# Convert block num to time
# Note: This script takes several mins to run

import pandas as pd
import numpy as np 
from web3 import Web3
from datetime import datetime

# Setup api
api_key = "8b80cbd4ba434126965334366f3be5f6"
infura_url = "https://mainnet.infura.io/v3/{}".format(api_key)
web3 = Web3(Web3.HTTPProvider(infura_url))

df = pd.read_csv('data/eth_AssetTransfers_raw.csv')

# Loop through df
list1 = []

for x in df['blockNum']:
    # note that if you are using latest web3 package, try
    # list1.append(web3.eth.getBlock(x).timestamp)
    # Due to venv issue https://ethereum.stackexchange.com/questions/94046/web3-py-attributeerror-eth-object-has-no-attribute-get-block
    # I have to use the older version "get_block"
    list1.append(web3.eth.get_block(x).timestamp)

df['timestamp'] = list1

# convert time format
temp1 = []

for x in df['timestamp']:
    temp1.append(datetime.utcfromtimestamp(int(x)).strftime('%Y-%m-%d %H:%M:%S'))

df['time'] = temp1

df = df.drop(columns= ['Unnamed: 0'])

# Save the df with date output
df.to_csv('data/eth_AssetTransfers_date.csv')
