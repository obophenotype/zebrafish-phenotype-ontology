import sys
import pandas as pd
import os

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

tsv = sys.argv[1]
term_file = sys.argv[2]
column_name = sys.argv[3]
reserved_ids = sys.argv[4]
zfin_map = sys.argv[5]
accession = int(sys.argv[6])
prefix = sys.argv[7]

tsv = "/ws/zebrafish-phenotype-ontology/src/patterns/data/anatomy/abnormalAnatomicalEntity.tsv"
term_file = "/ws/zebrafish-phenotype-ontology/src/curation/tmp/zfa_seed.txt"
column_name = "anatomical_entity"
zfin_map = "/ws/zebrafish-phenotype-ontology/src/curation/id_map_zfin.tsv"
prefix = "http://purl.obolibrary.org/obo/ZP_"

maxid = 9999999
pattern = os.path.basename(tsv)

# 1. Load TSV file, if not there, create it.
if os.path.isfile(tsv):
    df_tsv = pd.read_csv(tsv, sep='\t')
    if 'defined_class' not in df_tsv:
        df_tsv['defined_class'] = ""
else:
    df_tsv = pd.DataFrame(columns=['defined_class', column_name])

# 3. Load terms in the term file (the new seeds)
with open(term_file) as f:
    terms = f.readlines()

terms = [x.strip() for x in terms]
terms = [s for s in terms if s.startswith('http://purl.obolibrary.org/obo/')]

# 4. compute next assignable id
startid = get_highest_id(ids)
if startid<accession:
    startid=accession

# 5. Filter out new terms that have already been covered elsewhere


# 6. Generate new ZP ids
df_tsv['defined_class'].replace(r'^\s*$', "", regex=True)
df_tsv['defined_class'] = [generate_id(s) for s in df_tsv['defined_class']]

# 7. Export the TSV file
df_tsv.to_csv(tsv, sep = '\t', index=False)
