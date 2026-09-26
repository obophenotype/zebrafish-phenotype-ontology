# This makefile is not safe to run with `make -j`: several rules mutate
# shared state outside their own targets (`download_patterns` deletes and
# re-downloads pattern files that other rules read, and the ZFIN pipeline
# scripts rewrite files in place — see the stamps in "ZFIN pipeline steps").
.NOTPARALLEL:

AUTOPATTERNACCESSION = 99999
OBOPURL=http://purl.obolibrary.org/obo/
PURL=$(OBOPURL)ZP_
ZPCURIEPREFIX=ZP:

PDIR=../patterns/dosdp-patterns
TEMPLATEDIR=../templates
AUTOPATTERNDIR=../patterns/data/anatomy
MANUALPATTERNDIR=../patterns/data/manual
LABELPATTERNDIR=../patterns/data/labels
ZFINPATTERNDIR=../patterns/data/zfin
TODOPATTERNDIR=../patterns/data/todo
TMPDIR_CURATION=../curation/tmp

ID_MAP_ZFIN=../curation/id_map_zfin.tsv
ID_MAP=../curation/id_map.tsv

#$(PDIR)/data/zfin/%.ofn: $(PDIR)/data/zfin/%.tsv $(PDIR)/dosdp-patterns/%.yaml $(SRC) all_imports .FORCE
#	@$(if $(findstring _label.ofn,$@),dosdp-tools generate --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true --outfile=$@,dosdp-tools generate --infile=$< --template=$(word 2, $^) --ontology=$(word 3, $^) --obo-prefixes=true  --restrict-axioms-to=logical --outfile=$@)

#### 
# Defiinitions.owl overwrite (occurs in hack!)
####

mirror-zfa: | $(TMPDIR)
	if [ $(MIR) = true ] && [ $(IMP) = true ]; then curl -L $(OBOBASE)/zfa.owl --create-dirs -o $(MIRRORDIR)/zfa.owl --retry 4 --max-time 200 &&\
		$(ROBOT) merge -i $(MIRRORDIR)/zfa.owl remove --term BFO:0000050 convert -o $@.tmp.owl &&\
		mv $@.tmp.owl $(TMPDIR)/$@.owl; fi

ifeq ($(PAT),true)

# This goal is needed for the `dosdp-matches-matches` pipeline. 
# The pipeline, right now, only creates a report if there are matches.
# TODO: Make the pipeline create a report for classes where there are no matches.
$(TMPDIR)/zp-edit-merged-reasoned.owl: $(SRC) | $(TMPDIR)
	$(ROBOT) merge -i $< \
		-I https://raw.githubusercontent.com/obophenotype/uberon/refs/heads/master/src/ontology/bridge/cl-bridge-to-zfa.owl \
		-I https://raw.githubusercontent.com/obophenotype/uberon/refs/heads/master/src/ontology/bridge/uberon-bridge-to-zfa.owl \
		-I https://raw.githubusercontent.com/obophenotype/uberon/refs/heads/master/src/ontology/bridge/uberon-bridge-to-zfs.owl \
		reason -o $@	

DOSDP_TSV_FILES_MATCHES = $(wildcard $(PATTERNDIR)/data/matches/*.tsv)
DOSDP_PATTERN_NAMES_MATCHES = $(strip $(patsubst %.tsv, %, $(notdir $(DOSDP_TSV_FILES_MATCHES))))
DOSDP_OWL_FILES_MATCHES = $(foreach name, $(DOSDP_PATTERN_NAMES_MATCHES), $(PATTERNDIR)/data/matches/$(name).ofn)
DOSDP_TERM_FILES_MATCHES = $(foreach name, $(DOSDP_PATTERN_NAMES_MATCHES), $(PATTERNDIR)/data/matches/$(name).txt)
DOSDP_YAML_FILES_MATCHES = $(foreach name, $(DOSDP_PATTERN_NAMES_MATCHES), $(PATTERNDIR)/dosdp-patterns/$(name).yaml)

ALL_PATTERN_NAMES_WO_LABELS := $(filter-out %_label, $(ALL_PATTERN_NAMES))
ALL_PATTERN_NAMES_WO_LABELS_AND_ZFIN := $(filter-out abnormalQuality%, $(ALL_PATTERN_NAMES_WO_LABELS))

# We have to filter out the ZFIN patterns here, because some of them cannot be matched (they are missing EQs)
dosdp-matches-matches: $(TMPDIR)/zp-edit-merged-reasoned.owl
	$(DOSDPT) query --ontology=$< --catalog=$(CATALOG) --reasoner=elk --obo-prefixes=true --restrict-axioms-to=logical \
    --batch-patterns="$(ALL_PATTERN_NAMES_WO_LABELS_AND_ZFIN)" --template="$(PATTERNDIR)/dosdp-patterns" --outfile="$(PATTERNDIR)/data/matches/"

$(DOSDP_OWL_FILES_MATCHES): $(EDIT_PREPROCESSED) $(DOSDP_TSV_FILES_MATCHES) $(ALL_PATTERN_FILES)
	if [ "${DOSDP_TSV_FILES_MATCHES}" ]; then $(DOSDPT) generate --catalog=$(CATALOG) \
    --infile=$(PATTERNDIR)/data/matches --template=$(PATTERNDIR)/dosdp-patterns/ --batch-patterns="$(DOSDP_PATTERN_NAMES_MATCHES)" \
    --ontology=$< --obo-prefixes=true --restrict-axioms-to=annotation --add-axiom-source-annotation=true  --outfile=$(PATTERNDIR)/data/matches; fi

$(TMPDIR)/definitions-matches.owl: $(DOSDP_OWL_FILES_MATCHES) | $(TMPDIR)
	$(ROBOT) merge $(addprefix -i , $(DOSDP_OWL_FILES_MATCHES)) annotate --ontology-iri $(ONTBASE)/patterns/definitions-matches.owl --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions-matches.owl -o $@

$(TMPDIR)/definitions-matches-no-labels.owl: $(TMPDIR)/definitions-matches.owl | $(TMPDIR)
	$(ROBOT) remove -i $< --term rdfs:label --axioms annotation -o $@

../patterns/definitions.owl: $(DOSDP_OWL_FILES_DEFAULT) $(DOSDP_OWL_FILES_MANUAL) $(DOSDP_OWL_FILES_ZFIN)  $(DOSDP_OWL_FILES_ANATOMY)  $(DOSDP_OWL_FILES_PROCESS) $(TMPDIR)/definitions-matches-no-labels.owl
	#$(MAKE) update_patterns
	#$(MAKE) dosdp-matches-matches
	$(ROBOT) merge $(addprefix -i , $^) annotate --ontology-iri $(ONTBASE)/patterns/definitions.owl  --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions.owl -o definitions.ofn &&\
	mv definitions.ofn $@ &&\
	echo 'OCCURS IN HACK SKIPPED!'
	#java -jar ../scripts/zp_occurs_in_hack.jar $@ ../curation/unsat.txt $@

endif

#############################################
### Computing all reserved iris in ZP ######
#############################################
RESERVED_IRI=$(TMPDIR_CURATION)/reserved_iris.txt
ZP_SRC_SEED=$(TMPDIR_CURATION)/editseed.txt
pattern_term_lists_auto := $(patsubst %.tsv, $(AUTOPATTERNDIR)/%.txt, $(notdir $(wildcard $(AUTOPATTERNDIR)/*.tsv)))
pattern_term_lists_manual := $(patsubst %.tsv, $(MANUALPATTERNDIR)/%.txt, $(notdir $(wildcard $(MANUALPATTERNDIR)/*.tsv)))
pattern_term_lists_zfin := $(patsubst %.tsv, $(ZFINPATTERNDIR)/%.txt, $(notdir $(wildcard $(ZFINPATTERNDIR)/*.tsv)))


$(MANUALPATTERNDIR)/%.txt: $(MANUALPATTERNDIR)/%.tsv
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@

$(AUTOPATTERNDIR)/%.txt: $(AUTOPATTERNDIR)/%.tsv
	grep -Eo '(ZP)[^[:space:]"]+' $< | sort | uniq > $@
	
$(ZFINPATTERNDIR)/%.txt: $(ZFINPATTERNDIR)/%.tsv
	grep -Eo '(ZP)[^[:space:]"]+' $< | sort | uniq > $@

$(ZP_SRC_SEED): $(SRC) | $(TMPDIR_CURATION)
	robot query -f csv -i $< --use-graphs true --query ../sparql/zp_terms.sparql $@


$(TMPDIR_CURATION)/id_map_terms.txt.tmp: | $(TMPDIR_CURATION)
	grep -Eo '(ZP)[^[:space:]"]+' ../curation/id_map_zfin.tsv | sort | uniq > $@

$(TMPDIR_CURATION)/id_map_terms.txt.zp.tmp: | $(TMPDIR_CURATION)
	grep -Eo '(ZP)[:][^[:space:]"]+' ../curation/id_map.tsv | sort | uniq > $@	
	
$(TMPDIR_CURATION)/id_map_terms.txt: $(TMPDIR_CURATION)/id_map_terms.txt.tmp $(TMPDIR_CURATION)/id_map_terms.txt.zp.tmp | $(TMPDIR_CURATION)
	cat $^ | sort | uniq > $@


$(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.tmp: ../curation/id_map_zfin.tsv | $(TMPDIR_CURATION)
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

$(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.zp.tmp: ../curation/id_map_zfin.tsv | $(TMPDIR_CURATION)
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
$(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt: $(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.tmp $(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.zp.tmp | $(TMPDIR_CURATION)
	cat $^ | sort | uniq > $@


$(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.tmp: ../curation/id_map_zfin.tsv | $(TMPDIR_CURATION)
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

$(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.zp.tmp: ../curation/id_map_zfin.tsv | $(TMPDIR_CURATION)
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
$(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt: $(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.tmp $(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.zp.tmp | $(TMPDIR_CURATION)
	cat $^ | sort | uniq > $@


$(TMPDIR_CURATION)/obsoleted.txt.tmp: ../templates/obsolete.tsv | $(TMPDIR_CURATION)
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

$(TMPDIR_CURATION)/obsoleted.txt.zp.tmp: ../templates/obsolete.tsv | $(TMPDIR_CURATION)
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
$(TMPDIR_CURATION)/obsoleted.txt: $(TMPDIR_CURATION)/obsoleted.txt.tmp $(TMPDIR_CURATION)/obsoleted.txt.zp.tmp | $(TMPDIR_CURATION)
	cat $^ | sort | uniq > $@


$(RESERVED_IRI)_tmp.txt: $(pattern_term_lists_auto) $(pattern_term_lists_manual) $(pattern_term_lists_zfin) $(ZP_SRC_SEED) $(TMPDIR_CURATION)/id_map_terms.txt $(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt $(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt $(TMPDIR_CURATION)/obsoleted.txt
	cat $^ | sort | uniq > $@

$(RESERVED_IRI)_iri.txt: $(RESERVED_IRI)_tmp.txt
	cp $< $@
	sed -i 's!ZP[:]!$(PURL)!g' $@
	
$(RESERVED_IRI)_curie.txt: $(RESERVED_IRI)_tmp.txt
	cp $< $@
	sed -i 's!http[:][/][/]purl[.]obolibrary[.]org[/]obo[/]ZP[_]!ZP:!g' $@

$(RESERVED_IRI): $(RESERVED_IRI)_iri.txt $(RESERVED_IRI)_curie.txt
	cat $^ | sort | uniq > $@

reserved_iris: $(RESERVED_IRI)

#####################################################
### Filling in missing IRIs in manual patterns ######
#####################################################

MANUALPATTERNIDS=$(patsubst %.tsv, $(MANUALPATTERNDIR)/%_ids, $(notdir $(wildcard ../patterns/data/manual/*.tsv)))

$(MANUALPATTERNDIR)/%_ids: $(RESERVED_IRI) $(ID_MAP)
	python3 ../scripts/assign_unique_ids.py $(MANUALPATTERNDIR)/$*.tsv $(ID_MAP) $(RESERVED_IRI) $(AUTOPATTERNACCESSION) $(ZPCURIEPREFIX) $(PDIR)

missing_iris: $(MANUALPATTERNIDS)

###################################
### Running anatomy pipeline ######
###################################

ZFA_IRI = $(OBOPURL)zfa.owl
ZFA = $(TMPDIR_CURATION)/zfa.owl
PATTERN_CONFIG=../patterns/pattern-config.yaml
PIPELINE_DATA_PATH=../patterns/data/anatomy/
SPARQLDIR=../sparql

download_patterns: .FORCE
	cat $(PDIR)/external.txt | sed 's!.*/!!' | sed 's! !!g' |  xargs -I{} rm -f $(PDIR)/{}
	cat $(PDIR)/external.txt | sed 's! !!g' | xargs -I{} wget -q {} -P $(PDIR)/

$(ZFA): | $(TMPDIR_CURATION)
	$(ROBOT) reason --reasoner ELK -I $(ZFA_IRI) --output $@

anatomy_pipeline: download_patterns $(ZFA) $(ID_MAP) $(RESERVED_IRI) 
	echo "Using $(ZFA_IRI) for running anatomy pipeline, make sure this is correct!"
	python3 ../scripts/zp_anatomy_pipeline.py  $(ZFA) $(ID_MAP) $(RESERVED_IRI) $(PDIR) $(SPARQLDIR) $(PIPELINE_DATA_PATH) $(PATTERN_CONFIG) || exit 1

#########################################
### Generating all ROBOT templates ######
#########################################

TEMPLATESDIR=../templates

TEMPLATES=$(patsubst %.tsv, $(TEMPLATESDIR)/%.owl, $(notdir $(wildcard $(TEMPLATESDIR)/*.tsv)))

$(TEMPLATESDIR)/%.owl: $(TEMPLATESDIR)/%.tsv $(SRC)
	$(ROBOT) merge -i $(SRC) template --template $< --output $@ && \
	$(ROBOT) annotate --input $@ --ontology-iri $(ONTBASE)/components/$*.owl -o $@

templates: $(TEMPLATES)
	echo $(TEMPLATES)
	
	
#############################################
### ZFIN data snapshots            ##########
#############################################
# Snapshots are kept outside of $(TMPDIR_CURATION) so that `clean` does not
# remove them. Force a new download with `make refresh_zfin_data`.

ZFIN_SNAPSHOT_DIR=../curation/zfin-snapshots
ZFIN_FISH_DATA=$(ZFIN_SNAPSHOT_DIR)/phenotype_fish.txt
ZFIN_GENE_DATA=$(ZFIN_SNAPSHOT_DIR)/phenoGeneCleanData_fish.txt

$(ZFIN_FISH_DATA):
	curl -L --fail --create-dirs --retry 4 --max-time 400 -o $@.tmp https://zfin.org/downloads/phenotype_fish.txt
	mv $@.tmp $@

$(ZFIN_GENE_DATA):
	curl -L --fail --create-dirs --retry 4 --max-time 400 -o $@.tmp https://zfin.org/downloads/phenoGeneCleanData_fish.txt
	mv $@.tmp $@

.PHONY: refresh_zfin_data
refresh_zfin_data:
	rm -f $(ZFIN_FISH_DATA) $(ZFIN_GENE_DATA)
	$(MAKE) $(ZFIN_FISH_DATA) $(ZFIN_GENE_DATA)

#############################################
### WHOLE PIPELINE (main job)      ##########
#############################################

SHARED_ROBOT_COMMANDS += remove -T blacklist_eqs.txt --axioms equivalent --preserve-structure false \
	query --update ../sparql/rename-obsolete-classes.ru

.PHONY: .FORCE

$(ID_MAP): update_id_map

update_id_map: $(ID_MAP_ZFIN)
	python3 ../scripts/create_id_map.py ../patterns $(ID_MAP)

$(TMPDIR_CURATION):
	mkdir -p $@

.PHONY: zp-clean
zp-clean:
	rm -rf $(TMPDIR_CURATION)
	rm -f ../curation/kb_zp.ttl

clean: zp-clean

pattern_labels:
	rm -rf $(LABELPATTERNDIR)/*.tsv
	python3 ../scripts/zp_create_label_patterns.py ../patterns

zp_labels.csv:
	robot query -f csv -i ../patterns/definitions.owl --query ../sparql/zp_label_terms.sparql tmp_$@
	cat tmp_$@ | sort | uniq > $@ && rm tmp_$@
	
#############################################
### ZFIN pipeline steps            ##########
#############################################
# Completion of steps is marked by stamps, since some scripts are written in
# a way that is not possible to track with `make`. (e.g. in-place mutations,
# multiple outputs).

ZFIN_STAMPS=$(TMPDIR_CURATION)/stamps

$(ZFIN_STAMPS):
	mkdir -p $@

$(ZFIN_STAMPS)/id_map_updated: $(ZFIN_FISH_DATA) $(RESERVED_IRI) ../scripts/zp_update_id_map.py ../scripts/zp_lib.py | $(ZFIN_STAMPS)
	@echo "######################################"
	@echo "Updating the ZP to ZFIN EQ mappings..."
	cd ../curation && python3 ../scripts/zp_update_id_map.py id_map_zfin.tsv deprecated_id_map.tsv $(TMPDIR_CURATION)/reserved_iris.txt 100000 $(ZFIN_FISH_DATA)
	touch $@

$(ZFIN_STAMPS)/obsoletion_candidates: $(ZFIN_STAMPS)/id_map_updated zp_labels.csv ../templates/obsolete.tsv ../scripts/zfin_obsoletion.py | $(ZFIN_STAMPS)
	@echo "######################################"
	@echo "Determining Obsoletion candidates..."
	cd ../curation && python3 ../scripts/zfin_obsoletion.py deprecated_id_map.tsv ../templates/obsolete.tsv ../templates/df_obsolete_candidates.txt ../ontology/zp_labels.csv
	touch $@

$(ZFIN_STAMPS)/zfin_patterns: $(ZFIN_STAMPS)/id_map_updated $(ZFIN_STAMPS)/obsoletion_candidates ../scripts/zp_dosdp.py | $(ZFIN_STAMPS)
	@echo "######################################"
	@echo "Determining basic ZFIN patterns..."
	mkdir -p $(ZFINPATTERNDIR)
	rm -rf $(ZFINPATTERNDIR)/*
	cd ../curation && python3 ../scripts/zp_dosdp.py id_map_zfin.tsv ../patterns/data/zfin ../templates/obsolete.tsv pattern_assignments.txt ../ontology/zp_labels.csv
	touch $@

$(ZFIN_STAMPS)/upheno_aligned: $(ZFIN_STAMPS)/zfin_patterns ../scripts/zp_extract_upheno.py | $(ZFIN_STAMPS)
	@echo "######################################"
	@echo "Assigning to uPheno patterns..."
	for i in $(ZFINPATTERNDIR)/*.tsv; do \
		python3 ../scripts/zp_extract_upheno.py "$$i" || exit 1; \
	done
	touch $@

../curation/zp_zfin_phenotype_fish.tsv: $(ZFIN_STAMPS)/id_map_updated $(ZFIN_FISH_DATA) ../scripts/zp_fish_data.py
	@echo "######################################"
	@echo "Associating the ZFIN fish annotations with ZP ids..."
	cd ../curation && python3 ../scripts/zp_fish_data.py id_map_zfin.tsv zp_zfin_phenotype_fish.tsv $(ZFIN_FISH_DATA)

../curation/kb_zp.ttl: $(ZFIN_STAMPS)/id_map_updated $(ZFIN_GENE_DATA) ../scripts/zp_kb.py
	@echo "######################################"
	@echo "Associating the ZFIN gene annotations with ZP ids and exporting as RDF..."
	cd ../curation && python3 ../scripts/zp_kb.py id_map_zfin.tsv zp_zfin_phenoGeneCleanData_fish.tsv kb_zp.ttl $(ZFIN_GENE_DATA)

ZFIN_PIPELINE_PRODUCTS := $(ZFIN_STAMPS)/upheno_aligned \
			  ../curation/zp_zfin_phenotype_fish.tsv \
			  ../curation/kb_zp.ttl

.PHONY: zfin_pipeline
zfin_pipeline:
	$(MAKE) clean
	$(MAKE) update_patterns
	$(MAKE) $(ZFIN_PIPELINE_PRODUCTS)

#zp_pipeline: anatomy_pipeline missing_iris pattern_labels templates prepare_release
# This should only ever be run on a local machin
.PHONY: zp_pipeline_prepare_data
zp_pipeline_prepare_data:
	$(MAKE) zfin_pipeline
	$(MAKE) anatomy_pipeline
	$(MAKE) missing_iris
	$(MAKE) pattern_labels

#zp_pipeline_prepare_ontology: templates patterns preprocess

#############################################
### TEST PIPELINE                 ##########
#############################################

$(TMPDIR_CURATION)/new_labels.txt: | $(TMPDIR_CURATION)
	robot query -f csv -i ../../zp.owl --query ../sparql/zp_label_terms.sparql $@

$(TMPDIR_CURATION)/old_labels.txt: | $(TMPDIR_CURATION)
	robot query -f csv -I $(OBOPURL)zp.owl --query ../sparql/zp_label_terms.sparql $@

mass_obsolete: $(TMPDIR_CURATION)/old_labels.txt $(TMPDIR_CURATION)/new_labels.txt
	python3 ../scripts/mass_obsolete.py $(TMPDIR_CURATION)/old_labels.txt $(TMPDIR_CURATION)/new_labels.txt ../templates/obsolete.tsv

qc:
	$(ROBOT) report -i ../../zp.owl --fail-on None --print 5 -o zp_owl_report.owl
	$(ROBOT) merge --input ../../zp.owl reason --reasoner ELK  --equivalent-classes-allowed asserted-only --exclude-tautologies structural --output test.owl && rm test.owl && echo "Success"

#############################################
### ZP ZAPP                 #################
#############################################

$(TMPDIR)/zp-zapp-manual.owl: zapp/zp-zapp-manual.tsv | $(TMPDIR)
	$(ROBOT) template --template $< --output $@

$(TMPDIR)/zp-zapp.csv: zp.owl ../sparql/zp_zapp_terms.sparql | $(TMPDIR)
	$(ROBOT) query -f csv -i $< --use-graphs true --query ../sparql/zp_zapp_terms.sparql $@

ANNOTATION_PROPERTIES_ZAPP = rdfs:label IAO:0000115 OMO:0002000 oboInOwl:hasDbXref oboInOwl:hasExactSynonym oboInOwl:hasRelatedSynonym oboInOwl:hasBroadSynonym oboInOwl:hasNarrowSynonym

zp-zapp.owl: zp.owl $(TMPDIR)/zp-zapp.csv $(TMPDIR)/zp-zapp-manual.owl $(TMPDIR)/definitions-matches.owl
	$(ROBOT) merge -i zp.owl \
		remove -T $(TMPDIR)/zp-zapp.csv --select complement \
		remove $(foreach p, $(ANNOTATION_PROPERTIES_ZAPP), --term $(p)) \
			--term-file $(TMPDIR)/zp-zapp.csv \
			--select complement \
		remove --term rdfs:label --select "ZP:*" \
		merge -i $(TMPDIR)/zp-zapp-manual.owl \
		merge -i $(TMPDIR)/definitions-matches.owl \
		$(SHARED_ROBOT_COMMANDS) \
		annotate --link-annotation http://purl.org/dc/elements/1.1/type http://purl.obolibrary.org/obo/IAO_8000001 \
			--ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
			--output $@.tmp.owl && mv $@.tmp.owl $@
