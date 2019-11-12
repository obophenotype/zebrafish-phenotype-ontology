import sys
import os
import pandas as pd

new_lables_file = sys.argv[2]
old_lables_file = sys.argv[1]
obsolete_template_file = sys.argv[3]

df_new_lables = pd.read_csv(new_lables_file, sep=',').dropna()
df_old_lables = pd.read_csv(old_lables_file, sep=',').dropna()
df_obsolete_template = pd.read_csv(obsolete_template_file, sep='\t')

# Preparing obsoletion pattern
new_zp_terms = list(set(df_new_lables['term'].unique().tolist()))
old_zp_terms = list(set(df_old_lables['term'].unique().tolist()))
obsolete = [x for x in old_zp_terms if x not in new_zp_terms]

print("New zp terms: {}".format(len(new_zp_terms)))
print("Old zp terms: {}".format(len(old_zp_terms)))
print("Obsolete zp terms: {}".format(len(obsolete)))
print("New sig: {}".format(len(df_new_lables)))
print("Old sig: {}".format(len(df_old_lables)))
print(df_old_lables.head())
df_obsolete = df_old_lables[~df_old_lables.ix[:,0].isin(new_zp_terms)]
df_obsolete = df_obsolete.drop_duplicates()
df_obsolete.columns = ['Ontology ID', 'Label']
print(df_obsolete.head())
df_obsolete['Label'] = 'obsolete ' + df_obsolete['Label'].astype(str)
df_obsolete['Obsolete'] = 'true'
df_obsolete['ZFIN Annotation'] = "Removed as part of a major revision session. Please contact us on https://github.com/obophenotype/zebrafish-phenotype-ontology/issues for suitable replacement terms."
print("Obsolete: {}".format(len(df_obsolete)))

df_obsolete_template = pd.concat([df_obsolete_template,df_obsolete], axis=0, ignore_index=True)
df_obsolete_template.sort_values(by ='Ontology ID',inplace=True)
df_obsolete_template.drop_duplicates().to_csv(obsolete_template_file, sep = '\t', index=False)