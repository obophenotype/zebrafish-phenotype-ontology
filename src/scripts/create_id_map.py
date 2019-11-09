import sys
import os
import pandas as pd

pattern_dir= sys.argv[1]
idmap_out = sys.argv[2]

obo_prefix = "http://purl.obolibrary.org/obo/"

def get_id_columns_sorted(pattern_file):
    with open(pattern_file, 'r') as stream:
        try:
            pattern_json = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    idcolumns = list(pattern_json['vars'].keys()).sort()
    return idcolumns

def zfin_to_pattern_based_id(i):
    global pbase
    id = i
    if "abnormalAnatomicalEntity" in i['pattern']:
        "ZFA:0001135-PATO:0001236-GO:0042384-abnormalQualityPartOfThing.tsv"
        anatomical_entity=i.split("-")[0]
        
    return id

id_map['pattern_based_id'] = id_map['id'].apply(zfin_to_pattern_based_id,axis=1)

#print(columns)
#print(df1)
#print(df2)

pattern_data_dir = os.path.join(pattern_dir,"data")
pattern_yaml_dir = os.path.join(pattern_dir,"dosdp-patterns")

zfin_patterns = os.path.join(pattern_dir,"zfin")
anatomy_patterns = os.path.join(pattern_dir,"anatomy")
manual_patterns = os.path.join(pattern_dir,"manual")

pattern_data_dirs = [zfin_patterns,anatomy_patterns,manual_patterns]

joined = []

for dir in pattern_data_dirs:
    for filename in os.listdir(dir):
        if filename.endswith(".tsv"): 
            tsv = os.path.join(directory, filename)
            yaml = os.path.join(pattern_yaml_dir, filename.replace(".tsv",".yaml"))
            yids = get_id_columns_sorted(yaml)
            yids_incl_def = yids.append("defined_class")
            yids_incl_pattern = yids.append("pattern")
            df = pd.read_csv(tsv, usecols=yids_incl_def, sep='\t')
            
            for col in yids_incl:
                df_copy[col] = [str(i).replace(obo_prefix,"") for i in df_copy[col]]
                df_copy[col] = [str(i).replace("_", ":") for i in df_copy[col]]
            
            df['pattern'] = filename.replace(".tsv","") 
            df['id'] = df[yids_incl_pattern].apply('-'.join, axis=1) #generate a unique id string
            df = df.rename(columns={'defined_class': 'iri'})
            joined.append(df['iri','id'])
            continue
        else:
            continue

df_id_map = pd.concat(joined, axis=0, ignore_index=True)

#print(df_out)
df_id_map['iri','id'].to_csv(idmap_out, sep = '\t', index=False)
