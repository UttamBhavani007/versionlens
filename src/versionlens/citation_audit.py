"""Independent mechanical citation checks; never a semantic entailment judge."""

import re

from .answering import quote_spans
from .models import SearchRequest
from .retrieval import SearchHit


def audit_answer(result: dict, request: SearchRequest, chunks: tuple) -> dict:
    """Check returned provenance/quotes against canonical indexed source records."""
    canonical = {chunk.chunk_id: chunk for chunk in chunks}
    problems = []
    rows = []
    status = result.get('status')
    claims = result.get('claims')
    if status not in {'answered', 'abstained', 'error'} or not isinstance(claims, list):
        return {'output_contract_valid': False, 'output_problems': ['invalid_status_or_claims'],
                'citation_count': 0, 'mechanically_valid_citations': 0, 'citations': [],
                'semantic_support_verified': False, 'unsupported_answer': None}
    if status != 'answered' and (claims or result.get('answer') is not None):
        problems.append('withheld_output_contains_partial_answer')
    if status == 'answered' and (not claims or result.get('model_called') is not True
                                 or result.get('citation_identity_and_quotes_checked') is not True):
        problems.append('answered_output_contract_violation')
    if result.get('semantic_support_verified') is not False:
        problems.append('unsupported_semantic_verification_flag')
    if status == 'answered' and (not isinstance(result.get('answer'), str) or not result['answer'].strip()):
        problems.append('missing_answer_text')
    evidence_ids = result.get('evidence_ids')
    if not isinstance(evidence_ids, list):
        evidence_ids = []
        problems.append('invalid_evidence_ids')
    for claim_index, claim in enumerate(claims):
        if not isinstance(claim, dict) or not isinstance(claim.get('text'), str) or not claim['text'].strip():
            problems.append('invalid_claim')
            continue
        citations = claim.get('citations')
        if not isinstance(citations, list) or not citations:
            problems.append('claim_without_citations')
            continue
        for citation_index, citation in enumerate(citations):
            failures = []
            if not isinstance(citation, dict):
                failures.append('citation_not_object')
            else:
                chunk_id = citation.get('chunk_id')
                chunk = canonical.get(chunk_id) if isinstance(chunk_id, str) else None
                if chunk is None:
                    failures.append('unknown_chunk')
                else:
                    if chunk.source.version != request.version:
                        failures.append('wrong_version')
                    if not request.allows(chunk.source):
                        failures.append('access_violation')
                    expected = SearchHit(chunk, 0).to_dict()
                    if any(citation.get(key) != value for key, value in expected.items() if key != 'score'):
                        failures.append('provenance_mismatch')
                    quote = citation.get('quote')
                    quote_id = citation.get('quote_id')
                    spans = quote_spans(chunk.text)
                    if not isinstance(quote_id, str) or not re.fullmatch(r'Q(?:[1-9]|1[0-2])', quote_id):
                        failures.append('invalid_quote_id')
                    else:
                        index = int(quote_id[1:]) - 1
                        if index >= len(spans) or not isinstance(quote, str) or quote != spans[index]:
                            failures.append('quote_not_exact_menu_span')
                evidence_id = citation.get('evidence_id')
                if not isinstance(evidence_id, str) or not re.fullmatch(r'E[1-4]', evidence_id) or evidence_id not in evidence_ids:
                    failures.append('unknown_evidence_id')
            rows.append({'claim_index': claim_index, 'citation_index': citation_index,
                         'mechanically_valid': not failures, 'failures': failures})
    return {'output_contract_valid': not problems, 'output_problems': problems,
            'citation_count': len(rows), 'mechanically_valid_citations': sum(row['mechanically_valid'] for row in rows),
            'citations': rows, 'semantic_support_verified': False, 'unsupported_answer': None}
