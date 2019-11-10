import sys
import os
import yaml
import pandas as pd

pattern_dir= sys.argv[1]
idmap_out = sys.argv[2]

obo_prefix = "http://purl.obolibrary.org/obo/"

def get_rows_with_duplicates(x,id_col):
    z = x[id_col]
    broken = x[x[id_col].isin(z[z.duplicated()])]
    return(broken)

def get_id_columns_sorted(pattern_file):
    print(pattern_file)
    with open(pattern_file, 'r') as stream:
        try:
            pattern_json = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    idcolumns = list(pattern_json['vars'].keys())
    idcolumns.sort()
    #print("Cols: {}".format(idcolumns))
    return idcolumns

pattern_data_dir = os.path.join(pattern_dir,"data")
pattern_yaml_dir = os.path.join(pattern_dir,"dosdp-patterns")

zfin_patterns = os.path.join(pattern_data_dir,"zfin")
anatomy_patterns = os.path.join(pattern_data_dir,"anatomy")
manual_patterns = os.path.join(pattern_data_dir,"manual")

pattern_data_dirs = [zfin_patterns,anatomy_patterns,manual_patterns]

joined = []

for dir in pattern_data_dirs:
    for filename in os.listdir(dir):
        if filename.endswith(".tsv") and not filename.endswith("_label.tsv"): 
            tsv = os.path.join(dir, filename)
            yamlf = os.path.join(pattern_yaml_dir, filename.replace(".tsv",".yaml"))
            yids = get_id_columns_sorted(yamlf)
            yids_incl_def = yids.copy()
            yids_incl_def.append("defined_class")
            yids_incl_pattern = yids.copy()
            yids_incl_pattern.append("pattern")
            df = pd.read_csv(tsv, sep='\t')            
            for col in yids_incl_def:
                df[col] = [str(i).replace(obo_prefix,"") for i in df[col]]
                df[col] = [str(i).replace("_", ":") for i in df[col]]
            #df.to_csv(tsv, sep = '\t', index=False)
            
            df['pattern'] = filename.replace(".tsv","")
            df['pattern_file'] = tsv
            df['pipeline'] = os.path.basename(dir)
            df['id'] = df[yids_incl_pattern].apply('-'.join, axis=1) #generate a unique id string
            df = df.rename(columns={'defined_class': 'iri'})
            #print(df.head())
            joined.append(df[['iri','id','pipeline','pattern_file']])
            continue
        else:
            continue

df_id_map = pd.concat(joined, axis=0, ignore_index=True)
df_id_map.sort_values(by ='iri',inplace=True)

#print(df_out)

df_id_map_dup_id = get_rows_with_duplicates(df_id_map,'id')
df_id_map_dup_id.sort_values(by ='id',inplace=True)
print(df_id_map_dup_id.head())
print(len(df_id_map_dup_id))

df_id_map_dup_iri = get_rows_with_duplicates(df_id_map,'iri')
print(df_id_map_dup_iri.head())
print(len(df_id_map_dup_iri))

#for id in df_id_map_dup_id['id'].unique():
#    x = df_id_map_dup_id[df_id_map_dup_id['id']==id]
#    x_man = x[x['pipeline']=="anatomy"]
#    if not x_man.empty:
#        tsv = x_man['pattern_file'].values[0]
#        zp_iri = x_man['iri'].values[0]
#        print(tsv)
#        print(zp_iri)
#        df = pd.read_csv(tsv, sep='\t')
#        df = df[df['defined_class']!=zp_iri]
#        df.to_csv(tsv, sep = '\t', index=False)
#        #sys.exit(0)

df_id_map[['iri','id']].drop_duplicates().to_csv(idmap_out, sep = '\t', index=False)
