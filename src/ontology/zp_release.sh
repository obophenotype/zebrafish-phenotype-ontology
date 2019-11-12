#!/bin/sh
set -e
sh run.sh make zp_pipeline
sh run.sh make SRC=zp-edit-release.owl prepare_release
