from web3 import Web3
import progressbar
import pandas as pd
from utils import get_cached_abi, get_deploy_block
from get_contract_logs import getContractEvents
import time

df = pd.read_csv("data/tornado_deploys.csv")
df = df.dropna(axis=0)
df = df.astype({'deploy_block':int} )

target_events = 'all'

for i,row in df.iterrows():
	print( f"{row.deploy_block} - {row.address}" )
	outfile = f"data/{row.address}.csv"
	getContractEvents( row.address, target_events, outfile, row.deploy_block,end_block=None )

#
#
#mkr_chief = "0x0a3f6849f78076aefaDf113F5BED87720274dDC0"
#deploy_block = 11327777 


