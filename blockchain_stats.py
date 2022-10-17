import pandas as pd

df = pd.read_csv("data/tagged_addresses.csv")

chains = list( set(df.columns).difference(['address','names']) )

chain_names = {chain:chain.capitalize() for chain in chains}
chain_names['tronix'] = 'Tron'
chain_names['eos'] = 'EOS'

totals = pd.DataFrame(df[chains].sum(axis=0)).reset_index()
totals.columns = ['chain','count']
totals.sort_values('count',ascending=False,inplace=True)
totals.chain = totals.chain.apply( lambda x: chain_names[x] )
print( totals )

