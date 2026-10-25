#!/usr/bin/env python3
"""Export pending human claim judgments or score completed, digest-matching reviews."""

import argparse
from hashlib import sha256
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from versionlens.answer_review import make_answer_review_template, validate_and_score_answer_review
from versionlens.review import _read
from versionlens.models import ValidationError


def export_answers(report_path,output_dir):
    report,digest=_read(report_path)
    template=make_answer_review_template(report,digest)
    output_dir=Path(output_dir)
    if output_dir.exists():raise ValidationError('Choose a new answer-review directory; existing work is preserved.')
    lines=['# Pending human answer review','',
           '**No claim has been approved or judged semantically supported.**','',
           f'Evaluation report SHA-256: `{digest}`','',
           'Check support for each entire claim against its quoted source and surrounding',
           'versioned document. Separately judge factual/release correctness. A real quote',
           'alone does not establish either. Mark unsupported or incorrect claims honestly;',
           'completing a review is not endorsing the generated answer.','',
           'The unsupported-answer denominator contains answered case/method trials only.',
           'Abstentions and errors are reported separately, not counted as correct answers.',
           'These outputs are development observations and remain development after review.',
           'Use review-template.json as a copy, preserve digests, and fill completed status,',
           'reviewer_type human, reviewer, timezone-aware timestamp and claim booleans.','']
    for row in report['results']:
        answer=row.get('answer')
        if not answer or answer.get('status')!='answered':continue
        lines += [f'## {row["case_id"]} · {row["method"]}', '',
                  f'HTTPX `{row["version"]}` · Profile `{row["access_profile"]}`',
                  '**Question:** '+row['question'],'']
        for index,claim in enumerate(answer['claims']):
            lines += [f'### Claim {index}', '',claim['text'],'',
                      'Supported by the supplied evidence: pending. Factual/release correctness: pending.','']
            for citation in claim['citations']:
                lines += [f'Source `{citation["source_id"]}` · SHA-256 `{citation["source_sha256"]}`',
                          f'Version `{citation["version"]}` · {citation["section"]} · lines {citation["start_line"]}–{citation["end_line"]}',
                          'Reference: '+citation['citation_url'],'',
                          *[('> '+line).rstrip() for line in citation['quote'].splitlines()],'']
    output_dir.mkdir(parents=True)
    (output_dir/'ANSWERS.md').write_text('\n'.join(lines).rstrip()+'\n')
    (output_dir/'review-template.json').write_text(json.dumps(template,indent=2,ensure_ascii=False)+'\n')
    return {'report_sha256':digest,'pending_answer_trials':len(template['records']),
            'pending_claims':sum(len(row['claims']) for row in template['records']),
            'human_review_completed':False,'unsupported_answer_rate':None}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--report',type=Path,required=True)
    sub=parser.add_subparsers(dest='command',required=True)
    export=sub.add_parser('export');export.add_argument('--output-dir',type=Path,required=True)
    score=sub.add_parser('score');score.add_argument('--reviews',type=Path,required=True);score.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    try:
        if args.command=='export':result=export_answers(args.report,args.output_dir)
        else:
            if args.output.exists():raise ValidationError('Score output exists; preserve earlier results.')
            result=validate_and_score_answer_review(args.report,args.reviews)
            args.output.parent.mkdir(parents=True,exist_ok=True)
            with args.output.open('x') as output:json.dump(result,output,indent=2);output.write('\n')
    except (OSError,ValueError) as error:print(str(error),file=sys.stderr);return 2
    print(json.dumps(result,indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
