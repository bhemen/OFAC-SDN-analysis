"""
Utilities for getting contract ABIs from Etherscan and caching them locally
"""

import requests
import json
import time
from web3 import Web3
import os

ABI_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getabi&address='
DEPLOY_ENDPOINT = 'https://api.etherscan.io/api?module=contract&action=getcontractcreation&contractaddresses='

if not os.path.exists('abis'):
	os.makedirs('abis')

_cache_file = "abis/cached_abis.json"

_cache = dict()

def get_deploy_block(contract_address,retry=0):
	max_retries = 2 
	try:
		response = requests.get( f"{DEPLOY_ENDPOINT}{contract_address}", timeout = 20 )	
	except requests.exceptions.ReadTimeout as e:
		if retry < max_retries:
			print( f"Timeout, trying again" )
			return get_deploy_block(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get deployment info" )
			return None
	except Exception as e:
		print( f"Failed to get {address} from {DEPLOY_ENDPOINT}" )
		print( e )
		return None

	try:
		response_json = response.json()
		#deploy_json = json.loads(response_json['result'])
		deploy_json = response_json['result']
	except Exception as e:
		print( f"Failed to load json" )
		print( response )
		print( dir(response) )
		print( response.content )
		print( response.json() )
		return None
		print( e )
		if retry < max_retries:
			print( f"JSON error, trying again" )
			return fetch_abi(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get deployment" )
			return None

	if isinstance(deploy_json,str):
		print( "It's a string!" )
		print( deploy_json )
		return None
	deploy_txs = [r['txHash'] for r in deploy_json]
	#CONVERT TO BLOCK NUMBERS
	url="http://127.0.0.1:8545" #This should really only be run against a local node
	w3 = Web3(Web3.HTTPProvider(url))
	blocks = [w3.eth.get_transaction(tx_hash).blockNumber for tx_hash in deploy_txs]
	if len(blocks) == 1:
		return blocks[0]
	else:
		return blocks


def get_rarible_721():
	base_url = "https://raw.githubusercontent.com/rarible/protocol-contracts/master/deploy/build/contracts/"
	contracts = ['ERC721RaribleMinimal.json',
				'ERC721BaseMinimal.json',
				'ERC721LazyMinimal.json',
				'ERC721URI.json',
				'RoyaltiesV2.json',
				'RoyaltiesV2Upgradeable.json' ]

	abi = {}
	for c in contracts:
		try:
			c_abi= json.loads(requests.get(f"{base_url}{c}").text)['abi']
		except Exception as e:
			print( f"Failed to get {c}" )
			continue
		abi.update( { x['name']: x for x in c_abi } ) #Deduplicate on name field
	abi = list( abi.values() )
	
	return abi	

def fetch_abi(contract_address,retry=0):
	"""
	get abi for contract address from etherscan
	"""

	if contract_address == "rarible_erc721":
		print( f"Getting Rarible ERC721 Contract Info" )
		abi = get_rarible_721()
		return abi

	if contract_address == "0x2e59A20f205bB85a89C53f1936454680651E618e":
		return fetch_abi("0x72fb5253ad16307b9e773d2a78cac58e309d5ba4") #Lido governance proxy

	if contract_address == "0x7Fc66500c84A76Ad7e9c93437bFc5Ac33E2DDaE9":
		return fetch_abi("0xea86074fdac85e6a605cd418668c63d2716cdfbc") #Aave token is a proxy (https://docs.aave.com/developers/v/1.0/developing-on-aave/the-protocol/aave-token)

	if contract_address == "0x9757F2d2b135150BBeb65308D4a91804107cd8D6": #Rarible exchange
		abi_url = "https://raw.githubusercontent.com/rarible/protocol-contracts/master/deploy/build/contracts/ExchangeV2.json"
		try:
			abi = json.loads(requests.get(abi_url).text)['abi']
		except Exception as e:
			print( "Failed to get Rarible Exchange abi" )
			return None	
		return abi


	if contract_address == "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48": #USDC
		usdc_abi = "https://gist.githubusercontent.com/Ankarrr/570cc90f26ef7fb6a2a387612db80ceb/raw/e4e6dd3fc2d572f8999b06adc557b3edbbadf930/usdc-abi.json"
		try:
			abi = json.loads(requests.get(usdc_abi).text)
		except Exception as e:
			print( "Failed to get USDC abi" )
			return None	
		return abi

	aTokens = ["0xFFC97d72E13E01096502Cb8Eb52dEe56f74DAD7B"]
	if contract_address in aTokens: #aave a-tokens are interest-bearing ERC-20 tokens
		atoken_abi = "https://raw.githubusercontent.com/aave/aave-protocol/master/abi/AToken.json"
		try:
			abi = json.loads(requests.get(atoken_abi).text)
		except Exception as e:
			print( "Failed to get aToken abi" )
			return None	
		return abi

	max_retries = 1
	try:
		response = requests.get( f"{ABI_ENDPOINT}{contract_address}", timeout = 20 )	
	except requests.exceptions.ReadTimeout as e:
		if retry < max_retries:
			print( f"Timeout, trying again" )
			return fetch_abi(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get abi" )
			return None
	except Exception as e:
		print( f"Failed to get {address} from {ABI_ENDPOINT}" )
		print( e )
		return None

	try:
		response_json = response.json()
		abi_json = json.loads(response_json['result'])
	except Exception as e:
		print( f"Failed to load json" )
		print( e )
		if retry < max_retries:
			print( f"JSON error, trying again" )
			return fetch_abi(contract_address,retry+1)
		else:
			print( f"Retried {retry} times" )
			print( f"Failed to get abi" )
			return None
	#print( type( abi_json ) ) #list
	#print( type( abi_json[0] ) ) #dict
	return abi_json

def get_cached_abi(contract_address,abikw=""):
	"""Per process over-the-network ABI file retriever"""

	try:
		with open(_cache_file) as f:
			_cache = json.load(f)
	except Exception as e:
		_cache = dict()
	
	if abikw:
		search_for = abikw
	else:
		search_for = contract_address
	
	abi = _cache.get(search_for)

	if not abi:
		abi = fetch_abi(search_for)
		if abi is not None:
			_cache[search_for] = abi
			with open(_cache_file, 'w') as outfile:
				json.dump(_cache, outfile,indent=2)
		
	return abi

def create_contract(web3,address):
	abi = get_cached_abi(address)
	#print( abi )
	contract = web3.eth.contract(address, abi=abi)
	return contract

#if __name__ == '__main__':
#	print( get_rarible_721() )
