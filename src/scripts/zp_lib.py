import pandas as pd
import numpy as np
import copy
import sys
import os


# ---------------------------------------------------------------------------
# ZFIN EQ keys
#
# How ZP identifies a ZFIN post-composed phenotype (an "EQ").
#
# ZFIN's download files describe each phenotype by up to seven ontology
# terms: the affected structure or process (a subterm, a relation, and a
# superterm), the PATO quality, and an optional second structure or process
# (again subterm, relation, superterm). ZP's key for a phenotype is those
# seven ids joined with '-', with absent components written as '0':
#
#     0-0-ZFA:0000095-PATO:0000001-0-0-0
#
# The key is what id_map_zfin.tsv maps to ZP ids, so every script that reads
# ZFIN data must build it exactly this way. Each file also carries a
# normal/abnormal tag; it is deliberately not part of the key.
#
# Column positions are 1-based, as in ZFIN's documentation. The files have
# no header row.
# ---------------------------------------------------------------------------

# phenotype_fish.txt
PHENOTYPE_FISH_EQ_COLUMNS = (7, 9, 11, 13, 16, 18, 20)
PHENOTYPE_FISH_TAG_COLUMN = 15

# phenoGeneCleanData_fish.txt
PHENO_GENE_EQ_COLUMNS = (4, 6, 8, 10, 13, 15, 17)
PHENO_GENE_TAG_COLUMN = 12

EQ_COMPONENT_NAMES = [
    "affected_entity_1_sub",
    "affected_entity_1_rel",
    "affected_entity_1_super",
    "pato_id",
    "affected_entity_2_sub",
    "affected_entity_2_rel",
    "affected_entity_2_super",
]

ABSENT = "0"


def eq_key(components) -> str:
    """Join the seven EQ component ids into ZP's key, '0' for absent ones."""
    return "-".join(c.strip() or ABSENT for c in components)


def eq_components(row, columns):
    """Pick the EQ component ids out of a raw ZFIN row, by 1-based column."""
    return [row[c - 1] for c in columns]


class ZPPipelineConfig:
    def __init__(self,accession,zfin_fish_data_file,reserved_ids_file=None, include_modifier=True):
        # zfin_fish_data_file must be a local copy of ZFIN's
        # phenotype_fish.txt. This library does not hit the network.
        self.zfin_fish_data_file = zfin_fish_data_file

        self.zp_prefix = "ZP:"
        self.minid = accession
        self.maxid = 9999999 # THE maximum integer the current OBO IRI space allows (ZP_9999999).
        # 0-based column positions of the EQ components and the normal/abnormal
        # tag ("modifier") in phenotype_fish.txt; the key itself is eq_key above.
        self.phenotype_fish_eq_columns = [c - 1 for c in PHENOTYPE_FISH_EQ_COLUMNS]
        self.phenotype_fish_modifier_column = PHENOTYPE_FISH_TAG_COLUMN - 1
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
        
    def load_zfin_data(self, data_file, eq_columns, modifier_column):
        df = pd.read_csv(data_file, sep='\t', header=None, dtype=str, keep_default_na=False)
        d = df[eq_columns + [modifier_column]].drop_duplicates()
        d.columns = EQ_COMPONENT_NAMES + ['modifier']

        # For the ID generation process, we decided to replace empty or NAN values with 0
        d = d.replace("", ABSENT)
        d['modifier'] = d['modifier'].replace("^normal$", "PATO:0000461")
        d['modifier'] = d['modifier'].replace("^abnormal$", "PATO:0000460")
        # Movie modifier column to the beginning
        mod = d['modifier']
        d.drop(labels=['modifier'], axis=1,inplace = True)
        if self.include_modifier:
            d.insert(0, 'modifier', mod)
        d['id_raw'] = d.apply(eq_key, axis=1) #generate a unique id string
        d['id'] = d['id_raw'].apply(lambda x: self.correct_id(x))
        return d
        
    def load_zfin_phenotype_fish(self):
        return self.load_zfin_data(self.zfin_fish_data_file, self.phenotype_fish_eq_columns, self.phenotype_fish_modifier_column)

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
        ids = sorted(list(set(self.reserved_ids+df['iri'].tolist())))
        with open(reserved_ids_file, 'w') as f:
            for item in ids:
                f.write("%s\n" % item)

# Get and clean complete set of currently assigned ZP ids (can be generated using the respective make goal in src/curation/Makefile

