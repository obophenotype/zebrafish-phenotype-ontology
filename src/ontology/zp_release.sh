#!/bin/sh
set -e
IMP=true
PAT=true
sh run.sh make IMP=false PAT=false zp_pipeline_prepare_data -B
sh run.sh make IMP=false PAT=true templates patterns -B
sh run.sh make IMP=true PAT=false all_imports -B
sh run.sh make IMP=false PAT=true templates patterns -B
sh run.sh make IMP=true PAT=true preprocess -B
sh run.sh make IMP=false PAT=false SRC=zp-edit-release.owl prepare_release -B
