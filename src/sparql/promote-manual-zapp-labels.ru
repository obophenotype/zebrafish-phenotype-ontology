PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

DELETE {
  ?entity rdfs:label ?originalLabel .
  ?originalLabelAxiom owl:annotatedProperty rdfs:label .

  ?entity skos:preferredLabel ?zappLabel .
  ?zappLabelAxiom owl:annotatedProperty skos:preferredLabel .
}

INSERT {
  ?entity oboInOwl:exactSynonym ?originalLabel .
  ?originalLabelAxiom owl:annotatedProperty oboInOwl:exactSynonym .

  ?entity rdfs:label ?zappLabel .
  ?zappLabelAxiom owl:annotatedProperty rdfs:label .
}

WHERE {
  ?entity a owl:Class .
  ?entity skos:preferredLabel ?zappLabel .
  ?entity rdfs:label ?originalLabel .

  ?zappLabelAxiom
    a owl:Axiom ;
    owl:annotatedSource ?entity ;
    owl:annotatedProperty skos:preferredLabel ;
    owl:annotatedTarget ?zappLabel .

  ?originalLabelAxiom
    a owl:Axiom ;
    owl:annotatedSource ?entity ;
    owl:annotatedProperty rdfs:label ;
    owl:annotatedTarget ?originalLabel .

  FILTER(isIRI(?entity) && regex(str(?entity), "ZP_"))
}
