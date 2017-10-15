import pandas as pd
import re


df = pd.read_csv('testCCIvP.csv', sep=",")
results_df = pd.read_csv('testCCIvPResults.csv', header=0, index_col=0)
#print results_df
results_dict = {'ROW_ID': 316238, 'SUBJECT_ID': 20}
test = pd.DataFrame(results_dict, columns=results_df.columns, index=[0])
results_df = results_df[results_df['ROW_ID'] != 316238]
results_df = results_df.append(results_dict, ignore_index=True)
print results_df

#print results_df.loc[results_df['ROW_ID'] == 316238].replace(to_replace=, value=pd.Series(results_dict))
