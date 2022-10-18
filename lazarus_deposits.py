import pandas as pd

df = pd.read_csv('data/parsed_sdn.csv')

lazarus_addresses = df[df.names.str.find('Lazarus')>=0]['detail'].unique()

print( lazarus_addresses )
