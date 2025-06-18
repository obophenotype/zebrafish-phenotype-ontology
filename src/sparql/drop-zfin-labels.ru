PREFIX iao: <http://purl.obolibrary.org/obo/IAO_>
PREFIX infores: <https://w3id.org/biolink/infores/>
PREFIX obo: <http://purl.obolibrary.org/obo/>
PREFIX oboInOwl: <http://www.geneontology.org/formats/oboInOwl#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>

DELETE {
  ?entity rdfs:label ?zfinLabel .
  ?entity obo:IAO_0000115 ?zfinDefinition .
}

INSERT {
  [
    a owl:Axiom ;
    owl:annotatedSource ?entity ;
    owl:annotatedProperty oboInOwl:hasExactSynonym ;
    owl:annotatedTarget ?zfinLabel ;
    oboInOwl:source infores:zfin
  ]
}

WHERE {
  ?entity a owl:Class .
  ?entity rdfs:label ?zfinLabel .
  ?entity obo:IAO_0000115 ?zfinDefinition .
  FILTER(isIRI(?entity) && regex(str(?entity), "ZP_"))
  FILTER(STRENDS(?zfinLabel, ", abnormal"))
  FILTER(STRSTARTS(?zfinDefinition, "Abnormal(ly)"))
}
