# Change rdfs:label values from uPheno patterns into exact synonyms, and mark
# that synonym as the preferred label for ZAPP.
#
# infores:zapp is a stand-in for the moment. It should be updated when ZAPP
# has a stable PURL.

PREFIX rdfs:     <http://www.w3.org/2000/01/rdf-schema#>
PREFIX owl:      <http://www.w3.org/2002/07/owl#>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX OMO:      <http://purl.obolibrary.org/obo/OMO_>
PREFIX infores:  <https://w3id.org/information-resource-registry/>

DELETE {
  ?class rdfs:label ?label .
  ?ax owl:annotatedProperty rdfs:label .
}
INSERT {
  ?class oboInOwl:hasExactSynonym ?label .
  ?ax owl:annotatedProperty oboInOwl:hasExactSynonym ;
      OMO:0002001 infores:zapp .
}
WHERE {
  ?class rdfs:label ?label .
  FILTER(STRSTARTS(STR(?class), "http://purl.obolibrary.org/obo/ZP_"))

  ?ax a owl:Axiom ;
      owl:annotatedSource ?class ;
      owl:annotatedProperty rdfs:label ;
      owl:annotatedTarget ?label .
}
