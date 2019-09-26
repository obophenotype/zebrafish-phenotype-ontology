import sys
import os
import pandas as pd

deprecated_id_map_file = sys.argv[1]
obsolete_template_file = sys.argv[2]
labels_file = sys.argv[3]

#deprecated_id_map_file = "/ws/zebrafish-phenotype-ontology/src/curation/deprecated_id_map.tsv"
#obsolete_template_file = "/ws/zebrafish-phenotype-ontology/src/templates/obsolete.tsv"
#labels_file = "/ws/zebrafish-phenotype-ontology/src/ontology/zp_labels.csv"

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

df_obsolete = pd.merge(df_obsolete, df_deprecated_id_map,  how='outer', left_on=columns, right_on = columns)

print(df_deprecated_id_map.head())
print(df_obsolete.head())

df_obsolete.to_csv(obsolete_template_file, sep = '\t', index=False)