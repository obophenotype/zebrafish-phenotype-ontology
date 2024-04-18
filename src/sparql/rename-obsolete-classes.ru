PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

DELETE {
    ?entity rdfs:label ?oldLabel
}
INSERT {
    ?entity rdfs:label ?newLabel
}
WHERE {
    ?entity rdfs:label ?oldLabel .
    FILTER(STRSTARTS(LCASE(STR(?oldLabel)), "obsolete "))
    BIND(REPLACE(STR(?oldLabel), "^obsolete\\s+", "", "i") AS ?newString)
    BIND(?newString AS ?newLabel)
}
