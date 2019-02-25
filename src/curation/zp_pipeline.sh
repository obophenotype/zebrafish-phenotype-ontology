#!/bin/sh

# python3 ../scripts/zp_annotation_to_id_map.py id_map_zfin.tsv <----- THIS IS TO INITIALISE ZP FROM SCRATCH. DO NOT UNCOMMENT UNLESS YOU WANT TO BREAK CURRENT ZP-ZFINEQ ASSIGNMENTS!
cd ../ontology && sh run.sh make zfin_pipeline -B && 
python3 ../scripts/zp_update_id_map.py id_map_zfin.tsv deprecated_id_map.tsv reserved_iris.txt 100000
python3 ../scripts/zp_dosdp.py id_map_zfin.tsv ../patterns/data/auto pattern_assignments.txt
python3 ../scripts/zp_fish_data.py id_map_zfin.tsv zp_zfin_phenotype_fish.tsv
python3 ../scripts/zp_kb.py id_map_zfin.tsv zp_zfin_phenoGeneCleanData_fish.tsv kb_zp.ttl
