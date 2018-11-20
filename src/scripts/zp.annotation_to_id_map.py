import pandas as pd

# IGNORE THIS FILE PLEASE, ONLY FOR REFERENCE. This code was used to remove some ambiguous ZP identifiers (74 in total)
# from Sebastians latest pipeline run.

def get_rows_with_duplicates(x,id_col):
    z = x[id_col]
    broken = x[x[id_col].isin(z[z.duplicated()])]
    return(broken)

original_id_map = "https://raw.githubusercontent.com/obophenotype/zebrafish-phenotype-ontology-build/master/zp.annot_sourceinfo"
current_id_map = "/ws/zebrafish-phenotype-ontology/src/curation/id_map.tsv"

zfin = "https://zfin.org/downloads/phenotype_fish.txt"
df = pd.read_csv(zfin, sep='\t', header=None)
functionalcolumns = pd.np.array([7,9,11,13,16,18,20])-1
d = df[functionalcolumns].drop_duplicates()
d.columns = ['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']
d = d.replace(pd.np.nan, "0", regex=True)
d = d.replace("nan", "0", regex=True)

# Generate ids
df_ids = pd.read_csv(original_id_map, sep='\t', header=None)
df_ids = df_ids[[0,3,2,4,7,6]]
df_ids.columns = ['iri','affected_entity_1_sub','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_super']
df_ids = df_ids.replace(pd.np.nan, "0", regex=True)
df_ids = df_ids.replace("nan", "0", regex=True)
df_ids = df_ids.drop_duplicates()

beforelen=len(df_ids)
df_ids = pd.merge(df_ids, d, on=['affected_entity_1_sub','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_super'], how='left')
afterlen=len(df_ids)
print("Before: "+str(beforelen)+", after: "+str(afterlen))
df_ids = df_ids.replace(pd.np.nan, "0", regex=True)
df_ids = df_ids.replace("nan", "0", regex=True)

df_ids=df_ids[['iri','affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']]
df_ids['id'] = df_ids.loc[:, df_ids.columns != 'iri'].astype(str).apply('-'.join, axis=1)
df_ids=df_ids[['iri','id']]


# Remove duplicates
c = get_rows_with_duplicates(df_ids,'iri')
duplicated_ids = set(c['iri'])
x=df_ids[~df_ids['iri'].isin(duplicated_ids)]
b = get_rows_with_duplicates(x,'id')
duplicated_ids.update(set(b['iri']))
x=df_ids[~df_ids['iri'].isin(duplicated_ids)]
y=df_ids[df_ids['iri'].isin(duplicated_ids)]
x.to_csv(current_id_map, sep = '\t', index=False,header=True)
y.to_csv(current_id_map+"_removed.tsv", sep = '\t', index=False,header=True)
