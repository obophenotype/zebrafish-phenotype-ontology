#!/bin/sh
set -e
IMP=true
PAT=true
make IMP=false zp_pipeline -B
make IMP=$IMP PAT=$PAT SRC=zp-edit-release.owl prepare_release -B
