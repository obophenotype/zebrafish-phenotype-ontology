#!/usr/bin/env python3
"""Pin the ZFIN data files that supply the ZP pipeline.

ZFIN publishes a daily archive of its download files at
https://zfin.org/downloads/archive/<YYYY.MM.DD>/<file>, going back to 2012.
This script records a small lockfile tracking which ZFIN archive day was used
to run the pipeline. Any later build can fetch stable copies of those files and
verify their contents against a checksum.
"""

import hashlib
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

import click
import requests
import yaml
from bs4 import BeautifulSoup

ARCHIVE_INDEX = "https://zfin.org/downloads/archive/"
ARCHIVE_FILE = "https://zfin.org/downloads/archive/{date}/{name}"
FILES = ["phenotype_fish.txt", "phenoGeneCleanData_fish.txt"]
DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")
TIMEOUT = 600

LOCKFILE_HEADER = """\
# ZFIN archive day from which the ZP ids in id_map_zfin.tsv were minted.
# Written by src/scripts/zfin_snapshot.py refresh; do not edit by hand.
"""


@dataclass
class PinnedFile:
    """One ZFIN file: where it was fetched from and what its bytes hash to."""

    url: str
    md5: str


@dataclass
class Lockfile:
    """Pins the ZFIN archive day the pipeline uses, with the files it fetched."""

    date: str
    files: dict[str, PinnedFile] = field(default_factory=dict)

    def __post_init__(self):
        if not DATE_RE.match(str(self.date)):
            raise click.ClickException(f"invalid date in lockfile: {self.date!r}")
        self.files = {
            name: f if isinstance(f, PinnedFile) else PinnedFile(**f)
            for name, f in self.files.items()
        }

    @classmethod
    def from_file(cls, path: Path) -> "Lockfile":
        try:
            return cls(**yaml.safe_load(path.read_text()))
        except (TypeError, yaml.YAMLError) as e:
            raise click.ClickException(f"{path}: cannot parse lockfile: {e}")

    def to_file(self, path: Path) -> None:
        body = yaml.safe_dump(asdict(self), sort_keys=False)
        path.write_text(LOCKFILE_HEADER + body)


def newest_archive_date() -> str:
    """Return the newest date listed on the archive index, e.g. '2026.10.01'."""
    resp = requests.get(ARCHIVE_INDEX, timeout=TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "lxml")
    dates = [
        opt["value"]
        for opt in soup.find_all("option")
        if DATE_RE.match(opt.get("value", ""))
    ]
    if not dates:
        raise click.ClickException(f"no archive dates found at {ARCHIVE_INDEX}")
    return max(dates)


def download(url: str, dest: Path) -> None:
    tmp = dest.with_suffix(dest.suffix + ".tmp")
    with requests.get(url, stream=True, timeout=TIMEOUT) as resp:
        resp.raise_for_status()
        with open(tmp, "wb") as f:
            for chunk in resp.iter_content(chunk_size=1 << 20):
                f.write(chunk)
    tmp.replace(dest)


def md5sum(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


@click.group(help=__doc__)
def cli():
    pass


def validate_date(ctx, param, value):
    if value is not None and not DATE_RE.match(value):
        raise click.BadParameter("expected YYYY.MM.DD, e.g. 2026.09.24")
    return value


@cli.command()
@click.argument("lockfile", type=click.Path(path_type=Path))
@click.argument("snapshot_dir", type=click.Path(file_okay=False, path_type=Path))
@click.option(
    "--date",
    callback=validate_date,
    metavar="YYYY.MM.DD",
    help="Archive day to pin instead of the newest one.",
)
def refresh(lockfile: Path, snapshot_dir: Path, date: str | None):
    """Download a ZFIN archive day into <snapshot_dir> and write <lockfile>.

    Uses the newest archive day unless --date is given. This is the only
    command that writes the lockfile. Run it at the top of a ZFIN update.
    Everything downstream will then pin to the same version.
    """
    if date is None:
        date = newest_archive_date()
        click.echo(f"newest ZFIN archive day: {date}")
    else:
        click.echo(f"pinning ZFIN archive day: {date}")
    if lockfile.exists():
        current = Lockfile.from_file(lockfile).date
        if date < current:
            raise click.ClickException(
                f"{lockfile} pins {current}; refusing to go back to {date}. "
                "Rebuilding against an older version of ZFIN will cause the "
                "pipeline to act in unexpected ways.\n\n"
                "If you really want to use an older version, then delete the "
                "lockfile first, and run this command again."
            )
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    files = {}
    for name in FILES:
        url = ARCHIVE_FILE.format(date=date, name=name)
        dest = snapshot_dir / name
        click.echo(f"downloading {url} to {dest}")
        download(url, dest)
        files[name] = PinnedFile(url=url, md5=md5sum(dest))
    Lockfile(date=date, files=files).to_file(lockfile)
    click.echo(f"wrote {lockfile}")
    # The lockfile is now newer than the dumps it describes. Make would take
    # that as the dumps being stale and fetch them again; mark them newer.
    for name in FILES:
        (snapshot_dir / name).touch()


@cli.command()
@click.argument("lockfile", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("snapshot_dir", type=click.Path(file_okay=False, path_type=Path))
def fetch(lockfile: Path, snapshot_dir: Path):
    """Download the ZFIN data described in <lockfile> into <snapshot_dir>.

    Files already present in the directory are left alone, whatever their
    contents; use `verify` to check them. Does not touch the lockfile.
    """
    lock = Lockfile.from_file(lockfile)
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    for name, f in lock.files.items():
        dest = snapshot_dir / name
        if dest.exists():
            click.echo(f"present, skipping: {dest}")
            continue
        click.echo(f"downloading {f.url} to {dest}")
        download(f.url, dest)


@cli.command()
@click.argument("lockfile", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def date(lockfile: Path):
    """Print the ZFIN archive day pinned by <lockfile>."""
    click.echo(Lockfile.from_file(lockfile).date)


@cli.command()
@click.argument("lockfile", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def files(lockfile: Path):
    """Print the archive URL of each file pinned by <lockfile>, one per line.

    These are the exact files the pipeline was built from. They are published
    as dcterms:source annotations on the released ontologies.
    """
    lock = Lockfile.from_file(lockfile)
    for f in lock.files.values():
        click.echo(f.url)


@cli.command()
@click.argument("lockfile", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.argument("snapshot_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def verify(lockfile: Path, snapshot_dir: Path):
    """Check the files in <snapshot_dir> against the checksums in <lockfile>.

    Exits 1 if any file is missing or differs. Does not connect to the network.
    """
    lock = Lockfile.from_file(lockfile)
    failed = False
    for name in FILES:
        path = snapshot_dir / name
        f = lock.files.get(name)
        if f is None:
            click.echo(f"UNPINNED {name}: no entry in {lockfile}", err=True)
            failed = True
            continue
        if not path.exists():
            click.echo(f"MISSING  {path}", err=True)
            failed = True
            continue
        actual = md5sum(path)
        if actual != f.md5:
            click.echo(f"MISMATCH {path}: expected {f.md5}, got {actual}", err=True)
            failed = True
        else:
            click.echo(f"ok       {path} ({lock.date})")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    cli()
