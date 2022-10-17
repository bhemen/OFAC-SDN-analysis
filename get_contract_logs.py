from web3 import Web3
import progressbar
import pandas as pd
from utils import get_cached_abi

def getContractEvents( contract_address, target_events, outfile, start_block=1,end_block=None ):
	url="http://127.0.0.1:8545" #This should really only be run against a local node
	w3 = Web3(Web3.HTTPProvider(url))

	contract_address = Web3.toChecksumAddress(contract_address)
	latest_block = w3.eth.get_block_number()

	if end_block == None:
		end_block = latest_block
	
	batch_size = base_batch_size = 100

	max_retries = 5
	num_retries = 0
	abi = get_cached_abi(contract_address)

	contract = w3.eth.contract(address=contract_address,abi=abi)

	full_event_signatures = {}
	for evt in [obj for obj in abi if obj['type'] == 'event']:
		name = evt['name']
		types = [input['type'] for input in evt['inputs']]
		full = '{}({})'.format(name,','.join(types))
		#full_event_signatures[full] = Web3.keccak(text=full).hex()
		full_event_signatures[Web3.keccak(text=full).hex()] = full

	event_signatures = {}
	for evt in [obj for obj in abi if obj['type'] == 'event']:
		name = evt['name']
		types = [input['type'] for input in evt['inputs']]
		full = '{}({})'.format(name,','.join(types))
		#event_signatures[full] = Web3.keccak(text=full).hex()
		event_signatures[Web3.keccak(text=full).hex()] = name


	if target_events == 'all' or target_events == []:
		events = None
	else:
		events = [[k for k in event_signatures.keys() if event_signatures[k] in target_events]] #Note the double-list: https://ethereum.stackexchange.com/questions/90526/web3-py-topics
		if len(events[0]) < len(target_events):
			print( f"events = {events}" )
			print( f"target_events = {target_events}" )
			print( event_signatures )
			sys.exit(1)

	print( f"Scanning for events {events}" )
	print( f"Writing data to {outfile}" )

	df = pd.DataFrame()

	batch_start_block = start_block
	with progressbar.ProgressBar(max_value=end_block-start_block) as bar:
		while True:
			batch_end_block = min( batch_start_block + batch_size, latest_block )
			if batch_start_block >= min( latest_block, end_block ):
				break
			try:
				#lgs = w3.eth.get_logs( { 'fromBlock': start_block, 'toBlock': end_block, 'address': contract_address, 'topics': events } )
				lgs = w3.eth.get_logs( { 'fromBlock': batch_start_block, 'toBlock': batch_end_block, 'address': contract_address } )
			except Exception as e:
				print( "Error" )
				print( e )
				batch_size = max( batch_size // 2, 1 )
				num_retries += 1
				if num_retries == max_retries: 
					num_retries = 0
					with open(error_file,"a") as f:
						f.write(f"{start_block}\n" )
					start_block += 1
				continue

			if len(lgs) > 0:
				new_rows = processLogs(w3,contract,event_signatures,lgs)	
				df = pd.concat( [df, new_rows] )
				df.to_csv(outfile,index=False)
			
			batch_start_block = batch_end_block + 1
			batch_size = base_batch_size
			num_retries = 0
			bar.update(batch_end_block-start_block)

	df.to_csv(outfile,index=False)



def processLogs(w3,contract,event_signatures,lgs):
	rows = []
	for lg in lgs:
		row = {'address': lg.address, 'blockHash': lg.blockHash.hex(), 'blockNumber': lg.blockNumber, 'transactionHash': lg.transactionHash.hex(), 'data': lg.data }
		try:
			timestamp = w3.eth.get_block(lg.blockNumber).timestamp
			row['timestamp'] = timestamp
		except Exception as e:
			print( f"Failed to get timestamp" )
			print( e )
			pass
			

		if lg.topics[0].hex() in event_signatures.keys():
			event = event_signatures[lg.topics[0].hex()]
			event_obj = getattr( contract.events, event )
			logs = event_obj().processLog(lg)
			if 'args' in logs.keys():
				row.update( logs['args'] )
		else:
			print( f"Failed to process log" )
			event = lg.topics[0].hex()

		row['event'] = event

		try:
			tx = w3.eth.get_transaction(lg.transactionHash)
			row['msg.sender'] = tx['from']
		except Exception as e:
			row['msg.sender'] = None
	
		rows.append(row)

	mini_df = pd.DataFrame( rows )
	return mini_df
				

if __name__ == '__main__':
	deploy_block = start_block = 10926829
	contract_address = "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9" #AAVE token
	contract_address = "0x1f9840a85d5af5bf1d1762f925bdaddc4201f984" #UNI token

	contract_address = Web3.toChecksumAddress(contract_address)
	target_events = ['Transfer']

	outfile = "data/uni_token_logs.csv"

	getContractEvents( contract_address, target_events, outfile, deploy_block ,end_block=None )
