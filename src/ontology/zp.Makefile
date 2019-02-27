AO = zfa.owl
AUTOPATTERNACCESSION = 99999
ANATOMYPATTERNDIR=../patterns/data/anatomy
ZFINPATTERNDIR = ../patterns/data/zfin
MANUALPATTERNDIR = ../patterns/data/manual
OBOPURL=http://purl.obolibrary.org/obo/
PURL=http://purl.obolibrary.org/obo/ZP_
ANATOMYLOCATION = $(OBOPURL)""$(AO)
MANUALPATTERNS=$(patsubst %.tsv, $(MANUALPATTERNDIR)/%.tsv, $(notdir $(wildcard ../patterns/data/manual/*.tsv)))

$(PATTERNDIR)/data/zfin/%.ofn: $(PATTERNDIR)/data/zfin/%.tsv $(PATTERNDIR)/dosdp-patterns/%.yaml $(SRC) all_imports .FORCE
	@$(if $(findstring _label.ofn,$@),dosdp-tools generate --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true --outfile=$@,dosdp-tools generate --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true  --restrict-axioms-to=logical --outfile=$@)


../curation/tmp/$(AO):
	wget --no-check-certificate $(ANATOMYLOCATION) -O $@ &&\
  robot reason --reasoner ELK --input $@ --output $@.tmp.owl && mv $@.tmp.owl $@

../curation/tmp/subclasses.sparql:
	sh ../scripts/generate_sparql_subclass_query.sh ../curation/blacklist_branch.txt $@

../curation/tmp/blacklist.txt: ../curation/tmp/$(AO) ../curation/tmp/subclasses.sparql
	robot query --input $< --query ../curation/tmp/subclasses.sparql ../curation/tmp/blacklist_tmp.txt
	cat ../curation/tmp/blacklist_tmp.txt ../curation/blacklist.txt | grep -Eo '($(OBOPURL))[^[:space:]"]+' | sort | uniq >$@

../curation/tmp/anatomy_seed.txt: ../curation/tmp/$(AO) ../curation/tmp/blacklist.txt
	robot query -f csv -i ../curation/tmp/$(AO) --query ../sparql/zfa_terms.sparql $@.tmp
	sort -o $@.tmp $@.tmp
	sort -o ../curation/tmp/blacklist.txt ../curation/tmp/blacklist.txt
	python3 ../scripts/blacklist.py ../curation/tmp/anatomy_seed.txt.tmp ../curation/tmp/blacklist.txt $@

anatomy_tsv: ../curation/tmp/anatomy_seed.txt reserved_iris.txt 
	python3 ../scripts/add_anatomy_terms.py $(ANATOMYPATTERNDIR)/abnormalAnatomicalEntity.tsv $< reserved_iris.txt $(AUTOPATTERNACCESSION) $(PURL)

zp_labels.csv:
	robot query -f csv -i ../patterns/definitions.owl --query ../sparql/zp_label_terms.sparql $@

clean:
	rm -rf ../curation/tmp/*
	
anatomy_pipeline: clean prepare_patterns anatomy_tsv
	
zfin_pipeline: clean prepare_patterns reserved_iris.txt
	sh zp_pipeline.sh
	
manual_pipeline: clean prepare_patterns reserved_iris.txt
	for pattern in $(MANUALPATTERNS); do \
		python3 ../scripts/assign_unique_ids.py $$pattern reserved_iris.txt $(AUTOPATTERNACCESSION) $(PURL) ; \
	done

zp_pipeline: zfin_pipeline anatomy_pipeline manual_pipeline prepare_release

####################################################################
### Pipeline for determining all reserved_iris across ZP ###########

# Index all current patterns
ANATOMYPATTERNS=$(patsubst %.tsv, $(ANATOMYPATTERNDIR)/%.tsv, $(notdir $(wildcard ../patterns/data/anatomy/*.tsv)))
#ZFINPATTERNS=$(patsubst %.tsv, $(ZFINPATTERNDIR)/%.tsv, $(notdir $(wildcard ../patterns/data/zfin/*.tsv)))
pattern_term_lists_anatomy := $(patsubst %.tsv, $(ANATOMYPATTERNDIR)/%.txt, $(notdir $(wildcard ../patterns/data/anatomy/*.tsv)))
pattern_term_lists_manual := $(patsubst %.tsv, $(MANUALPATTERNDIR)/%.txt, $(notdir $(wildcard ../patterns/data/manual/*.tsv)))
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

reserved_iris.txt:  $(pattern_term_lists_anatomy) $(pattern_term_lists_manual) ../curation/tmp/id_map_terms.txt ../curation/tmp/idmap_removed_ambiguous_terms.txt ../curation/tmp/idmap_removed_incomplete_terms.txt
	robot query -f csv -i ../ontology/zp-edit.owl --query ../sparql/zpo_terms.sparql ../curation/tmp/editseed.txt &&\
	cat $^ ../curation/tmp/editseed.txt | sort | uniq > $@
