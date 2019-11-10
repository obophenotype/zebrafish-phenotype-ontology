import sys
import os
import pandas as pd

table1 = sys.argv[1]
table2 = sys.argv[2]
columns_string = sys.argv[3]
table_out = sys.argv[4]

columns = columns_string.split(",")
df1 = pd.read_csv(table1, sep='\t')
df2 = pd.read_csv(table2, sep='\t')
#print(columns)
#print(df1)
#print(df2)

df_out = pd.merge(df1, df2,  how='outer', left_on=columns, right_on = columns)

#print(df_out)
df_out.to_csv(table_out, sep = '\t', index=False)
