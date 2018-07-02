from time import time
import is24

df = is24.fetch_df(100, 20)
(expose_count, _) = df.shape
df.to_csv(f'data/is24_{expose_count}_{round(time() * 1000)}.csv')
