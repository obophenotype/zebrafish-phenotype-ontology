# Curation pipeline

## What is the role of each file

id_map.tsv_removed.tsv
These are 140 mappings involving a total of 74 ZP ids that were used in previous versions of the ZP, but are now excluded because their mapping to ZFIN EQs was ambiguous. EQs in ZFIN that were mapped that way now have new ids. However, just to be save, it makes sense to try and avoid re-using the 74 ZP ids in this file -> they should be added to reserved_iris.txt before any automatic curation task is run.

