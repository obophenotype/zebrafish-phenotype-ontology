#!/bin/sh
set -e
ODK=v1.6.1
# A release always starts from fresh ZFIN data
ODK_TAG=$ODK ./run.sh make refresh_zfin_data
ODK_TAG=$ODK ./run.sh make -B zp_labels.csv
ODK_TAG=$ODK ./run.sh make IMP=false PAT=true MIR=false COMP=false zp_pipeline_prepare_data
ODK_TAG=$ODK ./run.sh make IMP=false PAT=true MIR=false COMP=true templates patterns
ODK_TAG=$ODK ./run.sh make IMP=true PAT=false MIR=true COMP=false refresh-merged
ODK_TAG=$ODK ./run.sh make IMP=false PAT=true MIR=false COMP=true patterns
SHARED="remove -T blacklist_eqs.txt --axioms equivalent --preserve-structure false query --update ../sparql/rename-obsolete-classes.ru "
ODK_TAG=$ODK ./run.sh make SHARED_ROBOT_COMMANDS="$SHARED" prepare_release_fast
