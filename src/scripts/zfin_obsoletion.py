import sys
import os
import pandas as pd

deprecated_id_map_file = sys.argv[1]
obsolete_template_file = sys.argv[2]
obsolete_template_candiate_file = sys.argv[3]
labels_file = sys.argv[4]

df_deprecated_id_map = pd.read_csv(deprecated_id_map_file, sep='\t')
df_obsolete = pd.read_csv(obsolete_template_file, sep='\t')
df_labels = pd.read_csv(labels_file, sep=',')

# Preparing obsoletion pattern
df_labels.columns = ['iri','label']

df_deprecated_id_map['iri'] = [str(i).replace(":", "_") for i in df_deprecated_id_map['iri']]
df_deprecated_id_map['iri'] = 'http://purl.obolibrary.org/obo/' + df_deprecated_id_map['iri'].astype(str)
df_deprecated_id_map = pd.merge(df_deprecated_id_map, df_labels,  how='left', left_on="iri", right_on = "iri")

columns = ['Ontology ID','ZFIN Annotation','Obsolete','Label']
df_deprecated_id_map.columns = columns
df_deprecated_id_map['Obsolete'] = 'true'
df_deprecated_id_map['Label'] = 'obsolete ' + df_deprecated_id_map['Label'].astype(str)

obsolete_classes=list(set(df_obsolete['Ontology ID']))
df_obsolete_candidates = df_deprecated_id_map[~df_deprecated_id_map['Ontology ID'].isin(obsolete_classes)]
df_obsolete_candidates.sort_values(by ='Ontology ID',inplace=True)
df_obsolete_candidates.to_csv(obsolete_template_candiate_file, sep = '\t', index=False)