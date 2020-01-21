#!/bin/sh

DROPLABELPYTHON=$1
PATTERNSDIR=$2
for filename in $PATTERNSDIR/*.tsv; do
    [ -e "$filename" ] || continue
    # ... rest of the loop body
    echo $filename
    python $DROPLABELPYTHON $filename
done
