#!/usr/bin/env python3
"""Build the ZFIN annotation tables that ZP publishes with each release.

ZFIN annotates fish (and, for single-gene cases, genes) with post-composed
EQ phenotypes. ZP assigns each distinct EQ a stable ZP id, recorded in
id_map_zfin.tsv. This joins a ZFIN download to that id map and writes a
flat table with one row per ZFIN annotation and its ZP id:

    fish   phenotype_fish.txt           every fish phenotype annotation
    genes  phenoGeneCleanData_fish.txt  every gene phenotype annotation

Every annotation is included, normal observations too: ZP's key ignores the
normal/abnormal tag, so a fish observed normal for "pectoral fin quality"
maps to the same ZP class as one observed abnormal. The phenotype_tag
column tells them apart.

Every EQ in the ZFIN file is expected to have a ZP id: the id map is minted
from the same ZFIN archive day the lockfile pins. An EQ without one means
the data and the id map are out of step, and the command fails.
"""

import csv
from pathlib import Path

import click
import curies

from zp_lib import (
    PHENOTYPE_FISH_EQ_COLUMNS,
    PHENOTYPE_FISH_TAG_COLUMN,
    PHENO_GENE_EQ_COLUMNS,
    PHENO_GENE_TAG_COLUMN,
    eq_components,
    eq_key,
)

ZP = curies.Converter.from_prefix_map({"ZP": "http://purl.obolibrary.org/obo/ZP_"})

# Columns copied into the tables, by output name. 1-based, as in zp_lib.
FISH_COLUMNS = {
    "fish_id": 1,
    "fish_name": 2,
    "phenotype_tag": PHENOTYPE_FISH_TAG_COLUMN,
    "start_stage_id": 3,
    "end_stage_id": 5,
    "environment_id": 23,
    "publication_id": 22,
}
GENE_COLUMNS = {
    "gene_id": 3,
    "gene_symbol": 2,
    "phenotype_tag": PHENO_GENE_TAG_COLUMN,
    "fish_id": 19,
    "fish_name": 20,
    "start_stage_id": 21,
    "end_stage_id": 22,
    "environment_id": 23,
    "publication_id": 24,
    "figure_id": 25,
}


def read_id_map(path: Path) -> dict[str, str]:
    """id_map_zfin.tsv: columns 'iri' (a ZP CURIE) and 'id' (the EQ key)."""
    with open(path, newline="") as f:
        return {row["id"]: row["iri"] for row in csv.DictReader(f, delimiter="\t")}


def read_labels(path: Path) -> dict[str, str]:
    """zp_labels.csv as written by ROBOT: 'term' (full IRI) and 'label'."""
    with open(path, newline="") as f:
        return {ZP.compress(row["term"], strict=True): row["label"] for row in csv.DictReader(f)}


def zfin_rows(path: Path):
    with open(path, newline="") as f:
        yield from csv.reader(f, delimiter="\t", quoting=csv.QUOTE_NONE)


def write_table(
    source: Path,
    out,
    eq_columns: tuple[int, ...],
    columns: dict[str, int],
    id_map: dict[str, str],
    labels: dict[str, str],
) -> None:
    """Join SOURCE to the id map and write the table to OUT (a text stream).

    Nothing is written until every row has mapped, so a failure never
    leaves a partial table on stdout or in a file.
    """
    rows = []
    unmapped = []
    unlabelled = set()
    for row in zfin_rows(source):
        eq = eq_key(eq_components(row, eq_columns))
        zp_id = id_map.get(eq)
        if zp_id is None:
            unmapped.append(eq)
            continue
        label = labels.get(zp_id, "")
        if not label:
            unlabelled.add(zp_id)
        rows.append([row[c - 1] for c in columns.values()] + [zp_id, label, eq])
    if unmapped:
        distinct = sorted(set(unmapped))
        raise click.ClickException(
            f"{len(unmapped)} rows in {source} ({len(distinct)} distinct EQs) have no "
            f"ZP id in the id map, e.g. {', '.join(distinct[:3])}. Is the ZFIN data "
            f"from the archive day the id map was minted from?"
        )
    w = csv.writer(out, delimiter="\t", lineterminator="\n")
    w.writerow(list(columns) + ["zp_id", "zp_label", "zfin_eq"])
    w.writerows(rows)
    click.echo(f"wrote {len(rows)} rows", err=True)
    if unlabelled:
        click.echo(f"warning: {len(unlabelled)} ZP ids have no label", err=True)


TABLES = {
    "fish": (PHENOTYPE_FISH_EQ_COLUMNS, FISH_COLUMNS),
    "genes": (PHENO_GENE_EQ_COLUMNS, GENE_COLUMNS),
}


@click.command(help=__doc__)
@click.argument("table", type=click.Choice(TABLES))
@click.argument("source", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option("--id-map", "id_map", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path), help="id_map_zfin.tsv")
@click.option("--labels", required=True, type=click.Path(exists=True, dir_okay=False, path_type=Path), help="zp_labels.csv")
@click.option("-o", "--output", type=click.File("w"), default="-", help="Write the table here instead of stdout.")
def cli(table: str, source: Path, id_map: Path, labels: Path, output):
    eq_columns, columns = TABLES[table]
    write_table(source, output, eq_columns, columns, read_id_map(id_map), read_labels(labels))


if __name__ == "__main__":
    cli()
