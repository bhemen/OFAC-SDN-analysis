# Goal: Collect upstream/downstream info from SDN address

import pandas as pd
import numpy as np 
import requests 
import json

df = pd.read_csv('data/tagged_addresses.csv')

eth_list = list(set(df.loc[(df['ethereum']==True) | 
                  (df['ethereum-classic']==True) |
                  (df['ether-zero']==True)]['address'].values.tolist()))

# Alchemy api
api = "GkbhJQByWbUI7hKEtwsoYJAPoOorwbyf"

url = "https://eth-mainnet.g.alchemy.com/v2/{}".format(api)

eth_trans = []

# Here, we loop through contract deployer to get multiple transfers

# 1）upstream (transferred to SDN)
for i in eth_list:
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "toAddress": "{}".format(i),
                "category": ["external"],
                "withMetadata": False,
                "excludeZeroValue": True,
                "maxCount": "0x3e8"
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    #####################################################
    # Pretty Printing
    # json_data = response.text 
    # obj = json.loads(json_data)
    # json_formatted_str = json.dumps(obj, indent=4)
    # print(json_formatted_str) 
    #####################################################
    # Certain json blocks would appear to be error, for example:
    # {
    # "jsonrpc": "2.0",
    # "id": 0,
    # "error": {
    #     "code": 429,
    #     "message": "alchemy_getAssetTransfers is a method with custom rate limits that you have exceeded.
    # }
    # in which the message is not true.
    # Thus, we need try-except block 
    try:
        for _trans in json.loads(response.text)['result']['transfers']:
            eth_trans.append(
                (
                _trans['blockNum'], _trans['hash'], _trans['from'],
                _trans['to'], _trans['value'],_trans['asset']
                )
            )
    except Exception:
        pass 

# 2) Downstream (transfers from SDN)
for i in eth_list:
    payload = {
        "id": 1,
        "jsonrpc": "2.0",
        "method": "alchemy_getAssetTransfers",
        "params": [
            {
                "fromBlock": "0x0",
                "toBlock": "latest",
                "category": ["external"],
                "withMetadata": False,
                "excludeZeroValue": True,
                "maxCount": "0x3e8",
                "fromAddress": "{}".format(i)
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    response = requests.post(url, json=payload, headers=headers)
    #####################################################
    # Pretty Printing
    # json_data = response.text 
    # obj = json.loads(json_data)
    # json_formatted_str = json.dumps(obj, indent=4)
    # print(json_formatted_str) 
    #####################################################
    try:
        for _trans in json.loads(response.text)['result']['transfers']:
            eth_trans.append(
                (
                _trans['blockNum'], _trans['hash'], _trans['from'],
                _trans['to'], _trans['value'],_trans['asset']
                )
            )
    except Exception:
        pass   

# Creating df from these data
eth_trans_df = pd.DataFrame(eth_trans, columns=['blockNum','hash','from','to','value','asset'])

# Save the raw output
eth_trans_df.to_csv('data/eth_AssetTransfers_raw.csv')
