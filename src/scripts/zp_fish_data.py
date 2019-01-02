import pandas as pd
import copy
import sys

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# This script takes in the ZFIN EQ to GENE mappings and generates a little RDF knowledge graph from them referencing
# the precomposed ZP classes. This file can be used to affectively query and group annotations related to phenotype,
# for example: Find all annotations pertaining to morphological abnormalities of any anatomical part.

id_map = sys.argv[1] # The current ZP-ZFIN EQ id map
zp_zfin_mappings = sys.argv[2] # The desired location for the resulting gene annotation to ZP mappings

#id_map = '/ws/zebrafish-phenotype-ontology/src/curation/id_map.tsv'
#gene_annotation_mappings = "/ws/zebrafish-phenotype-ontology/src/curation/zp_annotations_to_iri.tsv"
#annotation_ttl = "/ws/zebrafish-phenotype-ontology/src/curation/kb_zp.ttl"

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
functionalcolumns = pd.np.array([7,9,11,13,16,18,20])-1
df_zfin.update(df_zfin[functionalcolumns].fillna('0'))
print(len(df_zfin))
df_zfin['id'] = df_zfin[functionalcolumns].astype(str).apply('-'.join, axis=1)
df_zfin = pd.merge(df_zfin, id_map, on='id', how='left')
print(len(df_zfin))
df_zfin[functionalcolumns] = df_zfin[functionalcolumns].replace('^0$', '', regex=True)
print(len(df_zfin))
df_zfin.to_csv(zp_zfin_mappings, sep = '\t', index=False)

print("Exporting ZP-ZFIN-EQ annotations complete!")
