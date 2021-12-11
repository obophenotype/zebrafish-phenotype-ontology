#!/bin/sh
set -e
IMP=false
PAT=true
sh run.sh make IMP=false PAT=false zp_pipeline_prepare_data -B
sh run.sh make IMP=false PAT=true templates patterns -B
sh run.sh make IMP=$IMP PAT=false all_imports -B
sh run.sh make IMP=false PAT=true templates patterns -B
sh run.sh make IMP=$IMP PAT=true preprocess -B
sh run.sh make IMP=false PAT=false SRC=zp-edit-release.owl prepare_release -B
