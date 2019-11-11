import sys
import os
import yaml
import pandas as pd

idmf="/Users/matentzn/ws/zebrafish-phenotype-ontology/src/curation/zp_zfin_phenotype_fish.tsv"
redf="/Users/matentzn/ws/zebrafish-phenotype-ontology/src/curation/zp_zfin_phenotype_fish_go_quality.tsv"
remf="/Users/matentzn/ws/zebrafish-phenotype-ontology/src/curation/fix_equivalents.txt"
fe = pd.read_csv(remf, sep='\t')
idm = pd.read_csv(idmf, sep='\t')

#rel=list(fe['rel'].values)
#print(rel)
#anatomy=list(fe['anatomy'].values)
#partof=list(fe['partof'].values)

#idm = idm[idm['Post-composed Relationship ID'].isin([''])]
print(len(idm))
idm = idm.loc[idm['Affected Structure or Process 1 subterm ID'].str.startswith('GO:', na=False)]
print(len(idm))
idm = idm.loc[idm['Phenotype Keyword ID']=='PATO:0000001']
print(len(idm))
#print(len(idm))
#idm = idm[idm['Affected Structure or Process 1 superterm ID'].isin(partof)]
#print(len(idm))
idm.to_csv(redf, sep='\t', index=False)