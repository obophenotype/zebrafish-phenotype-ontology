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

tsv = "/ws/xenopus-phenotype-ontology/src/patterns/data/anatomy/abnormalAnatomicalEntity.tsv"
term_file = "../curation/tmp/zfa_seed.txt"
column_name = "anatomical_entity"
reserved_ids = "/ws/xenopus-phenotype-ontology/src/patterns/reserved_iris.txt"
zfin_map = "/ws/xenopus-phenotype-ontology/src/curation/id_map_zfin.tsv"
accession = int("9898")
prefix = "http://purl.obolibrary.org/obo/XPO_"

raise Exception("interrupted")

maxid = 9999999
pattern = os.path.basename(tsv)

def get_highest_id(ids):
    global prefix
    x = [i.replace(prefix, "").lstrip("0") for i in ids]
    x = [s for s in x if s!='']
    if len(x)==0:
        x=[0,]
    x = [int(i) for i in x]
    return max(x)


def generate_id(i):
    global startid, maxid
    if(isinstance(i,str)):
        if(i.startswith(prefix)):
            return i
    startid = startid + 1
    if startid>maxid:
        raise ValueError('The ID space has been exhausted (maximum 10 million). Order a new one!')
    id = prefix+str(startid).zfill(7)
    return id

# Load data
df = pd.read_csv(tsv, sep='\t')

with open(reserved_ids) as f:
    ids = f.readlines()

ids = [x.strip() for x in ids]
ids = [s for s in ids if s.startswith(prefix)]

with open(anatomy_terms) as f:
    anatomy = f.readlines()

anatomy = [x.strip() for x in anatomy]
anatomy = [s for s in anatomy if s.startswith('http://purl.obolibrary.org/obo/')]

for a in anatomy:
    if a in df['anatomical_entity']:
        pass

# compute next assignable id
startid = get_highest_id(ids)
if startid<accession:
    startid=accession

if 'defined_class' not in df:
    df['defined_class'] = ""

df['defined_class'].replace(r'^\s*$', "", regex=True)
df['defined_class'] = [generate_id(s) for s in df['defined_class']]

df.to_csv(tsv, sep = '\t', index=False)
with open(reserved_ids, 'w') as f:
    for item in df['defined_class']:
        f.write("%s\n" % item)