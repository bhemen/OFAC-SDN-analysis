"""
Read the parsed SDN list and extract the entries that correspond to addresses on known blockchains

Writes the output to tagged_addresses.csv

parse_sdn.py must be run first to convert the SDN list to an easily readable CSV
"""

from web3 import Web3
import base58
import pandas as pd
import coinaddrvalidator
import requests

chains = ["binancecoin",
"bitcoin",
"bitcoin-sv",
"bitcoin-cash",
"boscoin",
"cardano",
"cosmos",
"dashcoin",
"decred",
"dogecoin",
"eos",
"ethereum",
"ethereum-classic",
"ether-zero",
"groestlcoin",
"horizen",
"kusama",
"litecoin",
"neocoin",
"ontology",
"polkadot",
"ravencoin",
"ripple",
"stellar",
"tezos",
"tronix",
"vechain",
"zcash" ]



def isTronAddress(a):
	#https://developers.tron.network/docs/account
   
	is_valid = False
	if len(a) == 42 or (len(a) == 44 and a[0:2] == '0x'):
		is_valid = True
		try:
			int( a, 16 )
		except ValueError as ve:
			print( "Case 1" )
			print( e )
			is_valid = False
			pass

	if len(a) == 34 and a[0] == "T":
		is_valid = True
		try:
			base58.b58decode_check(a).hex().lower() 
		except Exception as e:
			print( 'Case 2' )
			print(e ) 
			is_valid = False
			pass
		   
	if is_valid:
		try:
			resp = requests.get(f"https://apilist.tronscan.org/api/account?address={a}")
		except Exception as e:
			return False

		if resp.status_code == 200:
			try:
				resp_json = resp.json()
			except Exception as e:
				return False
			if 'message' in resp_json:
				print( f"Tron returns message: {resp_json['message']}" )
				return False
			return True

	return False

#def isBitcoinAddress(a):
#	 #https://medium.com/coinmonks/bitcoin-address-validation-on-python-a0123ba3adb8
#	 try:
#		 base58Decoder = base58.b58decode(a).hex()
#		 prefixAndHash = base58Decoder[:len(base58Decoder)-8]
#		 checksum = base58Decoder[len(base58Decoder)-8:]
#	 except Exception as e:
#		 print( "Case 1" )
#		 print( e )
#		 return False
#	 if(checksum == prefixAndHash[:8]):
#		 return True
#	 else:
#		 print( "Failed checksum" )
#		 return False

def isBitcoinAddress(a):
	n = coinaddrvalidator.validate('bitcoin', a )
	return n.valid

def isEthereumAddress(a):
	try:
		Web3.toChecksumAddress(a)
	except Exception as e:
		return False
	 
	return True

def checkAddress(a):
	row = {'address': a }
	if not isinstance(a,float):
		for chain in chains:
			row.update( {chain: coinaddrvalidator.validate(chain, a ).valid } )
	return row
		

sdn_list = pd.read_csv('data/parsed_sdn.csv')

tagged_addresses = []
for i, r in sdn_list.iterrows():
	a = r.detail
	row = checkAddress(a) 
	row.update( {'names': r.names } )
	tagged_addresses.append(row)

df = pd.DataFrame( tagged_addresses )

for c in df.columns:
	if df[c].any() == False:
		print( f"Dropping {c}" )
		df.drop(c,axis='columns',inplace=True)

chains = list(set(chains).intersection(df.columns))
#print( df[df[chains].any(axis='columns')].head() )
print( df.address.head())
df = df[df[chains].any(axis='columns')]
print( df.address.head() )

#df = pd.DataFrame(tagged_addresses)
df.to_csv("data/tagged_addresses.csv",index=False)

