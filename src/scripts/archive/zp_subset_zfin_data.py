import pandas as pd
import os
import copy
import sys

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# This script takes in a set of Curies or IRIs and a column name and outputs subsets of the ZFIN data tables

fids = os.path.abspath(sys.argv[1])
data = os.path.abspath(sys.argv[2])
column_id = sys.argv[3]

outdata = os.path.join(os.path.dirname(data),os.path.basename(fids)+"_"+os.path.basename(data))

# LOAD ZFIN ANNOTATION DATA, ID MAP, and TARGET IDS
df = pd.read_csv(data, sep='\t', dtype=str)
df = df.fillna("")

with open(fids) as f:
    ids = f.readlines()

ids = [x.strip() for x in ids]
ids_cur = [w.replace("http://purl.obolibrary.org/obo/", "") for w in ids]
ids_cur = [w.replace("_", ":") for w in ids_cur]
ids_iri = ["http://purl.obolibrary.org/obo/"+w.replace(":", "_") for w in ids_cur]
include = ids_cur + ids_iri


if column_id=="all":
    cols = df.columns.values.tolist()
    out = df[df.isin(include).any(axis=1)]
else:
    out = df.loc[df[column_id].isin(include)]

print(len(df))
print(len(out))
out.to_csv(outdata, sep = '\t', index=False)