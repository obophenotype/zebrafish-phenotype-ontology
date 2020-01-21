#!/bin/sh
set -e
IMP=true
PAT=true
sh run.sh make IMP=false zp_pipeline -B
sh run.sh make IMP=$IMP PAT=$PAT SRC=zp-edit-release.owl prepare_release -B
