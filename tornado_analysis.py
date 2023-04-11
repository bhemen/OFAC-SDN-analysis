import pandas as pd
import glob 

path = 'data/tornado_pool/*.csv'

for fname in glob.glob(path):
    try: 
        df = pd.read_csv(fname)
        exposed = (df['event']=='Withdrawal') & (df['msg.sender'] == df['relayer'])
        exposed_perc = len(df.loc[exposed])/len(df)*100
    except:
        pass
    print(f"Pool: {fname[-42:-4]}\n Exposed Withdrawal: {exposed_perc:.2f}%")
