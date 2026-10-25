#!/usr/bin/env python3
"""Prepare an isolated corpus and record local development/reviewed-holdout trials."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sqlite3
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from versionlens.benchmark import run_evaluation
from versionlens.evaluation_corpus import load_evaluation_corpus
from versionlens.local_model import LocalModelError
from versionlens.models import ValidationError
from versionlens.review import load_candidates, validate_holdout_lock
from versionlens.store import replace_corpus
from versionlens.vector_store import build_vector_index


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--index',type=Path,default=ROOT/'data/versionlens-evaluation.sqlite3')
    parser.add_argument('--vector-index',type=Path,default=ROOT/'data/versionlens-evaluation-vectors.sqlite3')
    parser.add_argument('--dataset',type=Path,default=ROOT/'data/evaluation/review-candidates.json')
    sub=parser.add_subparsers(dest='command',required=True)
    prepare=sub.add_parser('prepare');prepare.add_argument('--keyword-only',action='store_true')
    run=sub.add_parser('run');run.add_argument('--split',choices=('development','holdout'),default='development')
    run.add_argument('--methods',nargs='+',choices=('keyword','vector','hybrid'),default=['keyword','vector','hybrid'])
    run.add_argument('--generate',action='store_true');run.add_argument('--reviews',type=Path);run.add_argument('--lock',type=Path)
    run.add_argument('--output',type=Path,default=ROOT/'reports/local/support-development.json')
    args=parser.parse_args()
    try:
        corpus=load_evaluation_corpus(ROOT)
        load_candidates(args.dataset,corpus.chunks)
        if args.command=='prepare':
            if args.index.resolve()==(ROOT/'data/versionlens.sqlite3').resolve() or args.vector_index.resolve()==(ROOT/'data/versionlens-vectors.sqlite3').resolve():
                raise ValidationError('Use separate evaluation indexes; the application indexes are preserved.')
            result={'source_index':replace_corpus(args.index,corpus)}
            if not args.keyword_only:result['vectors']=build_vector_index(args.index,args.vector_index)
            print(json.dumps(result,indent=2));return 0
        if args.output.exists():raise ValidationError('Report already exists; choose a new output path.')
        if args.split=='holdout':
            if args.reviews is None or args.lock is None:
                raise ValidationError('Holdout execution needs completed human review and its matching lock.')
            validate_holdout_lock(args.lock,args.dataset,args.reviews,corpus.chunks)
        report=run_evaluation(args.index,args.vector_index,args.dataset,split=args.split,methods=tuple(args.methods),
                              generate=args.generate,lock_path=args.lock,review_path=args.reviews)
        report['implementation_sha256']={str(path.relative_to(ROOT)):sha256(path.read_bytes()).hexdigest()
                                          for path in sorted((ROOT/'src/versionlens').glob('*.py'))}
        report['runner_sha256']=sha256(Path(__file__).read_bytes()).hexdigest()
        args.output.parent.mkdir(parents=True,exist_ok=True)
        with args.output.open('x') as output:
            json.dump(report,output,indent=2,allow_nan=False,ensure_ascii=False);output.write('\n')
        print(json.dumps({'report':str(args.output),'cases_executed':report['cases_executed'],'summary':report['summary']},indent=2))
    except (OSError,ValueError,sqlite3.Error,LocalModelError) as error:
        print(f'Evaluation failed: {error}',file=sys.stderr);return 2
    return 0


if __name__=='__main__':raise SystemExit(main())
