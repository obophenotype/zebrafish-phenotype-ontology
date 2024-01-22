#!/bin/sh
set -e
IMP=true
PAT=true
ODK=v1.4.3
ODK_TAG=$ODK ./run.sh make IMP=false PAT=false MIR=false COMP=false zp_pipeline_prepare_data -B
ODK_TAG=$ODK ./run.sh make IMP=false PAT=true MIR=false COMP=true templates patterns -B
ODK_TAG=$ODK ./run.sh make IMP=$IMP PAT=false MIR=$IMP COMP=false refresh-merged -B
ODK_TAG=$ODK ./run.sh make IMP=false PAT=true MIR=false COMP=true patterns -B
SHARED="remove -T blacklist_eqs.txt --axioms equivalent --preserve-structure false"
ODK_TAG=$ODK ./run.sh make SHARED_ROBOT_COMMANDS="$SHARED" prepare_release_fast -B
