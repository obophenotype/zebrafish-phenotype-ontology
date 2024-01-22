# ZP Ontology Documentation

[//]: # "This file is meant to be edited by the ontology maintainer."

Welcome to the ZP documentation!

You can find descriptions of the standard ontology engineering workflows [here](odk-workflows/index.md).

The current release workflows is as follows (`DATE` is todays date):

```
cd src/ontology
git checkout -b release-DATE
sh zp_release.sh
```

Note that you should periodically review `zp_release.sh` to ensure the correct ODK version is used.

The release pipeline is currently quite work intensive. Prepare for a whole day of work.

During the first run, you will see a lot of classes being created which reference obsolete terms.

You will create issues, and then obsolete all these terms by copying the information from
`src/templates/df_obsolete_candidates.txt` to `src/templates/obsolete.tsv`. Then the pipeline has to be run again, until it does not break anymore. I recommend to commit all updated intermediate files after every run, even if they fail, so you can see in the next run what changes.

When the release was succesful, you create, manually, a GitHub release with the usual tag (`v2024-01-22`, dont forget the `v`). The you upload all release files (see previous release which they are). Hit publish.

To the next engineer seeing this:

We need to streamline some of the pipeline a bit more, perhaps auto-retiring ZP classes if any of its component terms are retired.
