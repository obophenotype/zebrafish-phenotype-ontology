import sys
import pandas as pd
import yaml
import os
import collections

tsv = sys.argv[1]
id_map = sys.argv[2]
reserved_ids = sys.argv[3]
accession = int(sys.argv[4])
prefix = sys.argv[5]
pattern_dir = sys.argv[6]

obo_prefix = "http://purl.obolibrary.org/obo/"
maxid = 9999999
pattern = os.path.basename(tsv)
pattern_file = os.path.join(pattern_dir,pattern.replace(".tsv",".yaml"))

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

# For the following function to work properly it is important to note that there should be absolutely no columns in teh tsv file other than the defi
# defined_class and columns whos names end with _label other than the ones that contribute to the identity of the entity in question

def add_id_column(df,idcolumns):
    global df_ids, pattern
    #df = pd.read_csv(tsv, sep='\t')
    if 'defined_class' not in df.columns:
        df['defined_class'] = ''

    if 'iritemp001' in df.columns:
        df = df.drop(['iritemp001'], axis=1)
        print("Warning: There was a colum labelled iritemp001, which is reserved vocabulary and will be overwritten")

    df['pattern'] = pattern.replace(".tsv","").replace(".yaml","")

    df_copy = df.copy()

    idcolumns_incl_patterns = idcolumns.copy()
    idcolumns_incl_patterns.append('pattern')

    for col in idcolumns:
        df_copy[col] = [str(i).replace(obo_prefix,"") for i in df_copy[col]]
        df_copy[col] = [str(i).replace("_", ":") for i in df_copy[col]]

    df['id'] = df_copy[idcolumns_incl_patterns].apply('-'.join, axis=1)

    if df_ids.empty:
        df['iritemp001'] = ""
    else:
        df = pd.merge(df, df_ids, on='id', how='left')

    df = df.replace(pd.np.nan, '', regex=True)
    #df.loc[(df['defined_class'] != '') & (df['iritemp001'] == ''), 'iritemp001'] = df['']
    broken = pd.np.where((df['defined_class'] != '') & (df['iritemp001'] != '' )& (df['iritemp001'] != df['defined_class']), df[['defined_class','iritemp001']].apply('-'.join, axis=1),"OK")
    if len(broken)>0:
        print("WARNING: Broken records")
        print(broken)

    df['iritemp001'] = pd.np.where(df['defined_class'] != '', df['defined_class'], df['iritemp001'])

    df['defined_class'] = [generate_id(i) for i in df['iritemp001']]
    x = df[['defined_class','id']]
    x.columns = ['iritemp001','id']
    df_ids = pd.concat([df_ids,x],sort=True)
    df_ids = df_ids.drop_duplicates()
    df = df.drop(['pattern', 'id','iritemp001'], axis=1)
    #print(df.head(4))
    return df

def get_id_columns(pattern_file):
    with open(pattern_file, 'r') as stream:
        try:
            pattern_json = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    idcolumns = list(pattern_json['vars'].keys())
    idcolumns.sort()
    return idcolumns

# Load data
df = pd.read_csv(tsv, sep='\t')
df_ids = pd.read_csv(id_map, sep='\t')
#we change the iri column name here temporarily to make merging and amending easier. Is changed back to normal at the end of the function
df_ids = df_ids.rename(columns={'iri': 'iritemp001'})

with open(reserved_ids) as f:
    ids = f.readlines()

ids = [x.strip() for x in ids]
ids = [s for s in ids if s.startswith(prefix)]


# compute next assignable id
startid = get_highest_id(ids)
if startid<accession:
    startid=accession

# create ids in df
idcolumns = get_id_columns(pattern_file) # Parses the var fillers from the pattern
df = add_id_column(df, idcolumns)

ids=list(set(ids+df_ids['iritemp001'].tolist()))
# wherever there is NULL assign new id starting with start id, make sure that value is then appended to df_ids and ids
defclass = df['defined_class']
df.drop(labels=['defined_class'], axis=1,inplace = True)
df.insert(0, 'defined_class', defclass)
df = df.sort_values('defined_class')
df.drop_duplicates().to_csv(tsv, sep = '\t', index=False)

df_ids = df_ids.rename(columns={'iritemp001': 'iri'})
df_ids.sort_values(by ='iri',inplace=True)
df_ids=df_ids[['iri','id']].drop_duplicates()
#df_ids=df_ids.reindex(['iri','id'], axis=1)
iristest = df_ids['iri']
idstest = df_ids['id']

if len(iristest) != len(set(iristest)):
    duplicates = [item for item, count in collections.Counter(iristest).items() if count > 1]
    raise ValueError('An iri was assigned more than once, aborting.. ('+str(duplicates)+')'+str(df_ids[df_ids['iri'].isin(duplicates)].head()))

if len(idstest) != len(set(idstest)):
    duplicates = [item for item, count in collections.Counter(idstest).items() if count > 1]
    raise ValueError('An id was assigned more than once, aborting.. ('+str(duplicates)+')'+str(df_ids[df_ids['id'].isin(duplicates)].head()))

    
df_ids.to_csv(id_map, sep = '\t', index=False)

with open(reserved_ids, 'w') as f:
    for item in ids:
        f.write("%s\n" % item)