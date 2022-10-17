import pandas as pd

df = pd.read_csv("tagged_addresses.csv")

chains = list( set(df.columns).difference(['address','names']) )

chain_stats = {}

for c in chains:
	cdf = df[df[c]][['address','names']]
	if df.shape[0] == 1:
		print( f"{cdf.shape[0]} entry for chain {c}" )
	else:
		print( f"{cdf.shape[0]} entries for chain {c}" )
	chain_stats.update( {c:cdf.shape[0]} )
	print( cdf )
	print( "\n======================================\n" )


for c,v in chain_stats.items():
	print( f"{c} - {v} entries" )


#tornado = pd.read_csv("tornado_addresses.csv")
#
#for a in tornado.detail:
#	if len(df[df['address']==a]['ethereum']) > 0 and df[df['address']==a]['ethereum'].all():
#		print( f"Address {a} is a valid Ethereum address" )
#	else:
#		print( f"Error: a tornado cash address was *not* tagged as a valid Ethereum address" )
#	print( df[df['address']==a] )
