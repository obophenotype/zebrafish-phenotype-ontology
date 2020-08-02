#!/bin/sh
set -e
make IMP=false PAT=false zp_pipeline_prepare_data -B
make IMP=false PAT=true templates patterns -B
make IMP=true PAT=false all_imports -B
make IMP=false PAT=true templates patterns -B
make IMP=true PAT=true preprocess -B
make IMP=false PAT=false SRC=zp-edit-release.owl prepare_release -B
