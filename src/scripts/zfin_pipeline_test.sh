#!/bin/sh

set -e

# python3 ../scripts/zp_annotation_to_id_map.py id_map_zfin.tsv <----- THIS IS TO INITIALISE ZP FROM SCRATCH. DO NOT UNCOMMENT UNLESS YOU WANT TO BREAK CURRENT ZP-ZFINEQ ASSIGNMENTS!

cd ../curation 

python3 ../scripts/zp_update_id_map.py id_map_zfin.tsv deprecated_id_map.tsv ../curation/tmp/reserved_iris.txt 100000 || exit 1

cd ../ontology
