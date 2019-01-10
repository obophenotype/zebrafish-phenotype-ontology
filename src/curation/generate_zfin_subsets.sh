#!/usr/bin/env bash

python3 ../scripts/zp_subset_zfin_data.py unsat.txt zp_zfin_phenotype_fish.tsv all
python3 ../scripts/zp_subset_zfin_data.py bspo.txt zp_zfin_phenotype_fish.tsv all
python3 ../scripts/zp_subset_zfin_data.py unsat.txt zp_zfin_phenoGeneCleanData_fish.tsv all
python3 ../scripts/zp_subset_zfin_data.py bspo.txt zp_zfin_phenoGeneCleanData_fish.tsv all

