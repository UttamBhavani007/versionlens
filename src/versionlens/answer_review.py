"""Digest-bound human claim judgments, separate from mechanical citation checks.

A valid review is a local human attestation, not identity authentication. This
module never fills in judgments or infers semantic correctness from quotations.
"""

from datetime import datetime, timedelta, timezone
from hashlib import sha256

from .models import ValidationError
from .review import _canonical, _digest, _fields, _read, _string
from .search_service import RETRIEVERS


REVIEW_FIELDS = {'schema_version', 'kind', 'report_sha256', 'records'}
RECORD_FIELDS = {'case_id', 'method', 'case_sha256', 'status', 'reviewer_type',
                 'reviewer', 'reviewed_at', 'notes', 'claims'}
CLAIM_FIELDS = {'claim_index', 'claim_sha256', 'status', 'supported', 'correct', 'notes'}


def _hash(value):
    return sha256(_canonical(value)).hexdigest()


def _answered_cases(report):
    if (not isinstance(report, dict) or type(report.get('schema_version')) is not int
            or report['schema_version'] != 1 or report.get('kind') != 'support_evaluation_observations'):
        raise ValidationError('Answer review requires a support-evaluation observations report.')
    # This also rejects nonfinite numbers and invalid Unicode elsewhere in the report.
    _canonical(report)
    rows = report.get('results')
    if not isinstance(rows, list) or len(rows) > 2000:
        raise ValidationError('Evaluation results must be a bounded list.')
    seen, answered = set(), {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValidationError('Evaluation result rows must be objects.')
        case_id = _string(row.get('case_id'), 'Case ID', limit=200)
        method = row.get('method')
        if not isinstance(method, str) or method not in RETRIEVERS:
            raise ValidationError('Evaluation result method is unsupported.')
        key = (case_id, method)
        if key in seen:
            raise ValidationError('Evaluation results repeat a case/method pair.')
        seen.add(key)
        if 'answer' not in row:
            raise ValidationError('Evaluation rows must explicitly record answer output or its absence.')
        answer = row['answer']
        if answer is None:
            continue
        if (not isinstance(answer, dict) or not isinstance(answer.get('status'), str)
                or answer['status'] not in {'answered', 'abstained', 'error'}):
            raise ValidationError('Evaluation answer has an invalid status.')
        claims = answer.get('claims')
        if not isinstance(claims, list) or len(claims) > 20:
            raise ValidationError('Evaluation claims must be a bounded list.')
        if answer['status'] != 'answered':
            if claims or answer.get('answer') is not None:
                raise ValidationError('Withheld output contains a partial answer; repair the report contract first.')
            continue
        if not claims:
            raise ValidationError('Answered cases must contain generated claims.')
        for claim in claims:
            if not isinstance(claim, dict):
                raise ValidationError('Generated claims must be objects.')
            _string(claim.get('text'), 'Generated claim', limit=20_000)
        answered[key] = row
    return answered


def make_answer_review_template(report: dict, report_sha256: str) -> dict:
    """Create pending judgments for every answered case/method and every claim."""
    _digest(report_sha256, 'Evaluation report digest')
    answered = _answered_cases(report)
    return {
        'schema_version': 1, 'kind': 'human_answer_review', 'report_sha256': report_sha256,
        'records': [
            {'case_id': case_id, 'method': method, 'case_sha256': _hash(row),
             'status': 'pending', 'reviewer_type': None, 'reviewer': None, 'reviewed_at': None,
             'notes': '', 'claims': [
                 {'claim_index': index, 'claim_sha256': _hash(claim), 'status': 'pending',
                  'supported': None, 'correct': None, 'notes': ''}
                 for index, claim in enumerate(row['answer']['claims'])]}
            for (case_id, method), row in answered.items()],
    }


def _attestation(record):
    if record['status'] != 'completed' or record['reviewer_type'] != 'human':
        raise ValidationError('Every answered case needs a completed explicit human review attestation.')
    _string(record['reviewer'], 'Human reviewer', limit=500)
    _string(record['reviewed_at'], 'Review timestamp', limit=100)
    try:
        timestamp = datetime.fromisoformat(record['reviewed_at'])
    except ValueError:
        raise ValidationError('Review timestamp must be timezone-aware ISO format.') from None
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        raise ValidationError('Review timestamp must include its timezone.')
    if timestamp > datetime.now(timezone.utc) + timedelta(minutes=1):
        raise ValidationError('Review timestamp cannot be in the future.')
    _string(record['notes'], 'Answer review notes', empty=True)


def _counts(records):
    claims = [claim for record in records for claim in record['claims']]
    unsupported_claims = sum(not claim['supported'] for claim in claims)
    incorrect_claims = sum(not claim['correct'] for claim in claims)
    unsupported_answers = sum(any(not claim['supported'] for claim in record['claims']) for record in records)
    all_correct_answers = sum(all(claim['correct'] for claim in record['claims']) for record in records)
    return {
        'reviewed_answer_count': len(records), 'reviewed_claim_count': len(claims),
        'supported_claim_count': len(claims) - unsupported_claims,
        'unsupported_claim_count': unsupported_claims,
        'unsupported_claim_rate': unsupported_claims/len(claims) if claims else None,
        'unsupported_answer_count': unsupported_answers,
        'unsupported_answer_rate': unsupported_answers/len(records) if records else None,
        'correct_claim_count': len(claims) - incorrect_claims, 'incorrect_claim_count': incorrect_claims,
        'claim_correctness_rate': (len(claims)-incorrect_claims)/len(claims) if claims else None,
        'all_claims_correct_answer_count': all_correct_answers,
        'all_claims_correct_answer_rate': all_correct_answers/len(records) if records else None,
        'semantic_citation_support_rate': None,
    }


def validate_and_score_answer_review(report_path, review_path) -> dict:
    """Score complete digest-matching judgments; pending/stale/partial reviews fail.

    `supported` concerns whether the supplied evidence supports the whole claim.
    `correct` is a separate factual/release-applicability judgment. Neither is
    inferred from the other. Citation-level entailment remains unmeasured.
    """
    report, report_sha = _read(report_path)
    review, review_sha = _read(review_path)
    answered = _answered_cases(report)
    _fields(review, REVIEW_FIELDS, 'Answer review')
    if (type(review['schema_version']) is not int or review['schema_version'] != 1
            or review['kind'] != 'human_answer_review' or review['report_sha256'] != report_sha):
        raise ValidationError('Answer review does not bind this exact evaluation report.')
    records = review['records']
    if not isinstance(records, list) or len(records) != len(answered):
        raise ValidationError('Answer review must cover every answered case/method exactly once.')
    seen = set()
    for record in records:
        _fields(record, RECORD_FIELDS, 'Answer review record')
        case_id = _string(record['case_id'], 'Case ID', limit=200)
        method = record['method']
        if not isinstance(method, str):
            raise ValidationError('Answer-review method must identify a generated trial.')
        key = (case_id, method)
        if key not in answered or key in seen:
            raise ValidationError('Answer review contains an unknown or duplicate case/method.')
        seen.add(key)
        row = answered[key]
        if record['case_sha256'] != _hash(row):
            raise ValidationError('Answer review case metadata is stale.')
        _attestation(record)
        judgments, claims = record['claims'], row['answer']['claims']
        if not isinstance(judgments, list) or len(judgments) != len(claims):
            raise ValidationError('Each answer review must cover all generated claims.')
        indexes = set()
        for judgment in judgments:
            _fields(judgment, CLAIM_FIELDS, 'Claim review')
            index = judgment['claim_index']
            if type(index) is not int or not 0 <= index < len(claims) or index in indexes:
                raise ValidationError('Claim judgments contain an unknown or duplicate claim index.')
            indexes.add(index)
            if judgment['claim_sha256'] != _hash(claims[index]):
                raise ValidationError('A generated claim or its citations changed after review.')
            if judgment['status'] != 'completed' or type(judgment['supported']) is not bool or type(judgment['correct']) is not bool:
                raise ValidationError('Each claim needs completed, explicit boolean support and correctness judgments.')
            _string(judgment['notes'], 'Claim review notes', empty=True)
    if _read(report_path)[1] != report_sha or _read(review_path)[1] != review_sha:
        raise ValidationError('Evaluation report or answer review changed during scoring.')
    return {
        'schema_version': 1, 'kind': 'human_answer_review_scores',
        'report_sha256': report_sha, 'review_sha256': review_sha,
        'answer_unit': 'case_id and retrieval method',
        'reviewed_unique_question_count': len({record['case_id'] for record in records}),
        'review_complete_for_answered_cases': True,
        'human_review_attestations_validated': bool(records),
        **_counts(records),
        'by_method': {method: _counts([record for record in records if record['method'] == method])
                      for method in sorted({record['method'] for record in records})},
        'limitations': [
            'Human reviewer metadata is an attestation, not identity authentication or agreement measurement.',
            'Unsupported-answer rate covers answered trials only; abstentions and operational errors are excluded.',
            'Claim support and factual/release correctness are separate judgments.',
            'Citation-level semantic support is unavailable without separate per-citation judgments.',
            'Reviewing development outputs does not turn them into held-out benchmark results.'],
    }
