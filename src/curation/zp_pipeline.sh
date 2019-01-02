#!/bin/sh

# python3 ../scripts/zp_annotation_to_id_map.py id_map.tsv <----- THIS IS TO INITIALISE ZP FROM SCRATCH. DO NOT UNCOMMENT UNLESS YOU WANT TO BREAK CURRENT ZP-ZFINEQ ASSIGNMENTS!
make -f make.reservediris reserved_iris.txt -B
python3 ../scripts/zp_update_id_map.py id_map.tsv deprecated_id_map.tsv reserved_iris.txt 100000
python3 ../scripts/zp_dosdp.py id_map.tsv ../patterns/data/auto pattern_assignments.txt
python3 ../scripts/zp_kb.py id_map.tsv zp_annotations_to_iri.tsv kb_zp.ttl
