import pandas as pd
import copy
import sys

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# This script takes the current ZFIN EQ annotations and assigns unique ZP identifiers to ones that do not have one yet.
# The outcome of this file is the id_map.tsv


current_id_map = sys.argv[1] # The current stable mapping between ZFIN post-composed EQ annotations and ZP identifiers
deprecated_id_map = sys.argv[2] #The file that contains all currently deprecated ZP classes, i.e. those ZP classes that were previously assigned to a ZFIN EQ statement, but have no corresponding one after the current run
reserved_ids = sys.argv[3] # This file contains a list of ALL ZP identifiers currently in use anywhere (deprecated or not). This is important to not assign a new EQ to a previously used ZP identifier
accession=int(sys.argv[4]) # The number from which we should start counting (if set to 1, ZP assignment resumes from the highest ZP identifier currently assigned

# Fixed parameters
startid = 0 # will be changed but needs to be declared
maxid = 9999999 # THE maximum integer the current OBO IRI space allows (ZP_9999999).
prefix = "ZP:"
zfin = "https://zfin.org/downloads/phenotype_fish.txt" # The ZFIN EQ data
#zfin = "/data/phenotype_fish.txt"

# METHODS
def get_highest_id(ids):
    global prefix
    x = [i.replace(prefix, "").lstrip("0") for i in ids]
    x = [s for s in x if s!='']
    if len(x)==0:
        x=[0,]
    x = [int(i) for i in x]
    return max(x)

def generate_id(i):
    global startid, maxid, prefix
    if isinstance(i,str):
        if i.startswith(prefix):
            return i
    startid = startid + 1
    if startid>maxid:
        raise ValueError('The ID space has been exhausted (maximum 10 million). Order a new one!')
    id = prefix+str(startid).zfill(7)
    return id

def compute_missing_zp_ids(df):
    df['iri'] = [generate_id(i) for i in df['iri']]
    return(df)

def get_rows_with_duplicates(x,id_col):
    z = x[id_col]
    broken = x[x[id_col].isin(z[z.duplicated()])]
    return(broken)

def split_eq(dfs):
    df = dfs['id'].str.split('-', expand=True).reindex(columns=pd.np.arange(7))
    xs = pd.concat([dfs, df], axis=1).replace({'0': pd.np.NaN})
    return(xs)
    
def correct_id(id):
    #0-0-GO:0001501-PATO:0000001-0-0-0
    #if id.startswith("0-0-GO:") and id.endswith("-PATO:0000001-0-0-0"):
    #    id = id.replace("PATO:0000001","PATO:0001236")
    return id


# Load ID MAP
id_map = pd.read_csv(current_id_map, sep='\t')

# Get and clean complete set of currently assigned ZP ids (can be generated using the respective make goal in src/curation/Makefile
with open(reserved_ids) as f:
    ids = f.readlines()
ids = [x.strip() for x in ids]
ids = [s for s in ids if s.startswith("ZP:")]

# Load the ZFIN EQ data
df = pd.read_csv(zfin, sep='\t', header=None)
print("Load data complete... ZFIN size: "+str(len(df)))


# Get the relevant subset from the raw ZFIN EQ data
# These are the original indices as documented on https://zfin.org/downloads. We added +1 to accomodate that python starts counting columns at 0
functionalcolumns = pd.np.array([7,9,11,13,16,18,20])-1
d = df[functionalcolumns].drop_duplicates()
d.columns = ['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']

# For the ID generation process, we decided to replace empty or NAN values with 0
d = d.replace(pd.np.nan, "0", regex=True)
d = d.replace("nan", "0", regex=True)
d = d.replace("http://purl.obolibrary.org/obo/", "")
d = d.replace("_", ":")
d['id_raw'] = d.apply('-'.join, axis=1) #generate a unique id string
d['id'] = d['id_raw'].apply(lambda x: correct_id(x))
#print(d[d['id_raw']!=d['id']].head())

# Merge the fresh set of annotations with the current set of ZP identifiers
zfin_id_map_merged = pd.merge(d, id_map, on='id', how='left')
zfin_id_map_merged = zfin_id_map_merged.drop_duplicates()
# Make sure there are no duplicate ids.
broken = get_rows_with_duplicates(zfin_id_map_merged,'id')
if len(broken)>0:
    e = str(broken)
    #broken.to_csv("broken_idmap.tsv", sep = '\t', index=False)
    raise ValueError('There are postcomposed EQ annotations with more than 1 IRI: '+e)

# Compute next assignable id
startid = get_highest_id(ids)
if startid<accession:
    startid=accession

# Computing new ZP identifiers where necessary
len_before = len(zfin_id_map_merged)
#print(d[['iri','id']].head(3))
zfin_id_map_merged = compute_missing_zp_ids(zfin_id_map_merged)
len_after = len(zfin_id_map_merged)

if len_after!=len_before:
    print("Length before assigning ids: "+str(len_before))
    print("Length after assigning ids: "+str(len_after))
    raise ValueError('The length of the dataframe has changed!')


#print(d[['iri','id']].head(3))

# Update ZFIN EQ id - ZP mapping
# d contains currently all annotations in the ZFIN dump. After we have completed the matches
# we now use the original id again (the one where pato qualities were not corrected)
x = copy.deepcopy(zfin_id_map_merged[['iri','id_raw']])
x = x.rename(columns={'id_raw': 'id'})
print("Length after subsetting: "+str(len(x)))
# we combine them with the previous version of the id map to see whether anything got lost
id_map = pd.concat([id_map,x])
x = None
print(str(len(id_map)))
id_map = id_map.drop_duplicates() # id_map now contains all mappings (old and new)
print(str(len(id_map)))


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
ids=list(set(ids+id_map['iri'].tolist()))
with open(reserved_ids, 'w') as f:
    for item in ids:
        f.write("%s\n" % item)

print("Updating the ZP to ZFIN EQ mappings complete!")