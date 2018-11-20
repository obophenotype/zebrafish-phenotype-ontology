import pandas as pd
import copy

#reserved_ids = sys.argv[3]

# The current stable mapping between ZFIN post-composed EQ annotations and ZP identifiers
current_id_map = "/ws/zebrafish-phenotype-ontology/src/curation/id_map.tsv"
deprecated_id_map = "/ws/zebrafish-phenotype-ontology/src/curation/deprecated_id_map.tsv"
reserved_ids = "/ws/zebrafish-phenotype-ontology/src/curation/reserved_iris.txt"
accession=1000000
prefix = "ZP:"
zfin = "https://zfin.org/downloads/phenotype_fish.txt"

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

# For the following function to work properly it is important to note that there should be absolutely no columns in teh tsv file other than the defi
# defined_class and columns whos names end with _label other than the ones that contribute to the identity of the entity in question

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

# Fixed parameters
maxid = 9999999 # THE maximum integer the current OBO IRI space allows (ZP_9999999).

# Load ID MAP
df_ids = pd.read_csv(current_id_map, sep='\t')
# Get and clean complete set of currently assigned ZP ids (can be generated using the respective make goal in src/curation/Makefile
with open(reserved_ids) as f:
    ids = f.readlines()
ids = [x.strip() for x in ids]
ids = [s for s in ids if s.startswith(prefix)]

# The ZFIN raw data used to create the annotations
df = pd.read_csv(zfin, sep='\t', header=None)

# Get the relevant subset from the raw data
# These are the original indices as labelled on https://zfin.org/downloads. We added +1 to accomodate that python starts counting columns at 0
functionalcolumns = pd.np.array([7,9,11,13,16,18,20])-1
d = df[functionalcolumns].drop_duplicates()
d.columns = ['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']

# For the ID generation process, we decided to replace empty or NAN values with 0
d = d.replace(pd.np.nan, "0", regex=True)
d = d.replace("nan", "0", regex=True)
d['id'] = d.apply('-'.join, axis=1)

# Merge the fresh set of annotations with the current set of ZP identifiers
x = pd.merge(d, df_ids, on='id', how='left')

# Make sure there are no duplicate ids.
broken = get_rows_with_duplicates(x,'id')
if len(broken)>0:
    print("There are postcomposed EQ annotations with more than 1 id!")
    print(broken[['id','iri']])


#d[pd.isnull(d).any(axis=1)].head()

# compute next assignable id
startid = get_highest_id(ids)
if startid<accession:
    startid=accession

# Computing new ZP identifiers where necessary
a = copy.deepcopy(x)
d = copy.deepcopy(a)
print(str(len(d)))
print(d[['iri','id']].head(3))
d = compute_missing_zp_ids(d)
print(str(len(d)))
print(d[['iri','id']].head(3))

# Update ZFIN EQ id - ZP mapping
# d contains currently all annotations in the ZFIN dump
x = copy.deepcopy(d[['iri','id']])
print(str(len(x)))
# we combine them with the old id map to see whether anything got lost
df_ids = pd.concat([df_ids,x])
print(str(len(df_ids)))
df_ids = df_ids.drop_duplicates() # df_ids now contains all mappings (old and new)
print(str(len(df_ids)))

y = copy.deepcopy(d[['iri','id']])
y['current'] = 'current'
z = pd.merge(df_ids, y, on=['id','iri'], how='left')
deprecated = z[pd.isnull(z).any(axis=1)]

# Exporting the files again
deprecated.to_csv(deprecated_id_map, sep = '\t', index=False)
df_ids.to_csv(current_id_map, sep = '\t', index=False)

# not strictly speaking necessary, but why not just ammend reserved_ids so they contain the newly minted ones as well?
ids=list(set(ids+df_ids['iri'].tolist()))
with open(reserved_ids, 'w') as f:
    for item in ids:
        f.write("%s\n" % item)
