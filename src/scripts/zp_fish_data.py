import pandas as pd
import numpy as np
import copy
import sys

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

id_map = sys.argv[1] # The current ZP-ZFIN EQ id map
zp_zfin_mappings = sys.argv[2] # The desired location for the resulting gene annotation to ZP mappings

tsv = 'https://zfin.org/downloads/phenotype_fish.txt'

# LOAD ZFIN GENE ANNOTATION DATA
df_zfin = pd.read_csv(tsv, sep='\t', header=None)
print("Number of gene annotations: "+str(len(df_zfin)))
print(df_zfin.shape)

#xxx=copy.deepcopy(df_zfin)
#df_zfin=copy.deepcopy(xxx)
# LOAD CURRENT ZP-ZFIN-EQ MAP

id_map = pd.read_csv(id_map, sep='\t')
print(id_map.shape)

# Generate ID string in ZFIN Gene annotation data and merge with ID MAP to get corresponding ZP identifier
functionalcolumns = np.array([7,9,11,13,15,16,18,20])-1
df_zfin.update(df_zfin[functionalcolumns].fillna('0'))
print(len(df_zfin))
df_zfin['id'] = df_zfin[functionalcolumns].astype(str).apply('-'.join, axis=1)
df_zfin = pd.merge(df_zfin, id_map, on='id', how='left')
print(len(df_zfin))
df_zfin[functionalcolumns] = df_zfin[functionalcolumns].replace('^0$', '', regex=True)
print(len(df_zfin))

cols = ['Fish ID','Fish Name','Start Stage ID','Start Stage Name',	'End Stage ID',	'End Stage Name', 'Affected Structure or Process 1 subterm ID',
        'Affected Structure or Process 1 subterm Name',	'Post-composed Relationship ID', 'Post-composed Relationship Name',
        'Affected Structure or Process 1 superterm ID',	'Affected Structure or Process 1 superterm Name', 'Phenotype Keyword ID',
        'Phenotype Keyword Name', 'Phenotype Tag', 'Affected Structure or Process 2 subterm ID',
        'Affected Structure or Process 2 subterm name', 'Post-composed Relationship (rel) ID', 'Post-composed Relationship (rel) Name',
        'Affected Structure or Process 2 superterm ID',	'Affected Structure or Process 2 superterm name',
        'Publication ID', 'Environment ID','ZFIN EQ ID','IRI']
df_zfin.columns = cols
df_zfin.to_csv(zp_zfin_mappings, sep = '\t', index=False)

print("Exporting ZP-ZFIN-EQ annotations complete!")
