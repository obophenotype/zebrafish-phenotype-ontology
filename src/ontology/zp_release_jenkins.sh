#!/bin/sh
set -e
make IMP=true zp_pipeline_prepare_ontology -B
make IMP=true PAT=true SRC=zp-edit-release.owl prepare_release -B
