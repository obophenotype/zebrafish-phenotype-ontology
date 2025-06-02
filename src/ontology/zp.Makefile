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
tmp/zp-edit-merged-reasoned.owl: $(SRC)
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
dosdp-matches-matches: tmp/zp-edit-merged-reasoned.owl
	$(DOSDPT) query --ontology=$< --catalog=$(CATALOG) --reasoner=elk --obo-prefixes=true --restrict-axioms-to=logical \
    --batch-patterns="$(ALL_PATTERN_NAMES_WO_LABELS_AND_ZFIN)" --template="$(PATTERNDIR)/dosdp-patterns" --outfile="$(PATTERNDIR)/data/matches/"

$(DOSDP_OWL_FILES_MATCHES): $(EDIT_PREPROCESSED) $(DOSDP_TSV_FILES_MATCHES) $(ALL_PATTERN_FILES)
	if [ "${DOSDP_TSV_FILES_MATCHES}" ]; then $(DOSDPT) generate --catalog=$(CATALOG) \
    --infile=$(PATTERNDIR)/data/matches --template=$(PATTERNDIR)/dosdp-patterns/ --batch-patterns="$(DOSDP_PATTERN_NAMES_MATCHES)" \
    --ontology=$< --obo-prefixes=true --restrict-axioms-to=annotation --add-axiom-source-annotation=true  --outfile=$(PATTERNDIR)/data/matches; fi

tmp/definitions-matches.owl: $(DOSDP_OWL_FILES_MATCHES)
	$(ROBOT) merge $(addprefix -i , $(DOSDP_OWL_FILES_MATCHES)) annotate --ontology-iri $(ONTBASE)/patterns/definitions-matches.owl --version-iri $(ONTBASE)/releases/$(TODAY)/patterns/definitions-matches.owl -o $@

tmp/definitions-matches-no-labels.owl: tmp/definitions-matches.owl
	$(ROBOT) remove -i $< --term rdfs:label --axioms annotation -o $@

../patterns/definitions.owl: $(DOSDP_OWL_FILES_DEFAULT) $(DOSDP_OWL_FILES_MANUAL) $(DOSDP_OWL_FILES_ZFIN)  $(DOSDP_OWL_FILES_ANATOMY)  $(DOSDP_OWL_FILES_PROCESS) tmp/definitions-matches-no-labels.owl
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

$(ZP_SRC_SEED): $(SRC)
	robot query -f csv -i $< --use-graphs true --query ../sparql/zp_terms.sparql $@


$(TMPDIR_CURATION)/id_map_terms.txt.tmp:
	grep -Eo '(ZP)[^[:space:]"]+' ../curation/id_map_zfin.tsv | sort | uniq > $@

$(TMPDIR_CURATION)/id_map_terms.txt.zp.tmp:
	grep -Eo '(ZP)[:][^[:space:]"]+' ../curation/id_map.tsv | sort | uniq > $@	
	
$(TMPDIR_CURATION)/id_map_terms.txt: $(TMPDIR_CURATION)/id_map_terms.txt.tmp $(TMPDIR_CURATION)/id_map_terms.txt.zp.tmp
	cat $^ | sort | uniq > $@


$(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

$(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.zp.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
$(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt: $(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.tmp $(TMPDIR_CURATION)/idmap_removed_ambiguous_terms.txt.zp.tmp
	cat $^ | sort | uniq > $@


$(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

$(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.zp.tmp: ../curation/id_map_zfin.tsv
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
$(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt: $(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.tmp $(TMPDIR_CURATION)/idmap_removed_incomplete_terms.txt.zp.tmp
	cat $^ | sort | uniq > $@


$(TMPDIR_CURATION)/obsoleted.txt.tmp: ../templates/obsolete.tsv
	grep -Eo '($(PURL))[^[:space:]"]+' $< | sort | uniq > $@

$(TMPDIR_CURATION)/obsoleted.txt.zp.tmp: ../templates/obsolete.tsv
	grep -Eo '(ZP)[:][^[:space:]"]+' $< | sort | uniq > $@	
	
$(TMPDIR_CURATION)/obsoleted.txt: $(TMPDIR_CURATION)/obsoleted.txt.tmp $(TMPDIR_CURATION)/obsoleted.txt.zp.tmp
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

$(ZFA):
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
### WHOLE PIPELINE (main job)      ##########
#############################################

.PHONY: .FORCE

$(ID_MAP): update_id_map

update_id_map: $(ID_MAP_ZFIN)
	python3 ../scripts/create_id_map.py ../patterns $(ID_MAP)

clean:
	mkdir -p $(TMPDIR_CURATION)
	rm -rf $(TMPDIR_CURATION)/*

pattern_labels:
	rm -rf $(LABELPATTERNDIR)/*.tsv
	python3 ../scripts/zp_create_label_patterns.py ../patterns

zp_labels.csv:
	robot query -f csv -i ../patterns/definitions.owl --query ../sparql/zp_label_terms.sparql tmp_$@
	cat tmp_$@ | sort | uniq > $@ && rm tmp_$@
	
zfin_pipeline: clean update_patterns $(RESERVED_IRI) zp_labels.csv
	sh ../scripts/zfin_pipeline.sh

#zp_pipeline: anatomy_pipeline missing_iris pattern_labels templates prepare_release
# This should only ever be run on a local machin
zp_pipeline_prepare_data: zfin_pipeline anatomy_pipeline missing_iris pattern_labels
	
#zp_pipeline_prepare_ontology: templates patterns preprocess

z:
	sh ../scripts/zfin_pipeline_test.sh

#############################################
### TEST PIPELINE                 ##########
#############################################

$(TMPDIR_CURATION)/new_labels.txt:
	robot query -f csv -i ../../zp.owl --query ../sparql/zp_label_terms.sparql $@

$(TMPDIR_CURATION)/old_labels.txt:
	robot query -f csv -I $(OBOPURL)zp.owl --query ../sparql/zp_label_terms.sparql $@

mass_obsolete: $(TMPDIR_CURATION)/old_labels.txt $(TMPDIR_CURATION)/new_labels.txt
	python3 ../scripts/mass_obsolete.py $(TMPDIR_CURATION)/old_labels.txt $(TMPDIR_CURATION)/new_labels.txt ../templates/obsolete.tsv

qc:
	$(ROBOT) report -i ../../zp.owl --fail-on None --print 5 -o zp_owl_report.owl
	$(ROBOT) merge --input ../../zp.owl reason --reasoner ELK  --equivalent-classes-allowed asserted-only --exclude-tautologies structural --output test.owl && rm test.owl && echo "Success"

#############################################
### ZP ZAPP                 #################
#############################################

tmp/zp-zapp-manual.owl: zapp/zp-zapp-manual.tsv
	$(ROBOT) template --template $< --output $@

tmp/zp-zapp.csv: zp.owl ../sparql/zp_zapp_terms.sparql
	$(ROBOT) query -f csv -i $< --use-graphs true --query ../sparql/zp_zapp_terms.sparql $@

ANNOTATION_PROPERTIES_ZAPP = rdfs:label IAO:0000115 OMO:0002000 oboInOwl:hasDbXref oboInOwl:hasExactSynonym oboInOwl:hasRelatedSynonym oboInOwl:hasBroadSynonym oboInOwl:hasNarrowSynonym

zp-zapp.owl: zp.owl tmp/zp-zapp.csv tmp/zp-zapp-manual.owl tmp/definitions-matches.owl
	$(ROBOT) merge -i zp.owl \
	  	remove -T tmp/zp-zapp.csv --select complement \
	  	remove $(foreach p, $(ANNOTATION_PROPERTIES_ZAPP), --term $(p)) \
		        --term-file tmp/zp-zapp.csv \
		        --select complement \
	  	remove --term rdfs:label --select "ZP:*" \
		merge -i tmp/zp-zapp-manual.owl \
		merge -i tmp/definitions-matches.owl \
		$(SHARED_ROBOT_COMMANDS) \
		annotate --link-annotation http://purl.org/dc/elements/1.1/type http://purl.obolibrary.org/obo/IAO_8000001 \
		--ontology-iri $(ONTBASE)/$@ $(ANNOTATE_ONTOLOGY_VERSION) \
		--output $@.tmp.owl && mv $@.tmp.owl $@
