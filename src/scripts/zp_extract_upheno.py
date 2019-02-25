import pandas as pd
import os
import sys

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# This script takes a single TSV file in tries to determine which upheno pattern would be a good fit.
# The TSV file is then split into the default and any upheno pattern that could be matched to it

# It is expected that this file will be developed and extended for a while to come

#tsv = "/ws/zebrafish-phenotype-ontology/src/patterns/data/auto/abnormalQualityOfThing.tsv"
tsv = sys.argv[1]

pbase="https://raw.githubusercontent.com/obophenotype/zebrafish-phenotype-ontology/master/src/patterns/dosdp-patterns/"
ubase="https://raw.githubusercontent.com/obophenotype/upheno/master/src/patterns/"

df = pd.read_csv(tsv, sep='\t')
fn = os.path.basename(tsv)
dir = os.path.dirname(tsv)

# This function should be extended to include other patterns as well.
# It is not unlikely that eventually some basic reasoning needs to be done, probably outside this script,
# to determine whether a specific class is an instance of a pattern filler
def determine_eq_pattern(i):
    global fn,pbase,ubase
    id = fn
    pato=i['pato_id']
    entity=i['affected_entity_1_super']
    if fn=='abnormalQualityOfThing.tsv':
        if pato=='PATO:0000001':
            if entity.startswith('GO'):
                id = 'abnormalAnatomicalEntity.tsv'
            if entity.startswith('ZFA'):
                id = 'abnormalBiologicalProcess.tsv'
    return id

# Determining the correct pattern
df['pattern'] = df.apply(determine_eq_pattern,axis=1)

# Split TSV into relevant patterns and export
for p in set(df['pattern']):
    print(p)
    pattern=p.replace(pbase,'').replace(ubase,'').replace('.yaml','.tsv')
    dx = df[df['pattern']==p]
    if pattern=="abnormalAnatomicalEntity.tsv":
        dx = dx.rename(columns={'affected_entity_1_super': 'anatomical_entity', 'pato_id': 'quality'})
    if pattern=="abnormalBiologicalProcess.tsv":
        dx = dx.rename(columns={'affected_entity_1_super': 'biological_process', 'pato_id': 'quality'})
    dx = dx.loc[:, dx.columns != 'pattern']
    dx.to_csv(os.path.join(dir,pattern), sep='\t', index=False)


