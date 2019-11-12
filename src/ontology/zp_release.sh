#!/bin/sh
set -e
sh run.sh make IMP=false zp_pipeline -B
sh run.sh make IMP=false PAT=false SRC=zp-edit-release.owl prepare_release -B
