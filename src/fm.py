import pandas as pd
import numpy as np 
import sklearn
import lightgbm
import statsmodels
import matplotlib

train_df = pd.read_json('data/train.json', orient='records')
test_df = pd.read_json('data/test.json', orient='records')

print(f"Shape of train_df is:", train_df)

train_df