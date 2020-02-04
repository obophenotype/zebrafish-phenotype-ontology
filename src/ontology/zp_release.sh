#!/bin/sh
set -e
IMP=true
PAT=true
sh run.sh make IMP=false zp_pipeline_prepare_data -B
sh run.sh make IMP=$IMP PAT=$PAT zp_pipeline_prepare_ontology -B
sh run.sh make IMP=false PAT=false SRC=zp-edit-release.owl prepare_release -B
