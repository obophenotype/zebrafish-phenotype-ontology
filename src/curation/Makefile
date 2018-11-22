ANATOMY = zfa.owl
ANATOMYLOCATION = http://purl.obolibrary.org/obo/zfa.owl
AUTOPATTERNS = ../patterns/data/auto/
AUTOPATTERNACCESSION = 99999
PURL=http://purl.obolibrary.org/obo/ZP_

#https://raw.githubusercontent.com/obophenotype/upheno/master/src


MANUALPATTERNS=$(patsubst %.tsv, $(MANUALPATTERNDIR)/%.tsv, $(notdir $(wildcard ../patterns/data/manual/*.tsv)))
AUTOPATTERNS=$(patsubst %.tsv, $(AUTOPATTERNDIR)/%.tsv, $(notdir $(wildcard ../patterns/data/auto/*.tsv)))
AUTOPATTERNDIR=../patterns/data/auto
MANUALPATTERNDIR=../patterns/data/manual
pattern_term_lists_auto := $(patsubst %.tsv, $(AUTOPATTERNDIR)/%_terms.txt, $(notdir $(wildcard ../patterns/data/auto/*.tsv)))
pattern_term_lists_manual := $(patsubst %.tsv, $(MANUALPATTERNDIR)/%_terms.txt, $(notdir $(wildcard ../patterns/data/manual/*.tsv)))

../patterns/data/manual/%_terms.txt: ../patterns/data/manual/%.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

../patterns/data/auto/%_terms.txt: ../patterns/data/auto/%.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

id_map_terms.txt: 
	grep -Eo '($(PURL))[^[:space:]"]+' id_map.tsv | sort | uniq > $@
		
id_map_removed_terms.txt: 
	grep -Eo '($(PURL))[^[:space:]"]+' id_map.tsv_removed.tsv | sort | uniq > $@

reserved_iris.txt: $(pattern_term_lists_auto) $(pattern_term_lists_manual) id_map_terms.txt id_map_removed_terms.txt
	robot query -f csv -i ../ontology/zp-edit.owl --query ../sparql/zpo_terms.sparql editseed.txt
	cat $(pattern_term_lists_auto) $(pattern_term_lists_manual) editseed.txt | sort | uniq >$@
 
anatomy_seed.txt: 
	curl -L -O $(ANATOMYLOCATION)
	robot query -f csv -i $(ANATOMY) --query ../sparql/zfa_terms.sparql $@
	rm $(ANATOMY)

#$(AUTOPATTERNDIR)/abnormal.tsv: anatomy_seed.txt
#	cp $< $@
#	sed -i '' "1s/.*/entity/" $@
#	python3 ../scripts/assign_unique_ids.py $@ id_map.tsv reserved_iris.txt $(AUTOPATTERNACCESSION) $(PURL)

#$(AUTOPATTERNDIR)/abnormalMorphology.tsv: anatomy_seed.txt
#	cp $< $@
#	sed -i '' "1s/.*/entity/" $@
#	python3 ../scripts/assign_unique_ids.py $@ id_map.tsv reserved_iris.txt $(AUTOPATTERNACCESSION) $(PURL)

$(AUTOPATTERNDIR)/%.tsv:
	python3 ../scripts/zp_extract_upheno.py $@

$(MANUALPATTERNDIR)/%.tsv:
	python3 ../scripts/assign_unique_ids.py $@ id_map.tsv reserved_iris.txt $(AUTOPATTERNACCESSION) $(PURL)

auto_patterns: $(AUTOPATTERNDIR)/abnormal.tsv $(AUTOPATTERNDIR)/abnormalMorphology.tsv 

manual_pattern_iris: $(MANUALPATTERNS)

# RUNNING THE FOLLOWING GOALS RESULTS IN LOSING ALL ZP-ZFINEQ MAPPINGS!	
initialise_id_map:
	python3 ../scripts/zp_annotation_to_id_map.py id_map.tsv

kb_zp.ttl:
	python3 ../scripts/zp_kb.py id_map.tsv zp_annotations_to_iri.tsv $@
	
update_zp_id_map: reserved_iris.txt
	python3 ../scripts/zp_update_id_map.py id_map.tsv deprecated_id_map.tsv $< 100000

generate_dosdp:
	python3 ../scripts/zp_dosdp.py id_map.tsv $(AUTOPATTERNDIR) pattern_assignments.txt

auto_pattern_iris: $(AUTOPATTERNS)