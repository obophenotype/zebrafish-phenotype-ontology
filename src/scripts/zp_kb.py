import pandas as pd
import copy
import sys

# Author: Nicolas Matentzoglu
# Date: 21.11.2018
# Samples, Phenotypes and Ontologies Team, EMBL-EBI

# This script takes in the ZFIN EQ to GENE mappings and generates a little RDF knowledge graph from them referencing
# the precomposed ZP classes. This file can be used to affectively query and group annotations related to phenotype,
# for example: Find all annotations pertaining to morphological abnormalities of any anatomical part.

id_map = sys.argv[1] # The current ZP-ZFIN EQ id map
gene_annotation_mappings = sys.argv[2] # The desired location for the resulting gene annotation to ZP mappings
annotation_ttl = sys.argv[3] # The desired output location of the KB

tsv = 'https://zfin.org/downloads/phenoGeneCleanData_fish.txt'

# LOAD ZFIN GENE ANNOTATION DATA
df_zfin = pd.read_csv(tsv, sep='\t', header=None)
print("Number of gene annotations: "+str(len(df_zfin)))
print(df_zfin.shape)

#xxx=copy.deepcopy(df_zfin)
#df_zfin=copy.deepcopy(xxx)
# LOAD CURRENT ZP-ZFIN-EQ MAP

id_map = pd.read_csv(id_map, sep='\t')
print(id_map.shape)

# Generate ID string in ZFIN Gene annotation data and merge with ID MAP to get corresponding ZP identifier
functionalcolumns = pd.np.array([4,6,8,10,13,15,17])-1
df_zfin.update(df_zfin[functionalcolumns].fillna('0'))
print(len(df_zfin))
df_zfin['id'] = df_zfin[functionalcolumns].astype(str).apply('-'.join, axis=1)
df_zfin = pd.merge(df_zfin, id_map, on='id', how='left')
print(len(df_zfin))
df_zfin[functionalcolumns] = df_zfin[functionalcolumns].replace('^0$', '', regex=True)
print(len(df_zfin))

# Extract relevant GENE annotation columns (GENE id, Fish id, etc)
annotationcolumns = pd.np.array([1,3,12,19,21,22,23,24,25])-1
kb = df_zfin[annotationcolumns]
kb.columns = ["ZFINID", "GENEID","PHENOTYPETAG","FISHID","STARTSTAGEID","ENDSTAGEID","FISHENVIRONMENTID","PUBLICATIONID","FIGUREID"]
kb = kb.assign(IRI=df_zfin['iri'])
kb['IRI'].replace({'ZP:': 'http://purl.obolibrary.org/obo/ZP_'}, inplace=True,regex=True)
kb = kb.assign(ANID=df_zfin['id'])
#kb.head(3)

any_na_values = kb[pd.isnull(kb).any(axis=1)]
if len(any_na_values)>0:
    print("Warning: some columns do not have valid ZP ids yet!")
    print(any_na_values.head())

# CREATE TURTLE data
preamble = """@prefix : <http://zfin.org/zp/annotations#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix xml: <http://www.w3.org/XML/1998/namespace> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@base <http://zfin.org/zp/annotations> .

<http://zfin.org/zp/annotations> rdf:type owl:Ontology .


#################################################################
#    Annotation properties
#################################################################

###  http://zfin.org/zp/annotations#hasZFINID
:hasZFINID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasGENEID
:hasGENEID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .
           
###  http://zfin.org/zp/annotations#hasPHENOTYPETAG
:hasPHENOTYPETAG rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasFISHID
:hasFISHID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasSTARTSTAGEID
:hasSTARTSTAGEID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .
           
###  http://zfin.org/zp/annotations#hasENDSTAGEID
:hasENDSTAGEID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasFISHENVIRONMENTID
:hasFISHENVIRONMENTID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasPUBLICATIONID
:hasPUBLICATIONID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasFIGUREID
:hasFIGUREID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

###  http://zfin.org/zp/annotations#hasAssociatedEQID
:hasAssociatedEQID rdf:type owl:AnnotationProperty ;
           rdfs:subPropertyOf rdfs:comment .

#################################################################
#    Object Properties
#################################################################

###  http://zfin.org/zp/annotations#hasPhenotype
:hasPhenotype rdf:type owl:ObjectProperty .


#################################################################
#    Classes
#################################################################

"""
main = ""

iris = list(set(kb[kb.IRI.notnull()]["IRI"]))
###  http://purl.obolibrary.org/obo/ZP_0021318
for iri in iris:
    main += """
<%s> rdf:type owl:Class ;
        :hasX "%s" . 

""" % (iri,kb[kb.IRI==iri]['ANID'].iloc[0])

main += """
#################################################################
#    Individuals
#################################################################

"""

###  http://www.semanticweb.org/matentzn/ontologies/2018/9/untitled-ontology-320#testI

for index, row in kb.iterrows():
   main += """
:ZPK_%s rdf:type owl:NamedIndividual ,
        [ rdf:type owl:Restriction ;
          owl:onProperty :hasPhenotype ;
          owl:someValuesFrom <%s>
        ] ;
        :hasZFINID %s ;
        :hasGENEID "%s" ;
        :hasPHENOTYPETAG "%s" ;
        :hasFISHID "%s" ;
        :hasSTARTSTAGEID "%s" ;
        :hasENDSTAGEID "%s" ;
        :hasFISHENVIRONMENTID "%s" ;
        :hasPUBLICATIONID "%s" ;
        :hasFIGUREID "%s" .

""" % (row['ZFINID'], row['IRI'], row['ZFINID'], row['GENEID'], row['PHENOTYPETAG'], row['FISHID'], row['STARTSTAGEID'], row['ENDSTAGEID'], row['FISHENVIRONMENTID'], row['PUBLICATIONID'], row['FIGUREID'])

o = preamble + main

# Export KB and gene_annotation to ZP mappings.
text_file = open(annotation_ttl, "w")
text_file.write("%s" % o)
text_file.close()
kb.to_csv(gene_annotation_mappings, sep = '\t', index=False)

print("Exporting GENE-ZFIN-EQ annotations complete!")