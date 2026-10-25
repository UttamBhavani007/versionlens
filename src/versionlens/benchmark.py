"""Local development observations and review-gated held-out execution."""

from collections import Counter
from datetime import datetime, timezone
from hashlib import sha256
import json
import math
from pathlib import Path
from statistics import median
import sqlite3
from time import perf_counter

from .answering import answer
from .citation_audit import audit_answer
from .models import SearchRequest, ValidationError
from .review import load_candidates, validate_holdout_lock
from .search_service import RETRIEVERS, retrieve
from .vector_store import corpus_fingerprint, load_chunks


def _matches(chunk, anchor):
    return (chunk.source.source_id == anchor['source_id'] and chunk.source.sha256 == anchor['source_sha256']
            and anchor['section_contains'] in chunk.section and anchor['text_contains'] in chunk.text)


def _latency(values):
    values = sorted(values)
    return {'count': len(values), 'median_ms': median(values) if values else None,
            'p95_nearest_rank_ms': values[math.ceil(.95*len(values))-1] if values else None}


def summarize_observations(rows, method):
    selected = [row for row in rows if row['method'] == method]
    eligible = [row for row in selected if row['category'] == 'answerable']
    successes = [row for row in eligible if row['retrieval_completed']]
    ranks = [row['first_known_anchor_rank'] for row in successes]
    answers = [row for row in selected if row.get('answer') is not None]
    audits = [row['citation_audit'] for row in answers]
    total_citations = sum(audit['citation_count'] for audit in audits)
    valid_citations = sum(audit['mechanically_valid_citations'] for audit in audits)
    provisional_answers = [row['case_id'] for row in answers
                           if row['expected_decision'] == 'abstain' and row['answer']['status'] == 'answered']
    usage = [row['answer'].get('usage') or {} for row in answers]
    return {
        'attempted_cases': len(selected), 'case_errors': sum(row['error'] is not None for row in selected),
        'retrieval_stage_errors': sum(row['error'] is not None and row['error']['stage']=='retrieval' for row in selected),
        'answer_stage_errors': sum(row['error'] is not None and row['error']['stage']=='answering' for row in selected),
        'positive_anchor_cases': len(eligible), 'positive_anchor_case_errors': len(eligible)-len(successes),
        'known_anchor_hit_at_5_errors_as_misses': sum(rank is not None for rank in ranks)/len(eligible) if eligible else None,
        'known_anchor_mrr_at_5_errors_as_zero': sum(1/rank for rank in ranks if rank is not None)/len(eligible) if eligible else None,
        'known_anchor_hit_at_5_successful_calls_only': sum(rank is not None for rank in ranks)/len(successes) if successes else None,
        'retrieval_latency': _latency([row['retrieval_latency_ms'] for row in selected if row['retrieval_latency_ms'] is not None]),
        'answer_pipeline_latency': _latency([row['answer']['latency_ms'] for row in answers]),
        'audited_answer_results': len(answers),
        'answer_runtime_errors': sum(row['answer']['status']=='error' for row in answers),
        'answer_status_counts': dict(Counter(row['answer']['status'] for row in answers)),
        'answer_status_by_category': {category: dict(Counter(row['answer']['status'] for row in answers if row['category']==category))
                                      for category in sorted({row['category'] for row in selected})},
        'answers_on_draft_abstention_labels': {'count': len(provisional_answers), 'case_ids': provisional_answers},
        'output_contract_failures': sum(not audit['output_contract_valid'] for audit in audits),
        'citation_count': total_citations, 'mechanically_valid_citations': valid_citations,
        'mechanical_citation_validity_fraction': valid_citations/total_citations if total_citations else None,
        'citation_semantic_correctness': None, 'unsupported_answer_rate': None,
        'version_violating_hits': sum(row['version_violations'] for row in selected),
        'access_violating_hits': sum(row['access_violations'] for row in selected),
        'model_calls': sum(row['answer']['model_called'] for row in answers),
        'prompt_tokens': sum(item.get('prompt_tokens',0) for item in usage),
        'output_tokens': sum(item.get('output_tokens',0) for item in usage), 'api_fee_usd': 0,
    }


def run_evaluation(index_path: Path, vector_path: Path, dataset_path: Path, *, split='development',
                   methods=RETRIEVERS, generate=False, lock_path=None, review_path=None,
                   embedding_client=None, generator=None):
    """Do not execute a candidate holdout without matching completed human reviews."""
    if (not isinstance(split, str) or split not in {'development','holdout'} or type(generate) is not bool
            or not isinstance(methods, (tuple,list)) or not methods
            or any(not isinstance(method,str) or method not in RETRIEVERS for method in methods)
            or len(set(methods)) != len(methods)):
        raise ValidationError('Select development/holdout and distinct approved retrieval methods.')
    chunks = load_chunks(index_path)
    dataset_digest = sha256(dataset_path.read_bytes()).hexdigest()
    data = load_candidates(dataset_path, chunks)
    if sha256(dataset_path.read_bytes()).hexdigest() != dataset_digest:
        raise ValidationError('Dataset changed while it was being loaded.')
    fingerprint = corpus_fingerprint(chunks)
    if split == 'holdout':
        if lock_path is None or review_path is None:
            raise ValidationError('Holdout execution requires completed human review and its matching lock.')
        validate_holdout_lock(lock_path,dataset_path,review_path,chunks)
    chosen = [case for case in data['cases'] if case['split'] == ('development' if split=='development' else 'candidate_holdout')]
    if not chosen:
        raise ValidationError('The selected split has no cases.')
    embedding_identity = None
    if any(method != 'keyword' for method in methods):
        from .embeddings import LocalEmbeddingClient
        embedding_client = embedding_client or LocalEmbeddingClient()
        embedding_identity = embedding_client.identity()
    model_inventory = None
    if generate:
        if generator is None:
            from .local_model import LocalModelClient
            generator = LocalModelClient()
        if hasattr(generator,'health'):
            model_inventory = generator.health()
    rows = []
    for case in chosen:
        request = SearchRequest(case['question'],case['version'],5,case['access_profile'])
        for method in methods:
            row = {key: case[key] for key in ('case_id','group_id','question','version','access_profile','category','expected_decision')}
            trial_started = perf_counter()
            row.update(method=method, error=None, retrieval_completed=False, retrieval_latency_ms=None, first_known_anchor_rank=None,
                       matched_anchor_sources=[], hits=[], version_violations=0, access_violations=0,
                       answer=None, citation_audit=None)
            try:
                started = perf_counter()
                hits = retrieve(index_path,request,method=method,vector_path=vector_path,client=embedding_client)
                row['retrieval_latency_ms'] = round((perf_counter()-started)*1000,3)
                row['version_violations'] = sum(hit.chunk.source.version != request.version for hit in hits)
                row['access_violations'] = sum(not request.allows(hit.chunk.source) for hit in hits)
                if row['version_violations'] or row['access_violations']:
                    raise ValidationError('Retrieval violated the selected version or access profile.')
                row['hits'] = [hit.to_dict() for hit in hits]
                ranks = [rank for rank,hit in enumerate(hits,1) if any(_matches(hit.chunk,anchor) for anchor in case['anchors'])]
                row['first_known_anchor_rank'] = min(ranks) if ranks else None
                row['matched_anchor_sources'] = sorted({hit.chunk.source.source_id for hit in hits
                                                        if any(_matches(hit.chunk,anchor) for anchor in case['anchors'])})
                row['retrieval_completed'] = True
                if generate:
                    output = answer(index_path,request,generator,retrieval_method=method,
                                    vector_path=vector_path,embedding_client=embedding_client)
                    row['answer'] = output
                    row['citation_audit'] = audit_answer(output,request,chunks)
            except (ValidationError, OSError, RuntimeError, sqlite3.Error) as error:
                row['error'] = {'stage':'answering' if row['retrieval_completed'] else 'retrieval',
                                'type':type(error).__name__,'message':str(error)[:500]}
            row['trial_latency_ms'] = round((perf_counter()-trial_started)*1000,3)
            rows.append(row)
    if sha256(dataset_path.read_bytes()).hexdigest() != dataset_digest or corpus_fingerprint(load_chunks(index_path)) != fingerprint:
        raise ValidationError('Dataset or corpus changed during execution; report was not finalized.')
    if embedding_identity is not None and embedding_client.identity() != embedding_identity:
        raise ValidationError('Embedding model changed during evaluation.')
    if model_inventory is not None and generator.health().get('digest') != model_inventory.get('digest'):
        raise ValidationError('Generation model changed during evaluation.')
    if split == 'holdout':
        validate_holdout_lock(lock_path,dataset_path,review_path,load_chunks(index_path))
    return {
        'schema_version':1,'kind':'support_evaluation_observations','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
        'split':split,'question_review_records_validated':split=='holdout','human_claim_review_completed':False,
        'held_out_benchmark':split=='holdout','candidate_labels_provisional':split=='development',
        'dataset_sha256':dataset_digest,'corpus_fingerprint':fingerprint,'cases_executed':len(chosen),
        'candidate_holdout_cases_executed':len(chosen) if split=='holdout' else 0,
        'protocol':{**data['protocol'],'methods':list(methods),'fixed_method_order':True,'generation':generate,
                    'reranker':None,'keyword_remains_default':True},
        'embedding_identity':vars(embedding_identity) if embedding_identity is not None else None,
        'generation_model_inventory':model_inventory,
        'summary':{method:summarize_observations(rows,method) for method in methods},'results':rows,
        'limitations':['Draft question labels are not human ground truth. Positive anchors are not exhaustive relevance labels.',
                       'Mechanical quote/provenance checks do not establish semantic entailment or answer accuracy.',
                       'Unsupported-answer rate remains unavailable until a person judges generated claims.',
                       'Fixed-order local repeated probes include model loading, warming and swapping; no latency guarantee.',
                       'Profiles and conflicts use prominently labelled fictional documents; not production authentication.'],
    }
