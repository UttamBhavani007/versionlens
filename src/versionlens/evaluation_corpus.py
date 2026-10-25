"""Isolated evaluation corpus; default application/demo manifests stay unchanged."""

from pathlib import Path
from .ingest import Corpus, load_corpus, load_demo_corpus
from .models import ValidationError


def load_evaluation_corpus(root: Path) -> Corpus:
    base = load_demo_corpus(root)
    conflicts = load_corpus(root, 'data/evaluation/conflict-sources.json', allow_synthetic=True)
    combined = Corpus(base.sources+conflicts.sources, base.chunks+conflicts.chunks)
    if len({source.source_id for source in combined.sources}) != len(combined.sources):
        raise ValidationError('Evaluation fixture source IDs overlap the base corpus.')
    return combined
