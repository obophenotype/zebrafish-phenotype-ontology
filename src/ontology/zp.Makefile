ACCESSION = 99999
ANATOMYPDIR=../patterns/data/anatomy
PROCESSPDIR=../patterns/data/process
ZFINPDIR = ../patterns/data/zfin
MANUALPDIR = ../patterns/data/manual

OBOPURL=http://purl.obolibrary.org/obo/
PURL=$(OBOPURL)"ZP_"

MANUALPATTERNS=$(patsubst %.tsv, $(MANUALPATTERNDIR)/%.tsv, $(notdir $(wildcard ../patterns/data/manual/*.tsv)))

$(PATTERNDIR)/data/zfin/%.ofn: $(PATTERNDIR)/data/zfin/%.tsv $(PATTERNDIR)/dosdp-patterns/%.yaml $(SRC) all_imports .FORCE
	@$(if $(findstring _label.ofn,$@),dosdp-tools generate --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true --outfile=$@,dosdp-tools generate --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true  --restrict-axioms-to=logical --outfile=$@)

#### 
# Defiinitions.owl overwrite (occurs in hack!)
####

$(PATTERNDIR)/definitions.owl: prepare_patterns $(individual_patterns_default)   $(individual_patterns_manual) $(individual_patterns_anatomy) $(individual_patterns_zfin) $(individual_patterns_process)
	$(ROBOT) merge $(addprefix -i , $(individual_patterns_default))   $(addprefix -i , $(individual_patterns_manual)) $(addprefix -i , $(individual_patterns_anatomy)) $(addprefix -i , $(individual_patterns_zfin)) $(addprefix -i , $(individual_patterns_process)) annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl  --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions.owl -o definitions.ofn &&\
	mv definitions.ofn $@ &&\
	echo 'OCCURS IN HACK skipped!'
	#java -jar ../scripts/zp_occurs_in_hack.jar $@ ../curation/unsat.txt $@ 

#### 
# Pipelines for intermedidate Phenotypes
####

clean:
	rm -rf ../curation/tmp/*
	
zp_labels.csv:
	robot query -f csv -i ../patterns/definitions.owl --query ../sparql/zp_label_terms.sparql $@


# Loading sources

PSOURCES=zfa go
PSOURCE_BLACKLISTS = $(patsubst %, ../curation/tmp/%_blacklist.txt, $(PSOURCES))
PSOURCE_SOURCES = $(patsubst %, ../curation/tmp/%.owl, $(PSOURCES))

../curation/tmp/zfa.owl:
	wget --no-check-certificate $(OBOPURL)"zfa.owl" -O $@ &&\
	robot reason --reasoner ELK --input $@ --output $@.tmp.owl && mv $@.tmp.owl $@
	
../curation/tmp/go.owl:
	cp ../ontology/imports/go_import.owl $@ &&\
	robot reason --reasoner ELK --input $@ --output $@.tmp.owl && mv $@.tmp.owl $@

# Preparing the blacklist (classes to be ignored by the pipeline)
## Preparing sparql query that allows obtaining subclasses ignoring the blacklist
../curation/tmp/subclasses.sparql:
	sh ../scripts/generate_sparql_subclass_query.sh ../curation/blacklist_branch.txt $@

../curation/tmp/%_blacklist.txt: ../curation/tmp/%.owl ../curation/tmp/subclasses.sparql
	robot query --input $< --query ../curation/tmp/subclasses.sparql $@

../curation/tmp/blacklist.txt: $(PSOURCE_BLACKLISTS)
	cat $(PSOURCE_BLACKLISTS) ../curation/blacklist.txt | grep -Eo '($(OBOPURL))[^[:space:]"]+' | sort | uniq > $@

../curation/tmp/%_seed.txt: ../curation/tmp/%.owl ../curation/tmp/blacklist.txt ../sparql/%_terms.sparql
	robot query -f csv -i $< --query ../sparql/$*_terms.sparql $@.tmp
	sort -o $@.tmp $@.tmp
	sort -o ../curation/tmp/blacklist.txt ../curation/tmp/blacklist.txt
	python3 ../scripts/blacklist.py $@.tmp ../curation/tmp/blacklist.txt $@

anatomy_tsv: ../curation/tmp/zfa_seed.txt reserved_iris.txt 
	python3 ../scripts/add_terms_to_column.py $(ANATOMYPDIR)/abnormalAnatomicalEntity.tsv $< anatomical_entity reserved_iris.txt ../curation/id_map_zfin.tsv $(ACCESSION) $(PURL)

go_tsv: ../curation/tmp/go_seed.txt reserved_iris.txt 
	python3 ../scripts/add_terms_to_column.py $(PROCESSPDIR)/abnormalBiologicalProcess.tsv $< biological_process reserved_iris.txt ../curation/id_map_zfin.tsv $(ACCESSION) $(PURL)

#### Main pipeline goals:

anatomy_pipeline: clean prepare_patterns anatomy_tsv
	
go_pipeline: clean prepare_patterns go_tsv
	
zfin_pipeline: clean prepare_patterns reserved_iris.txt zp_labels.csv
	sh zp_pipeline.sh
	
manual_pipeline: clean prepare_patterns reserved_iris.txt
	for pattern in $(MANUALPATTERNS); do \
		python3 ../scripts/assign_unique_ids.py $$pattern reserved_iris.txt $(ACCESSION) $(PURL) ; \
	done

zp_pipeline: zfin_pipeline anatomy_pipeline go_pipeline manual_pipeline prepare_release

####################################################################
### Pipeline for determining all reserved_iris across ZP ###########

# Index all current patterns
pattern_term_lists_anatomy := $(patsubst %.tsv, $(ANATOMYPDIR)/%.txt, $(notdir $(wildcard ../patterns/data/anatomy/*.tsv)))
pattern_term_lists_process := $(patsubst %.tsv, $(PROCESSPDIR)/%.txt, $(notdir $(wildcard ../patterns/data/process/*.tsv)))
pattern_term_lists_manual := $(patsubst %.tsv, $(MANUALPDIR)/%.txt, $(notdir $(wildcard ../patterns/data/manual/*.tsv)))
#pattern_term_lists_zfin := $(patsubst %.tsv, $(ZFINPATTERNS)/%_terms.txt, $(notdir $(wildcard ../patterns/data/zfin/*.tsv)))

../curation/tmp/id_map_terms.txt.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

../curation/tmp/id_map_terms.txt.zp.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
../curation/tmp/id_map_terms.txt: ../curation/tmp/id_map_terms.txt.tmp ../curation/tmp/id_map_terms.txt.zp.tmp
	cat $^ | sort | uniq > $@

../curation/tmp/idmap_removed_ambiguous_terms.txt.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

../curation/tmp/idmap_removed_ambiguous_terms.txt.zp.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
../curation/tmp/idmap_removed_ambiguous_terms.txt: ../curation/tmp/idmap_removed_ambiguous_terms.txt.tmp ../curation/tmp/idmap_removed_ambiguous_terms.txt.zp.tmp
	cat $^ | sort | uniq > $@

../curation/tmp/idmap_removed_incomplete_terms.txt.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

../curation/tmp/idmap_removed_incomplete_terms.txt.zp.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
../curation/tmp/idmap_removed_incomplete_terms.txt: ../curation/tmp/idmap_removed_incomplete_terms.txt.tmp ../curation/tmp/idmap_removed_incomplete_terms.txt.zp.tmp
	cat $^ | sort | uniq > $@

reserved_iris.txt:  $(pattern_term_lists_anatomy) $(pattern_term_lists_process) $(pattern_term_lists_manual) ../curation/tmp/id_map_terms.txt ../curation/tmp/idmap_removed_ambiguous_terms.txt ../curation/tmp/idmap_removed_incomplete_terms.txt
	robot query -f csv -i ../ontology/zp-edit.owl --query ../sparql/zpo_terms.sparql ../curation/tmp/editseed.txt &&\
	cat $^ ../curation/tmp/editseed.txt | sort | uniq > $@
