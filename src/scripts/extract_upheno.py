import sys
import pandas as pd
import os

tsv = sys.argv[1]
id_map = sys.argv[2]
reserved_ids = sys.argv[3]
accession = int(sys.argv[4])
prefix = sys.argv[5]

tsv = "/ws/zebrafish-phenotype-ontology/src/patterns/data/auto/abnormalQualityOfThing.tsv"
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
    if fn=='abnormalQualityOfThing.tsv':
        if pato=='PATO:0000001':
            id = 'abnormal.tsv'
    return id

df['pattern'] = df.apply(determine_eq_pattern,axis=1)

for p in set(df['pattern']):
    print(p)
    pattern=p.replace(pbase,'').replace(ubase,'').replace('.yaml','.tsv')
    dx = df[df['pattern']==p]
    dx = dx.loc[:, dx.columns != 'pattern']
    dx.to_csv(os.path.join(dir,pattern), sep='\t', index=False)


