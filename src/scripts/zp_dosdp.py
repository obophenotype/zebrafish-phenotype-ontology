import pandas as pd
import sys
import os

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# This scripts takes the current id map and assigns ZP ids to one of the ZFIN default patterns

# The current stable mapping between ZFIN post-composed EQ annotations and ZP identifiers
#current_id_map = "/ws/zebrafish-phenotype-ontology/src/curation/id_map.tsv"
#pattern_data = "/ws/zebrafish-phenotype-ontology/src/patterns/data/auto/"
#pattern_assignments = "/ws/zebrafish-phenotype-ontology/src/curation/pattern_assignments.tsv"

current_id_map = sys.argv[1]
pattern_data = sys.argv[2]
deprecated_id_map = sys.argv[3]
pattern_assignments = sys.argv[4]
zp_labels = sys.argv[5]

prefix = "ZP:"
pbase="https://raw.githubusercontent.com/obophenotype/zebrafish-phenotype-ontology/master/src/patterns/dosdp-patterns/"
ubase="https://raw.githubusercontent.com/obophenotype/upheno/master/src/patterns/"

# METHODS

def get_rows_with_duplicates(x,id_col):
    z = x[id_col]
    broken = x[x[id_col].isin(z[z.duplicated()])]
    return(broken)

def split_eq(dfs):
    df = dfs['id'].str.split('-', expand=True).reindex(columns=pd.np.arange(7))
    xs = pd.concat([dfs, df], axis=1).replace({'0': pd.np.NaN})
    return(xs)

def determine_base_pattern(i):
    global pbase
    id = ''
    if i['affected_entity_1_super'] == '' or pd.isnull(i['affected_entity_1_super']):
        print("No affected entity 1 is a case not accounted for")
        print(str(i))
        id = ''
    else:
        # Should be all.
        if not (i['affected_entity_1_rel'] == '' or pd.isnull(i['affected_entity_1_rel'])):
            if i['affected_entity_1_rel'] == 'BFO:0000050':
                if not (i['affected_entity_2_super'] == '' or pd.isnull(i['affected_entity_2_super'])):
                    if not (i['affected_entity_2_rel'] == '' or pd.isnull(i['affected_entity_2_rel'])):
                        if i['affected_entity_2_rel'] == 'BFO:0000050':
                            id = pbase + "abnormalQualityPartOfThingTowardsPartOfThing.yaml"
                        elif i['affected_entity_2_rel'] == 'BFO:0000066':
                            id = pbase + "abnormalQualityPartOfThingTowardsOccursInThing.yaml"
                    else:
                        id = pbase + "abnormalQualityPartOfThingTowardsThing.yaml"
                else:
                    id = pbase + "abnormalQualityPartOfThing.yaml"
            elif i['affected_entity_1_rel'] == 'BFO:0000066':
                if not (i['affected_entity_2_super'] == '' or pd.isnull(i['affected_entity_2_super'])):
                    if not (i['affected_entity_2_rel'] == '' or pd.isnull(i['affected_entity_2_rel'])):
                        if i['affected_entity_2_rel'] == 'BFO:0000050':
                            id = pbase + "abnormalQualityOccursInThingTowardsPartOfThing.yaml"
                        elif i['affected_entity_2_rel'] == 'BFO:0000066':
                            id = pbase + "abnormalQualityOccursInThingTowardsOccursInThing.yaml"
                    else:
                        id = pbase + "abnormalQualityOccursInThingTowardsThing.yaml"
                else:
                    id = pbase + "abnormalQualityOccursInThing.yaml"
        else:
            if not (i['affected_entity_2_super'] == '' or pd.isnull(i['affected_entity_2_super'])):
                if not (i['affected_entity_2_rel'] == '' or pd.isnull(i['affected_entity_2_rel'])):
                    if i['affected_entity_2_rel'] == 'BFO:0000050':
                        id = pbase + "abnormalQualityOfThingTowardsPartOfThing.yaml"
                    elif i['affected_entity_2_rel'] == 'BFO:0000066':
                        id = pbase + "abnormalQualityOfThingTowardsOccursInThing.yaml"
                else:
                    id = pbase + "abnormalQualityOfThingTowardsThing.yaml"
            else:
                id = pbase + "abnormalQualityOfThing.yaml"
    return id

# Load ID MAP
id_map = pd.read_csv(current_id_map, sep='\t')
id_map = split_eq(id_map)
id_map.columns = ['iri','id','affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']

# Load Depreacted ID MAP
df_deprecated_id_map = pd.read_csv(deprecated_id_map, sep='\t')
obsolete_classes = list(set(df_deprecated_id_map['Ontology ID']))

id_map = id_map[~id_map['iri'].isin(obsolete_classes)]

#df_deprecated_id_map['obsolete'] = 'obsolete'

# Load ZP labels (and replace IRIs by curies)
#df_zp_labels = pd.read_csv(zp_labels)
#df_zp_labels.drop_duplicates(subset=['term'],inplace=True)
#df_zp_labels = df_zp_labels.replace("http://purl.obolibrary.org/obo/", "")
#df_zp_labels = df_zp_labels.replace("_", ":") 

# Merge labels into depreacted ID map so we can generate some pretty labels
#df_deprecated_id_map = pd.merge(df_deprecated_id_map, df_zp_labels, left_on=['iri'], right_on=['term'], how='left')
#print(str(df_deprecated_id_map.head()))
#df_deprecated_id_map.to_csv(deprecated_id_map+"_dep.tsv", sep = '\t', index=False)
#colsp = ['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super','pattern']

# determine pattern for each EQ definition
cols = ['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']
id_map['pattern'] = id_map[cols].apply(determine_base_pattern,axis=1)
#id_map['label_pattern'] = id_map['pattern'].replace(".yaml", "_label.yaml", regex=True)
#id_map['eq_pattern'] = id_map[colsp].apply(determine_eq_pattern,axis=1)

# Exporting the files again
id_map.sort_values(by ='iri',inplace=True)
id_map=id_map.reindex(sorted(df.columns), axis=1)

id_map.to_csv(pattern_assignments, sep = '\t', index=False)

# Export DOSDP TSV Files
cols = ['iri','affected_entity_1_sub','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_super']
for p in set(id_map['pattern']):
    pattern=p.replace(pbase,'').replace('.yaml','.tsv')
    print(p)
    dx = id_map[id_map['pattern']==p]
    dx = dx[cols]
    dx.columns = ['defined_class','affected_entity_1_sub','affected_entity_1_super','pato_id','affected_entity_2_sub','affected_entity_2_super']
    dx = dx.dropna(axis=1, how='all')
    dx.sort_values(by ='defined_class',inplace=True)
    dx.to_csv(os.path.join(pattern_data, pattern), sep='\t', index=False)
    dx.to_csv(os.path.join(pattern_data, pattern.replace(".tsv", "_label.tsv")), sep='\t', index=False)

print("DOSDP export of ZP base patterns complete!")
