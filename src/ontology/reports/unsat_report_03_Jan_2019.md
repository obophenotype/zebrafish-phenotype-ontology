# Compatibility analysis of corpus
## Analysing individual ontologies for Profile violations
### Ontology: http://www.semanticweb.org/matentzn/zp-debug.owl
* Profile Conformance
  * Undeclared Entities: 0
* Consistency analysis
  * Consistent:true
  * Unsatisfiable Classes: 73
    * protein kinase activity cardiac ventricle increased occurrence, abnormal
    * glutathione transferase activity whole organism process quality, abnormal
    * glutathione transferase activity whole organism decreased process quality, abnormal
    * mRNA (2'-O-methyladenosine-N6-)-methyltransferase activity muscle decreased occurrence, abnormal
    * lipoprotein lipase activity blood plasma increased process quality, abnormal
    * protein serine/threonine kinase activity intestine increased occurrence, abnormal
    * catechol oxidase activity melanocyte decreased process quality, abnormal
    * glutamate-ammonia ligase activity liver occurrence, abnormal
    * glutamate-ammonia ligase activity liver increased occurrence, abnormal
    * voltage-gated sodium channel activity Rohon-Beard neuron decreased process quality, abnormal
    * calcium channel activity neuromast hair cell increased occurrence, abnormal
    * lipoprotein lipase activity female organism increased process quality, abnormal
    * protein serine/threonine kinase activity kidney increased occurrence, abnormal
    * acetylcholinesterase activity brain increased occurrence, abnormal
    * superoxide dismutase activity brain decreased process quality, abnormal
    * glutathione peroxidase activity brain increased process quality, abnormal
    * alkaline phosphatase activity osteoblast increased process quality, abnormal
    * acetylcholinesterase activity brain process quality, abnormal
    * acetylcholinesterase activity brain increased process quality, abnormal
    * antioxidant activity brain increased process quality, abnormal
    * mRNA (2'-O-methyladenosine-N6-)-methyltransferase activity liver decreased occurrence, abnormal
    * mRNA (2'-O-methyladenosine-N6-)-methyltransferase activity brain decreased occurrence, abnormal
    * mRNA (2'-O-methyladenosine-N6-)-methyltransferase activity testis decreased occurrence, abnormal
    * mRNA (2'-O-methyladenosine-N6-)-methyltransferase activity ovary decreased occurrence, abnormal
    * GTPase activator activity integument increased process quality, abnormal
    * peroxidase activity neutrophil decreased process quality, abnormal
    * protein serine/threonine kinase activity brain increased occurrence, abnormal
    * protein serine/threonine kinase activity spinal cord increased occurrence, abnormal
    * protein serine/threonine kinase activity eye increased occurrence, abnormal
    * protein serine/threonine kinase activity liver increased occurrence, abnormal
    * heme oxygenase (decyclizing) activity whole organism decreased process quality, abnormal
    * NMDA glutamate receptor activity Mauthner neuron decreased duration, abnormal
    * chitin synthase activity intestine lumen decreased occurrence, abnormal
    * nitric-oxide synthase activity leukocyte increased process quality, abnormal
    * cysteine-type endopeptidase activity retinal ganglion cell decreased occurrence, abnormal
    * phosphodiesterase I activity whole organism decreased occurrence, abnormal
    * adenosine deaminase activity brain decreased occurrence, abnormal
    * NADH dehydrogenase (ubiquinone) activity whole organism decreased occurrence, abnormal
    * olfactory receptor activity microvillous olfactory receptor neuron decreased process quality, abnormal
    * AMPA glutamate receptor activity Mauthner neuron process quality, abnormal
    * cAMP-dependent protein kinase activity whole organism increased occurrence, abnormal
    * olfactory receptor activity olfactory bulb decreased process quality, abnormal
    * NMDA glutamate receptor activity Mauthner neuron decreased process quality, abnormal
    * calcium channel activity neuromast hair cell increased process quality, abnormal
    * catalase activity brain decreased process quality, abnormal
    * catalase activity brain increased process quality, abnormal
    * glutathione transferase activity brain decreased process quality, abnormal
    * peroxidase activity brain increased occurrence, abnormal
    * glutathione transferase activity brain increased process quality, abnormal
    * cytochrome-c oxidase activity brain decreased process quality, abnormal
    * catechol oxidase activity eye process quality, abnormal
    * beta-galactosidase activity spinal cord increased process quality, abnormal
    * ubiquinol-cytochrome-c reductase activity brain decreased process quality, abnormal
    * peroxidase activity whole organism increased occurrence, abnormal
    * lipoprotein lipase activity female organism decreased process quality, abnormal
    * cysteine-type endopeptidase activity retinal ganglion cell occurrence, abnormal
    * laminin binding whole organism decreased occurrence, abnormal
    * acetylcholinesterase activity gut decreased process quality, abnormal
    * catechol oxidase activity melanocyte process quality, abnormal
    * AMP-activated protein kinase activity muscle increased occurrence, abnormal
    * pyruvate kinase activity muscle process quality, abnormal
    * lipase activity intestine decreased occurrence, abnormal
    * lipase activity gall bladder absent, abnormal
    * hexokinase activity muscle process quality, abnormal
    * catechol oxidase activity eye disrupted, abnormal
    * phosphoenolpyruvate carboxykinase activity liver process quality, abnormal
    * chitinase activity brain increased process quality, abnormal
    * alkaline phosphatase activity gut epithelium disrupted, abnormal
    * NADH dehydrogenase (ubiquinone) activity whole organism occurrence, abnormal
    * hexosaminidase activity brain increased process quality, abnormal
    * catechol oxidase activity melanocyte disrupted, abnormal
    * alkaline phosphatase activity dorsal aorta decreased occurrence, abnormal
    * lipase activity intestine decreased process quality, abnormal


## Analyse Incompatibilites of Union
* Unsatisfiable classes are marked with {}, Named anonymous classes are marked with [] and the class in questions is marked with ()
* The explanation class hierarchies only includes top level classes that have at least one child.
  * (Only those can be potentially relevant for debugging).

### Explanations

#### Explanations for unsatistifiable protein kinase activity cardiac ventricle increased occurrence, abnormal
* IRI: http://purl.obolibrary.org/obo/ZP_0100801
  * Explanation 1
    * Axioms that impose constraints that might affect satisfiability
      * 'end stage' SubPropertyOf: 'relation between structure and stage'
      * 'relation between structure and stage' Domain 'continuant'
      *  Transitive: 'part of'
      * 'occurrent' DisjointWith 'part of' some 'continuant'
    * Class Hierarchy of Explanation
        * X7 [∃ 'has modifier'.'abnormal']
        * occurrent
           * process
             * molecular_function
               * catalytic activity
                 * transferase activity
                   * transferase activity, transferring phosphorus-containing groups
                     * kinase activity
                       * protein kinase activity
                         * {X8 ['protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle')]}
        * continuant
        * abnormal
        * X0 [∃ 'part of'.'continuant']
        * increased occurrence
           * {X1 ['increased occurrence' ⊓ (∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))) ⊓ (∃ 'has modifier'.'abnormal')]}
        * Adult
    * Other unsatisfiable classes in explanation: 
      * {X8 ['protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle')]}
      * {X5 [∃ 'has_part'.('increased occurrence' ⊓ (∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))) ⊓ (∃ 'has modifier'.'abnormal'))]}
      * {(protein kinase activity cardiac ventricle increased occurrence, abnormal)}
      * {X3 [∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))]}
      * {X1 ['increased occurrence' ⊓ (∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))) ⊓ (∃ 'has modifier'.'abnormal')]}
  * Explanation 2
    * Axioms that impose constraints that might affect satisfiability
      * 'existence starts during or after' SubPropertyOf: 'relation between structure and stage'
      * 'occurrent' DisjointWith 'part of' some 'continuant'
      * 'relation between structure and stage' Domain 'continuant'
    * Class Hierarchy of Explanation
        * occurrent
           * process
             * molecular_function
               * catalytic activity
                 * catalytic activity, acting on a protein
                   * protein kinase activity
                     * {X7 ['protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle')]}
        * continuant
        * X6 [∃ 'has modifier'.'abnormal']
        * X0 [∃ 'part of'.'continuant']
        * abnormal
        * Pharyngula:High-pec
        * increased occurrence
           * {X1 ['increased occurrence' ⊓ (∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))) ⊓ (∃ 'has modifier'.'abnormal')]}
    * Other unsatisfiable classes in explanation: 
      * {X7 ['protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle')]}
      * {(protein kinase activity cardiac ventricle increased occurrence, abnormal)}
      * {X3 [∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))]}
      * {X4 [∃ 'has_part'.('increased occurrence' ⊓ (∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))) ⊓ (∃ 'has modifier'.'abnormal'))]}
      * {X1 ['increased occurrence' ⊓ (∃ 'inheres in'.('protein kinase activity' ⊓ (∃ 'part of'.'cardiac ventricle'))) ⊓ (∃ 'has modifier'.'abnormal')]}

#### Explanations for unsatistifiable glutathione transferase activity whole organism process quality, abnormal
* IRI: http://purl.obolibrary.org/obo/ZP_0103876
  * Explanation 1
    * Axioms that impose constraints that might affect satisfiability
      * 'occurrent' DisjointWith 'part of' some 'continuant'
      * 'end stage' SubPropertyOf: 'relation between structure and stage'
      * 'relation between structure and stage' Domain 'continuant'
    * Class Hierarchy of Explanation
        * occurrent
           * process
             * molecular_function
               * catalytic activity
                 * transferase activity
                   * transferase activity, transferring alkyl or aryl (other than methyl) groups
                     * glutathione transferase activity
                       * {X2 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}
        * continuant
        * process quality
           * {X5 ['process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}
        * X6 [∃ 'has modifier'.'abnormal']
        * X0 [∃ 'part of'.'continuant']
        * abnormal
        * Adult
    * Other unsatisfiable classes in explanation: 
      * {X7 [∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))]}
      * {X5 ['process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}
      * {(glutathione transferase activity whole organism process quality, abnormal)}
      * {X1 [∃ 'has_part'.('process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal'))]}
      * {X2 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}
  * Explanation 2
    * Axioms that impose constraints that might affect satisfiability
      * 'part of' o 'existence starts during or after' SubPropertyOf: 'existence starts during or after'
      * 'continuant' DisjointWith 'occurrent'
      * 'relation between structure and stage' Domain 'continuant'
      * 'existence starts during or after' SubPropertyOf: 'relation between structure and stage'
    * Class Hierarchy of Explanation
        * occurrent
           * process
             * molecular_function
               * catalytic activity
                 * transferase activity
                   * transferase activity, transferring alkyl or aryl (other than methyl) groups
                     * glutathione transferase activity
                       * {X1 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}
        * continuant
        * X5 [∃ 'has modifier'.'abnormal']
        * process quality
           * {X4 ['process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}
        * abnormal
        * Zygote:1-cell
    * Other unsatisfiable classes in explanation: 
      * {X6 [∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))]}
      * {(glutathione transferase activity whole organism process quality, abnormal)}
      * {X0 [∃ 'has_part'.('process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal'))]}
      * {X4 ['process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}
      * {X1 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}

#### Explanations for unsatistifiable glutathione transferase activity whole organism decreased process quality, abnormal
* IRI: http://purl.obolibrary.org/obo/ZP_0103875
  * Explanation 1
    * Axioms that impose constraints that might affect satisfiability
      * 'part of' o 'existence starts during or after' SubPropertyOf: 'existence starts during or after'
      * 'continuant' DisjointWith 'occurrent'
      * 'relation between structure and stage' Domain 'continuant'
      * 'existence starts during or after' SubPropertyOf: 'relation between structure and stage'
    * Class Hierarchy of Explanation
        * occurrent
           * process
             * molecular_function
               * catalytic activity
                 * transferase activity
                   * transferase activity, transferring alkyl or aryl (other than methyl) groups
                     * glutathione transferase activity
                       * {X1 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}
        * X5 [∃ 'has modifier'.'abnormal']
        * continuant
        * abnormal
        * Zygote:1-cell
        * decreased process quality
           * {X2 ['decreased process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}
    * Other unsatisfiable classes in explanation: 
      * {X6 [∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))]}
      * {(glutathione transferase activity whole organism decreased process quality, abnormal)}
      * {X0 [∃ 'has_part'.('decreased process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal'))]}
      * {X1 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}
      * {X2 ['decreased process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}
  * Explanation 2
    * Axioms that impose constraints that might affect satisfiability
      * 'part of' o 'existence starts during or after' SubPropertyOf: 'existence starts during or after'
      * 'continuant' DisjointWith 'occurrent'
      * 'relation between structure and stage' Domain 'continuant'
      * 'existence starts during or after' SubPropertyOf: 'relation between structure and stage'
    * Class Hierarchy of Explanation
        * occurrent
           * process
             * molecular_function
               * catalytic activity
                 * transferase activity
                   * transferase activity, transferring alkyl or aryl (other than methyl) groups
                     * glutathione transferase activity
                       * {X1 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}
        * continuant
        * X5 [∃ 'has modifier'.'abnormal']
        * abnormal
        * Zygote:1-cell
        * decreased process quality
           * {X2 ['decreased process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}
    * Other unsatisfiable classes in explanation: 
      * {X6 [∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))]}
      * {(glutathione transferase activity whole organism decreased process quality, abnormal)}
      * {X0 [∃ 'has_part'.('decreased process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal'))]}
      * {X1 ['glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism')]}
      * {X2 ['decreased process quality' ⊓ (∃ 'inheres in'.('glutathione transferase activity' ⊓ (∃ 'part of'.'whole organism'))) ⊓ (∃ 'has modifier'.'abnormal')]}

## Frequently used axioms across unsatisfiability explanations
* 'catalytic activity' SubClassOf 'molecular_function' (6)
* 'process' SubClassOf 'occurrent' (6)
* 'molecular_function' SubClassOf 'process' (6)
* 'relation between structure and stage' Domain 'continuant' (6)
* 'transferase activity' SubClassOf 'catalytic activity' (5)
* 'transferase activity, transferring alkyl or aryl (other than methyl) groups' SubClassOf 'transferase activity' (4)
* 'existence starts during or after' SubPropertyOf: 'relation between structure and stage' (4)
* 'glutathione transferase activity' SubClassOf 'transferase activity, transferring alkyl or aryl (other than methyl) groups' (4)
* 'occurrent' DisjointWith 'part of' some 'continuant' (3)
* 'continuant' DisjointWith 'occurrent' (3)
* 'part of' o 'existence starts during or after' SubPropertyOf: 'existence starts during or after' (3)
* 'end stage' SubPropertyOf: 'relation between structure and stage' (2)
* 'protein kinase activity cardiac ventricle increased occurrence, abnormal' EquivalentTo 'has_part' some 
('increased occurrence' and ('inheres in' some 
('protein kinase activity' and ('part of' some 'cardiac ventricle'))) and ('has modifier' some 'abnormal')) (2)
* 'glutathione transferase activity whole organism decreased process quality, abnormal' EquivalentTo 'has_part' some 
('decreased process quality' and ('inheres in' some 
('glutathione transferase activity' and ('part of' some 'whole organism'))) and ('has modifier' some 'abnormal')) (2)
* 'glutathione transferase activity whole organism process quality, abnormal' EquivalentTo 'has_part' some 
('process quality' and ('inheres in' some 
('glutathione transferase activity' and ('part of' some 'whole organism'))) and ('has modifier' some 'abnormal')) (2)
* 'whole organism' SubClassOf 'existence starts during or after' some 'Zygote:1-cell' (2)
* 'whole organism' SubClassOf 'anatomical structure' (1)
* 'cardiac ventricle' SubClassOf 'existence starts during or after' some 'Pharyngula:High-pec' (1)
*  Transitive: 'part of' (1)
* 'anatomical structure' SubClassOf 'existence starts during or after' some 'Zygote:1-cell' (1)
* 'kinase activity' SubClassOf 'transferase activity, transferring phosphorus-containing groups' (1)
* 'whole organism' SubClassOf 'end stage' some 'Adult' (1)
* 'transferase activity, transferring phosphorus-containing groups' SubClassOf 'transferase activity' (1)
* 'heart' SubClassOf 'end stage' some 'Adult' (1)
* 'protein kinase activity' SubClassOf 'catalytic activity, acting on a protein' (1)
* 'catalytic activity, acting on a protein' SubClassOf 'catalytic activity' (1)
* 'cardiac ventricle' SubClassOf 'part of' some 'heart' (1)
* 'protein kinase activity' SubClassOf 'kinase activity' (1)
 