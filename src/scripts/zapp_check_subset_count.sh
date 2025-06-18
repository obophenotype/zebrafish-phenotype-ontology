ZAPP_GRAPH_TERMS=$(grep 'owl:Class rdf:about="http://purl.obolibrary.org/obo/ZP_' zp-zapp.owl | sort | uniq)
ZAPP_GRAPH_COUNT=$(echo "$ZAPP_GRAPH_TERMS" | wc -l)

ZAPP_CSV_TERMS=$(grep 'ZP_' ../ontology/tmp/zp-zapp.csv | sort | uniq)
ZAPP_CSV_COUNT=$(echo "$ZAPP_CSV_TERMS" | wc -l)

echo "Expected number of ZAPP terms from CSV: $ZAPP_CSV_COUNT"
echo "Actual number of ZAPP terms in graph:   $ZAPP_GRAPH_COUNT"

if [ $ZAPP_GRAPH_COUNT -ne $ZAPP_CSV_COUNT ]
then
	exit 1
fi
