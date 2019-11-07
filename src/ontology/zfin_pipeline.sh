#!/bin/sh

set -e

# python3 ../scripts/zp_annotation_to_id_map.py id_map_zfin.tsv <----- THIS IS TO INITIALISE ZP FROM SCRATCH. DO NOT UNCOMMENT UNLESS YOU WANT TO BREAK CURRENT ZP-ZFINEQ ASSIGNMENTS!

cd ../curation 

python3 ../scripts/zp_update_id_map.py id_map_zfin.tsv deprecated_id_map.tsv ../curation/tmp/reserved_iris.txt 100000 || exit 1

python3 ../scripts/zfin_obsoletion.py deprecated_id_map.tsv ../templates/obsolete.tsv ../templates/df_obsolete_candidates.txt ../ontology/zp_labels.csv || exit 1

python3 ../scripts/zp_dosdp.py id_map_zfin.tsv ../patterns/data/zfin ../templates/obsolete.tsv pattern_assignments.txt ../ontology/zp_labels.csv || exit 1

for i in ../patterns/data/zfin/*.tsv; do
    python3 ../scripts/zp_extract_upheno.py "$i" || exit 1
done

python3 ../scripts/zp_fish_data.py id_map_zfin.tsv zp_zfin_phenotype_fish.tsv || exit 1

python3 ../scripts/zp_kb.py id_map_zfin.tsv zp_zfin_phenoGeneCleanData_fish.tsv kb_zp.ttl || exit 1


cd ../ontology
