"""
Read the list of Tornado Cash addresses from parse_sdn.py
Find the Ethereum block number in which that contract was deployed (using Etherscan)

Save the output to tornado_deploys.csv
"""

from web3 import Web3
import progressbar
import pandas as pd
from utils import get_cached_abi, get_deploy_block
from get_contract_logs import getContractEvents
import time
import sys

filename = "tornado_addresses.csv"

df = pd.read_csv(filename)

addresses = df.detail.unique()

contracts = []
for addr in addresses:
	try:
		block = get_deploy_block(addr)	
	except Exception as e:
		block = None
	contracts.append( {'deploy_block': block, 'address': addr } )
	print( f"{addr} - {block}" )
	time.sleep(5)

df = pd.DataFrame(contracts)

df.to_csv("tornado_deploys.csv",index=False)


