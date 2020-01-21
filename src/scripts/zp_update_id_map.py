import pandas as pd
import copy
import sys
from zp_lib import zp_pipeline_config

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# This script takes the current ZFIN EQ annotations and assigns unique ZP identifiers to ones that do not have one yet.
# The outcome of this file is the id_map.tsv


current_id_map = sys.argv[1] # The current stable mapping between ZFIN post-composed EQ annotations and ZP identifiers
deprecated_id_map = sys.argv[2] #The file that contains all currently deprecated ZP classes, i.e. those ZP classes that were previously assigned to a ZFIN EQ statement, but have no corresponding one after the current run
reserved_ids = sys.argv[3] # This file contains a list of ALL ZP identifiers currently in use anywhere (deprecated or not). This is important to not assign a new EQ to a previously used ZP identifier
accession=int(sys.argv[4]) # The number from which we should start counting (if set to 1, ZP assignment resumes from the highest ZP identifier currently assigned

# Load ID MAP

id_map = pd.read_csv(current_id_map, sep='\t')

config = zp_pipeline_config(accession=accession,reserved_ids_file=reserved_ids, include_modifier = False)
d = config.load_zfin_phenotype_fish()

# Merge the fresh set of annotations with the current set of ZP identifiers
zfin_id_map_merged = pd.merge(d, id_map, on='id', how='left')
zfin_id_map_merged = zfin_id_map_merged.drop_duplicates()

# Make sure there are no duplicate ids.
broken = config.get_rows_with_duplicates(zfin_id_map_merged,'id')
if len(broken)>0:
    e = str(broken)
    #broken.to_csv("broken_idmap.tsv", sep = '\t', index=False)
    raise ValueError('There are postcomposed EQ annotations with more than 1 IRI: '+e)

# Compute next assignable id

# Computing new ZP identifiers where necessary
len_before = len(zfin_id_map_merged)
#print(d[['iri','id']].head(3))
zfin_id_map_merged = config.compute_missing_zp_ids(zfin_id_map_merged)

len_after = len(zfin_id_map_merged)

if len_after!=len_before:
    print("Length before assigning ids: "+str(len_before))
    print("Length after assigning ids: "+str(len_after))
    raise ValueError('The length of the dataframe has changed!')


#print(d[['iri','id']].head(3))

# Update ZFIN EQ id - ZP mapping
# zfin_id_map_merged contains currently all annotations in the ZFIN dump. After we have completed the matches
x = copy.deepcopy(zfin_id_map_merged[['iri','id_raw']])
x = x.rename(columns={'id_raw': 'id'})

# we combine them with the previous version of the id map to see whether anything got lost
id_map = pd.concat([id_map,x])
x = None
id_map = id_map.drop_duplicates() # id_map now contains all mappings (old and new)
print("ID MAP size after merging with zfin"+str(len(id_map)))


# Create a copy of the old mappings, label as 'current'
y = copy.deepcopy(zfin_id_map_merged[['iri','id_raw']])
y = y.rename(columns={'id_raw': 'id'})
y['current'] = 'current'
# Merge the complete id_map (containing old and new mappings) with the labelled old results
z = pd.merge(id_map, y, on=['id','iri'], how='left')
# deprecated results are those that contain at least one NULL value (which can only be in the 'current' columns)

df_deprecated_id_map = z[pd.isnull(z).any(axis=1)]

# Exporting the files again
df_deprecated_id_map.sort_values(by ='iri',inplace=True)
df_deprecated_id_map=df_deprecated_id_map.reindex(['iri', 'id','current'], axis=1)
df_deprecated_id_map.to_csv(deprecated_id_map, sep = '\t', index=False)

id_map.sort_values(by ='iri',inplace=True)
id_map=id_map.reindex(['iri', 'id'], axis=1)
id_map.to_csv(current_id_map, sep = '\t', index=False)

# not strictly speaking necessary, but why not just amend reserved_ids so they contain the newly minted ones as well?
config.dump_reserved_ids(id_map,reserved_ids)

print("Updating the ZP to ZFIN EQ mappings complete!")