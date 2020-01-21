import pandas as pd
import copy
import sys
import os


class zp_pipeline_config:
    def __init__(self,accession,reserved_ids_file=None, include_modifier=True):
        self.zfin_fish_data = "https://zfin.org/downloads/phenotype_fish.txt"
        self.zfin_gene_data = 'https://zfin.org/downloads/phenoGeneCleanData_fish.txt'
        self.zp_prefix = "ZP:"
        self.minid = accession
        self.maxid = 9999999 # THE maximum integer the current OBO IRI space allows (ZP_9999999).
        self.phenotype_fish_functional_columns=pd.np.array([7,9,11,13,15,16,18,20])-1
        self.phenotype_gene_functional_columns=pd.np.array([4,6,8,10,12,13,15,17])-1
        self.functional_column_names=['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','modifier','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']
        if reserved_ids_file is None:
            self.reserved_ids = []
        else:
            self.reserved_ids = self.zp_ids_from_txt_file(reserved_ids_file)
        self.currentid = self.get_highest_id(self.reserved_ids)
        self.include_modifier = include_modifier

    def get_highest_id(self,ids):
        if ids:
            x = [i.replace(self.zp_prefix, "").lstrip("0") for i in ids]
            x = [s for s in x if s!='']
            if len(x)==0:
                x=[0,]
            x = [int(i) for i in x]
            return max(x)
        else:
            return 0
    
    def zp_ids_from_txt_file(self,filename):
        with open(filename) as f:
            ids = f.readlines()
        ids = [x.strip() for x in ids]
        ids = [s for s in ids if s.startswith("ZP:")]
        return ids

    def set_currentid(self,currentid):
        self.currentid = currentid
    
    def correct_id(self,id):
        #0-0-GO:0001501-PATO:0000001-0-0-0
        #if id.startswith("0-0-GO:") and id.endswith("-PATO:0000001-0-0-0"):
        #    id = id.replace("PATO:0000001","PATO:0001236")
        return id
        
    def load_zfin_data(self,data_url, functional_column_indexes):
        df = pd.read_csv(data_url, sep='\t', header=None)
        d = df[functional_column_indexes].drop_duplicates()
        d.columns = ['affected_entity_1_sub','affected_entity_1_rel','affected_entity_1_super','pato_id','modifier','affected_entity_2_sub','affected_entity_2_rel','affected_entity_2_super']

        # For the ID generation process, we decided to replace empty or NAN values with 0
        d = d.replace(pd.np.nan, "0", regex=True)
        d = d.replace("nan", "0", regex=True)
        d = d.replace("http://purl.obolibrary.org/obo/", "")
        d = d.replace("_", ":")
        d['modifier'] = d['modifier'].replace("^normal$", "PATO:0000461")
        d['modifier'] = d['modifier'].replace("^abnormal$", "PATO:0000460")
        # Movie modifier column to the beginning
        mod = d['modifier']
        d.drop(labels=['modifier'], axis=1,inplace = True)
        if self.include_modifier:
            d.insert(0, 'modifier', mod)
        d['id_raw'] = d.apply('-'.join, axis=1) #generate a unique id string
        d['id'] = d['id_raw'].apply(lambda x: self.correct_id(x))
        return d
        
    def load_zfin_phenotype_fish(self):
        return self.load_zfin_data(self.zfin_fish_data,self.phenotype_fish_functional_columns)
        
    def load_zfin_phenotype_gene(self):
        return self.load_zfin_data(self.zfin_gene_data,self.phenotype_gene_functional_columns)
    
    def generate_id(self,i):
        if isinstance(i,str):
            if i.startswith(self.zp_prefix):
                return i
        self.currentid = self.currentid + 1
        if self.currentid>self.maxid:
            raise ValueError('The ID space has been exhausted (maximum 10 million). Order a new one!')
        id = self.zp_prefix+str(self.currentid).zfill(7)
        return id
    
    def compute_missing_zp_ids(self,df):
        df['iri'] = [self.generate_id(i) for i in df['iri']]
        return(df)

    def get_rows_with_duplicates(self,x,id_col):
        z = x[id_col]
        broken = x[x[id_col].isin(z[z.duplicated()])]
        return(broken)
    
    def dump_reserved_ids(self,df,reserved_ids_file):
        ids=list(set(self.reserved_ids+df['iri'].tolist()))
        with open(reserved_ids_file, 'w') as f:
            for item in ids:
                f.write("%s\n" % item)

# Get and clean complete set of currently assigned ZP ids (can be generated using the respective make goal in src/curation/Makefile

