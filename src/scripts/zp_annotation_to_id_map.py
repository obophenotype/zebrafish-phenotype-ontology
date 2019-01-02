import pandas as pd
import sys

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# Once the first version of ZP is vetted and accepted, this file should NOT BE RUN EVER again. It was only necessary
# as a first step to migrate the old ZP ids defined here: https://github.com/obophenotype/zebrafish-phenotype-ontology-build

def get_rows_with_duplicates(x,id_col):
    z = x[id_col]
    broken = x[x[id_col].isin(z[z.duplicated()])]
    return(broken)

original_id_map = "https://raw.githubusercontent.com/obophenotype/zebrafish-phenotype-ontology-build/master/zp.annot_sourceinfo"
zfin = "https://zfin.org/downloads/phenotype_fish.txt"

current_id_map = sys.argv[1]
#current_id_map = "/ws/zebrafish-phenotype-ontology/src/curation/id_map.tsv"

# Step 1: Extract ZFIN EQ annotations from phenotype_fish.txt annotation data available at ZFIN.
# As the stable ids will be generated using the character '0' whenever an EQ annotion slot is empty
# this is set as well.
#zfin = "/data/phenotype_fish.txt"
df = pd.read_csv(zfin, sep='\t', header=None)
functionalcolumns = pd.np.array([7,9,11,13,16,18,20])-1
d = df[functionalcolumns].drop_duplicates()
d.columns = ['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']
d = d.replace(pd.np.nan, "0", regex=True)
d = d.replace("nan", "0", regex=True)

# Step 2: Load original ZP identifier map and replace empty columns with the character 0 (as before for the ZFIN data)
df_ids = pd.read_csv(original_id_map, sep='\t', header=None)
df_ids = df_ids[[0,3,2,4,7,6]]
df_ids.columns = ['iri','affected_entity_1_sub','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_super']
df_ids = df_ids.replace(pd.np.nan, "0", regex=True)
df_ids = df_ids.replace("nan", "0", regex=True)
df_ids = df_ids.drop_duplicates()

# Step 3: Merge the ZFIN EQ data into the current ZP id map, using the 5 entity columns (PATO, entity1sub, entity1super, entity2sub, entity2super)
# The sole purpose for loading the ZFIN EQs is to merge back the two RELATION columns that are not present in the original ZP identifier map.
beforelen=len(df_ids)
df_ids = pd.merge(df_ids, d, on=['affected_entity_1_sub','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_super'], how='left')
afterlen=len(df_ids)
print("Before: "+str(beforelen)+", after: "+str(afterlen))
df_ids = df_ids.replace(pd.np.nan, "0", regex=True)
df_ids = df_ids.replace("nan", "0", regex=True)
df_ids=df_ids[['iri','affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']]

# Step 4: From the 7 EQ columns, generate a single id string by concating tall column values with a dash (-)
df_ids['id'] = df_ids.loc[:, df_ids.columns != 'iri'].astype(str).apply('-'.join, axis=1)


# Step 5: Filtering and Cleaning

# Filtering out ZP records that, in the old pipeline, had a corresponding ZFIN EQ annotation, but do not have anymore
# We can recognise them here easily because our new dataframe does not contain RELATIONS after the merge with the ZFIN EQ data
# We permanently store the results as tsv and recommend to avoid generating new ZP ids for those in case any tool still relies on the old one
no_rel=df_ids[((df_ids['affected_entity_1_rel']=='0') & (df_ids['affected_entity_1_sub']!='0'))|((df_ids['affected_entity_2_rel']=='0') & (df_ids['affected_entity_2_sub']!='0'))]
incomplete_records = set(no_rel['iri'])
df_ids=df_ids[['iri','id']]
df_incomplete=df_ids[df_ids['iri'].isin(incomplete_records)]
df_incomplete.to_csv(current_id_map+"_removed_incomplete.tsv", sep = '\t', index=False,header=True)
df_ids = df_ids[~df_ids['iri'].isin(incomplete_records)]

# Filtering out ZP records for which there are more than one corresponding EQ definitions (ZP:1 -> ZFINEQ1, ZP:1 -> ZFINEQ2).
# This is likely a bug. The EQ definitons referenced in such a way will simply get assigned new, unambiguous identifiers
c = get_rows_with_duplicates(df_ids,'iri')
duplicated_ids = set(c['iri'])
x=df_ids[~df_ids['iri'].isin(duplicated_ids)]

# Filtering out ZP records for which there are corresponding EQ definitions with more than one ZP id (ZP:1 -> ZFINEQ1, ZP:2 -> ZFINEQ1).
# This is likely a bug. The EQ definitons referenced in such a way will simply get assigned new, unambiguous identifiers
b = get_rows_with_duplicates(x,'id')
duplicated_ids.update(set(b['iri']))

# Export the final id_map.tsv and a record of the ids excluded. We recommend to not re-use these identifiers again
x=df_ids[~df_ids['iri'].isin(duplicated_ids)]
y=df_ids[df_ids['iri'].isin(duplicated_ids)]
x.to_csv(current_id_map, sep = '\t', index=False,header=True)
y.to_csv(current_id_map+"_removed_ambiguous.tsv", sep = '\t', index=False,header=True)
print("Migrating old ID map to new complete!")
