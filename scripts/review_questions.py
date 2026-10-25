#!/usr/bin/env python3
"""Export draft questions for people; freeze only completed human-attested reviews."""

import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from versionlens.evaluation_corpus import load_evaluation_corpus
from versionlens.review import load_candidates, make_review_template, freeze_holdout
from versionlens.models import ValidationError


def export_review(dataset_path, output_dir):
    corpus=load_evaluation_corpus(ROOT)
    data=load_candidates(dataset_path,corpus.chunks)
    digest=sha256(dataset_path.read_bytes()).hexdigest()
    output_dir=Path(output_dir)
    if output_dir.exists():
        raise ValidationError('Choose a new review directory; existing work is preserved.')
    lines=['# Draft question review pack','',
           '**All labels are AI-authored drafts. No question is approved or human-reviewed.**','',
           f'Dataset SHA-256: `{digest}`',f'Corpus fingerprint: `{data["corpus_fingerprint"]}`','',
           'Development and candidate holdout are split by topic group. Previously used',
           'intents remain in development. Reading source anchors is not a retrieval or',
           'generation trial. Candidate-holdout questions must remain unrun until review.','',
           'For every question, check version, profile, answerability, exact source context,',
           'reference answer and the abstention/conflict rubric. Approve only after checking',
           'the original source. Reject or request changes when uncertain. Source excerpts',
           'below are nonexhaustive anchors, not complete relevance judgments.','',
           'Copy `review-template.json` to your own review file. Fill status, reviewer_type',
           '(human), reviewer, timezone-aware reviewed_at and notes. Preserve case digests.',
           'All 60 candidate-holdout records need approval before a lock can be released.',
           'The tool checks attestations and content digests; it cannot verify identity.',
           'Claim entailment/unsupported answers need a separate later review of outputs.','',
           'Upstream excerpts retain the HTTPX BSD attribution in THIRD_PARTY_NOTICES.md;',
           'synthetic material is fictional MIT-licensed project data.','']
    for case in data['cases']:
        lines += [f'## {case["case_id"]} — {case["split"]}', '',
                  f'Group: `{case["group_id"]}` · HTTPX `{case["version"]}` · Profile: `{case["access_profile"]}`',
                  f'Category: `{case["category"]}` · Draft decision: **{case["expected_decision"]}**','',
                  '**Question:** '+case['question'],'','**Draft reference/rubric:** '+case['reference_answer'],'',
                  '**Review notes:** '+case['review_notes'],'',
                  'Prior development overlap: '+(', '.join(case['prior_development_overlap']) or 'None declared; verify this during review.'),'']
        for anchor in case['anchors']:
            matched=[chunk for chunk in corpus.chunks if chunk.source.source_id==anchor['source_id']
                     and chunk.source.sha256==anchor['source_sha256'] and anchor['section_contains'] in chunk.section
                     and anchor['text_contains'] in chunk.text]
            chunk=matched[0]
            lines += [f'**Source:** `{anchor["source_id"]}` · SHA-256 `{anchor["source_sha256"]}`',
                      f'Section: {chunk.section} · lines {chunk.start_line}–{chunk.end_line}',
                      f'Pinned reference: {chunk.citation_url}',
                      f'Local source file: [{chunk.source.path}]({os.path.relpath(ROOT/chunk.source.path,output_dir).replace(os.sep,chr(47))})',
                      '',*[('> '+line).rstrip() for line in chunk.text.splitlines()],'']
        if not case['anchors']:
            lines += ['No positive answer anchor is supplied. Check the stated absence,',
                      'snapshot or permission boundary; nearest neighbors are not proof of support.','']
    template=make_review_template(data,digest)
    output_dir.mkdir(parents=True)
    (output_dir/'QUESTIONS.md').write_text('\n'.join(lines).rstrip()+'\n')
    (output_dir/'review-template.json').write_text(json.dumps(template,indent=2)+'\n')
    return {'kind':'draft_review_export','dataset_sha256':digest,'corpus_fingerprint':data['corpus_fingerprint'],
            'questions':len(data['cases']),'split_counts':dict(Counter(case['split'] for case in data['cases'])),
            'category_counts':dict(Counter(case['category'] for case in data['cases'])),
            'approved_records':0,'human_review_completed':False,'candidate_holdout_executed':False}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dataset',type=Path,default=ROOT/'data/evaluation/review-candidates.json')
    sub=parser.add_subparsers(dest='command',required=True)
    export=sub.add_parser('export');export.add_argument('--output-dir',type=Path,default=ROOT/'reports/local/question-review')
    freeze=sub.add_parser('freeze');freeze.add_argument('--reviews',type=Path,required=True);freeze.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=='export':result=export_review(args.dataset,args.output_dir)
        else:result=freeze_holdout(args.dataset,args.reviews,load_evaluation_corpus(ROOT).chunks,args.output)
    except (OSError,ValueError) as error:
        print(str(error),file=sys.stderr);return 2
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
