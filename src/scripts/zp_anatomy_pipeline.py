import sys
import pandas as pd
import numpy as np
import yaml
import os
import collections
from subprocess import check_call

zfa = os.path.join(sys.argv[1])
id_map = os.path.join(sys.argv[2])
reserved_ids = os.path.join(sys.argv[3])
pattern_dir = os.path.join(sys.argv[4])
sparql_dir = os.path.join(sys.argv[5])
out_dir = os.path.join(sys.argv[6])
configf = os.path.join(sys.argv[7])

class zpconfig:
    def __init__(self, config_file):
        self.config = yaml.safe_load(open(config_file, 'r'))

    def get_iri_accession(self):
        return int(self.config.get("anatomy_config").get("iri_accession"))
    
    def get_iri_prefix(self):
        return self.config.get("anatomy_config").get("iri_prefix")
    
    def get_global_blacklist(self):
        return self.config.get("anatomy_config").get("global").get("blacklist")
    
    def get_global_blacklist_branch(self):
        return self.config.get("anatomy_config").get("global").get("blacklist_branch")
    
    def get_patterns(self):
        return [t['pattern'] for t in self.config.get("anatomy_config").get("patterns")]
    
    def get_blacklist(self, pattern):
        return [t['blacklist'] for t in self.config.get("anatomy_config").get("patterns") if t['pattern'] == pattern][0]
    
    def get_blacklist_branch(self, pattern):
        return [t['blacklist_branch'] for t in self.config.get("anatomy_config").get("patterns") if t['pattern'] == pattern][0]

def cdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def rm(path):
    if os.path.isfile(path):
        os.remove(path)
        
def robot_query(ontology_path,seedfile,sparql_terms, TIMEOUT="3600", robot_opts="-v"):
    print("Query "+ontology_path+" with "+sparql_terms)
    try:
        check_call(['timeout',TIMEOUT,'robot', 'query',robot_opts,'--use-graphs','true','-f','csv','-i', ontology_path,'--query', sparql_terms, seedfile])
    except Exception as e:
        print(e)
        raise Exception("Seed extraction of" + ontology_path + " failed")
        
def file_to_list(file_path):
    with open(file_path) as f:
        return f.read().splitlines()

#upheno_config_file = os.path.join("/ws/upheno-dev/src/curation/upheno-config.yaml")
print("Configfile:"+configf)
config = zpconfig(configf)
accession = config.get_iri_accession()
prefix = config.get_iri_prefix()
obo_prefix = "http://purl.obolibrary.org/obo/"
maxid = 9999999

# Set up temp directory
tmpdir=os.path.join("tmp")
rm(tmpdir)
cdir(tmpdir)

zfa_terms_file = os.path.join(tmpdir,"zfa_terms.txt")
zfa_terms_sparql = os.path.join(sparql_dir,"zfa_terms.sparql")


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

def add_id_column(df,idcolumns,pattern):
    global df_ids
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

    df = df.replace(np.nan, '', regex=True)
    #df.loc[(df['defined_class'] != '') & (df['iritemp001'] == ''), 'iritemp001'] = df['']
    broken = np.where((df['defined_class'] != '') & (df['iritemp001'] != '' )& (df['iritemp001'] != df['defined_class']), df[['defined_class','iritemp001']].apply('-'.join, axis=1),"OK")
    if len(broken)>0:
        print("WARNING: Broken records")
        print(broken)

    df['iritemp001'] = np.where(df['defined_class'] != '', df['defined_class'], df['iritemp001'])

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

# Get Anatomy seed
robot_query(zfa,zfa_terms_file,zfa_terms_sparql)
zfa_terms = file_to_list(zfa_terms_file)
if 'term' in zfa_terms: zfa_terms.remove('term')
zfa_terms = [str(i).replace(obo_prefix,"") for i in zfa_terms]
zfa_terms = [str(i).replace("_", ":") for i in zfa_terms]


## COMPUTE GLOBAL BLACKLIST. THIS HAS TWO COMPONENTS: (1) Loading the IRIS from the the 
## Respective section in the config and querying the blacklisted branches
## Using a dynamic SPARQL approach

zfa_global_blacklist = []
if config.get_global_blacklist() is not None:
    zfa_global_blacklist = zfa_global_blacklist + config.get_global_blacklist()

global_sparql = os.path.join(tmpdir,"global_blacklist.sparql")
global_blacklist_file = os.path.join(tmpdir,"global_blacklist.txt")
superclasses = ""
for branch in config.get_global_blacklist_branch():
    superclasses = superclasses +" <"+branch+">"
query= """prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
SELECT DISTINCT ?term WHERE {
    VALUES ?o { %s } 
    ?term rdfs:subClassOf* ?o .
} """ % superclasses
with open(global_sparql, "w") as f:
    f.write(query)
robot_query(zfa,global_blacklist_file,global_sparql)
zfa_global_blacklist = zfa_global_blacklist + file_to_list(global_blacklist_file)
zfa_global_blacklist = [str(i).replace(obo_prefix,"") for i in zfa_global_blacklist]
zfa_global_blacklist = [str(i).replace("_", ":") for i in zfa_global_blacklist]

# Load data
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

for pattern in config.get_patterns():
    print(pattern)
    pattern_yaml = os.path.join(pattern_dir,pattern+".yaml")
    pattern_tsv = os.path.join(out_dir,pattern+".tsv")
    pattern_sparql = os.path.join(tmpdir,pattern+".sparql")
    blacklist_file = os.path.join(tmpdir,pattern+"_blacklist.txt")
    superclasses = ""
    for branch in config.get_blacklist_branch(pattern):
        superclasses = superclasses +" <"+branch+">"
    query= """prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    SELECT DISTINCT ?term WHERE {
        VALUES ?o { %s } 
        ?term rdfs:subClassOf* ?o .
    } """ % superclasses
    print(query)
    with open(pattern_sparql, "w") as f:
        f.write(query)
    robot_query(zfa,blacklist_file,pattern_sparql)
    blacklist = file_to_list(blacklist_file) + zfa_global_blacklist
    if config.get_blacklist(pattern) is not None:
        blacklist = blacklist + config.get_blacklist(pattern)
    if 'term' in blacklist: blacklist.remove('term')
    whitelist = [b for b in zfa_terms if b not in blacklist]
    df = pd.DataFrame(whitelist)
    df.columns = ['anatomical_entity']
    
    # create ids in df
    idcolumns = get_id_columns(pattern_yaml) # Parses the var fillers from the pattern
    df = add_id_column(df, idcolumns,pattern+".tsv")

    ids=list(set(ids+df_ids['iritemp001'].tolist()))
    
    defclass = df['defined_class']
    df.drop(labels=['defined_class'], axis=1,inplace = True)
    df.insert(0, 'defined_class', defclass)
    df = df.drop_duplicates()
    df = df.sort_values('defined_class')
    df.to_csv(pattern_tsv, sep = '\t', index=False)

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

