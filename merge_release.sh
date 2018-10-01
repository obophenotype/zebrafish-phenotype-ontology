#!/bin/sh
cd src/ontology/
./run.sh robot merge --input ../../zp.owl annotate --ontology-iri https://purl.obolibrary.org/obo/zp/zp_merged.owl --output ../../zp_merged.owl
