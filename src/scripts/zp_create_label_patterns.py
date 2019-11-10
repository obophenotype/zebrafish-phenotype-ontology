import sys
import os
import yaml
import pandas as pd

pattern_dir= sys.argv[1]

obo_prefix = "http://purl.obolibrary.org/obo/"

class zpconfig:
    def __init__(self, config_file):
        self.config = yaml.load(open(config_file, 'r'))

    def get_iri_accession(self):
        return int(self.config.get("label_config").get("iri_accession"))
    
    def get_iri_prefix(self):
        return self.config.get("label_config").get("iri_prefix")
    
    def get_patterns(self):
        return [t['pattern'] for t in self.config.get("label_config").get("patterns")]
    
    def get_variable_mappings(self, pattern):
        return [t['column_matches'] for t in self.config.get("label_config").get("patterns") if t['pattern'] == pattern][0]
    
    def get_label_pattern(self, pattern):
        return [t['label_pattern'] for t in self.config.get("label_config").get("patterns") if t['pattern'] == pattern][0]
    

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
label_patterns = os.path.join(pattern_data_dir,"labels")

configf = os.path.join(pattern_dir,"pattern-label-config.yaml")

config = zpconfig(configf)


pattern_data_dirs = [zfin_patterns,anatomy_patterns,manual_patterns]

joined = []

for pattern_dir in pattern_data_dirs:
    print(pattern_dir)
    for filename in os.listdir(pattern_dir):
        if filename.endswith(".tsv") and not filename.endswith("_label.tsv"): 
            tsv = os.path.join(pattern_dir, filename)
            pattern = filename.replace(".tsv","")
            print(pattern)
            df_labels = pd.read_csv(tsv, sep='\t')            
            
            # Check if the pattern already has a corresponding label pattern.. If not
            # obtain from config
            yaml_label_f = os.path.join(pattern_yaml_dir, filename.replace(".tsv","_label.yaml"))
            if os.path.exists(yaml_label_f):
                label_pattern_name = filename.replace(".tsv","_label.tsv")
            else:
                label_pattern_name = config.get_label_pattern(pattern)+".tsv"
                for mapping in config.get_variable_mappings(pattern):
                    if '|' in mapping:
                        upheno_var = mapping.split('|')[0]
                        zp_var = mapping.split('|')[1]
                        if ':' in upheno_var:
                            df_labels[zp_var] = upheno_var
                        else:    
                            df_labels = df_labels.rename(columns={upheno_var: zp_var})
            
            # Save the freshly created label TSV
            label_pattern_tsv = os.path.join(label_patterns,label_pattern_name)
            if os.path.exists(label_pattern_tsv):
                df_label_pattern = pd.read_csv(label_pattern_tsv, sep='\t')
                df_label_pattern = pd.concat([df_label_pattern,df_labels],sort=True)
                df_label_pattern = df_label_pattern.drop_duplicates()
                df_labels = df_label_pattern    
            
            df_labels.to_csv(label_pattern_tsv, sep = '\t', index=False)
        else:
            continue