import sys
import os
import yaml
import pandas as pd

idmf=os.path.join("~/ws/zebrafish-phenotype-ontology/src/patterns/data/anatomy","abnormalAnatomicalEntity.tsv")
remf=os.path.join("~/ws/zebrafish-phenotype-ontology/src/ontology","id_map_rem.txt")
rem = pd.read_csv(remf, header=None, sep='\t')
idm = pd.read_csv(idmf, sep='\t')
print(idm.head())
remids = list(rem.ix[:,0].values)
print(remids)
idm = idm[~idm['defined_class'].isin(remids)]
idm.to_csv(idmf, sep='\t', index=False)