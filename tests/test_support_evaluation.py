"""Evaluation boundaries with deterministic models and fictional review fixtures.

Passing these tests is not evidence of answer quality or genuine human review.
"""

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from test_answering import FakeGenerator
from test_models import example_source
from test_permissions import synthetic_source, RESTRICTED_TEXT
from test_vector_store import FakeEmbeddingClient
from versionlens.answering import quote_spans
from versionlens.benchmark import run_evaluation
from versionlens.citation_audit import audit_answer
from versionlens.ingest import Corpus, chunk_markdown
from versionlens.local_model import LocalModelError
from versionlens.models import SearchRequest, ValidationError
from versionlens.retrieval import SearchHit
from versionlens.review import freeze_holdout, make_review_template
from versionlens.store import replace_corpus
from versionlens.vector_store import build_vector_index, corpus_fingerprint


PUBLIC_TEXT = 'The public timeout is five seconds for network inactivity.'
OLD_TEXT = 'The previous timeout is ten seconds for network inactivity.'
ABSTAIN = {'decision': 'insufficient_evidence', 'claims': []}


def case(case_id, group, question, source=None, *, version='0.28.1', profile='public',
         split='development', category='answerable', text=None):
    return {
        'case_id': case_id, 'group_id': group, 'split': split, 'question': question,
        'version': version, 'access_profile': profile, 'category': category,
        'expected_decision': 'answer' if category == 'answerable' else 'abstain',
        'anchors': [] if source is None else [{'source_id': source.source_id,
            'source_sha256': source.sha256, 'section_contains': source.title,
            'text_contains': text}],
        'reference_answer': 'DRAFT fixture answer, not human-reviewed.' if source else '',
        'review_notes': 'Unit-test fixture; never a real question-review attestation.',
        'prior_development_overlap': [],
    }


def cited_result(chunk):
    citation = {**SearchHit(chunk, 1).to_dict(), 'evidence_id': 'E1', 'quote_id': 'Q1',
                'quote': quote_spans(chunk.text)[0]}
    return {'status': 'answered', 'claims': [{'text': 'The timeout is five seconds.', 'citations': [citation]}],
            'answer': 'The timeout is five seconds.', 'evidence_ids': ['E1'],
            'model_called': True, 'citation_identity_and_quotes_checked': True,
            'semantic_support_verified': False}


class CitationAuditTests(unittest.TestCase):
    def setUp(self):
        self.public = example_source(text=PUBLIC_TEXT)
        self.current = chunk_markdown(self.public, PUBLIC_TEXT)[0]
        previous = example_source('0.27.2', OLD_TEXT)
        self.previous = chunk_markdown(previous, OLD_TEXT)[0]
        restricted = synthetic_source()
        self.restricted = chunk_markdown(restricted, RESTRICTED_TEXT)[0]
        self.chunks = (self.current, self.previous, self.restricted)
        self.request = SearchRequest('default timeout', '0.28.1')

    def audit(self, output):
        return audit_answer(output, self.request, self.chunks)

    def test_exact_quote_and_canonical_provenance_pass_mechanical_checks(self):
        audited = self.audit(cited_result(self.current))
        self.assertTrue(audited['output_contract_valid'])
        self.assertEqual(audited['citation_count'], 1)
        self.assertEqual(audited['mechanically_valid_citations'], 1)
        self.assertFalse(audited['semantic_support_verified'])
        self.assertIsNone(audited['unsupported_answer'])

    def test_opposite_claim_is_not_mistaken_for_automatically_verified_entailment(self):
        output = cited_result(self.current)
        output['claims'][0]['text'] = 'The public timeout is NOT five seconds.'
        audited = self.audit(output)
        self.assertEqual(audited['mechanically_valid_citations'], 1)
        self.assertFalse(audited['semantic_support_verified'])
        self.assertIsNone(audited['unsupported_answer'])

    def test_modified_identity_metadata_or_literal_quote_is_rejected(self):
        changes = (
            {'source_sha256': 'f' * 64}, {'source_id': 'invented'}, {'version': '0.27.2'},
            {'citation_url': 'https://untrusted.invalid/source'}, {'access': 'support'},
            {'text': 'Altered source body'}, {'start_line': 99},
            {'quote': 'a fabricated quote'}, {'quote_id': 'Q2'}, {'evidence_id': 'E99'},
        )
        for fields in changes:
            output = cited_result(self.current)
            output['claims'][0]['citations'][0].update(fields)
            with self.subTest(fields=fields):
                audit = self.audit(output)
                self.assertEqual(audit['mechanically_valid_citations'], 0)
                self.assertTrue(audit['citations'][0]['failures'])

    def test_real_other_version_or_restricted_source_still_fails_request_boundary(self):
        for chunk, expected in ((self.previous, 'wrong_version'), (self.restricted, 'access_violation')):
            output = cited_result(chunk)
            with self.subTest(expected=expected):
                audit = self.audit(output)
                self.assertIn(expected, audit['citations'][0]['failures'])
                self.assertEqual(audit['mechanically_valid_citations'], 0)

    def test_unknown_or_malformed_chunk_ids_are_audited_without_exception(self):
        for chunk_id in ('0' * 24, None, [], {'unexpected': 'object'}):
            output = cited_result(self.current)
            output['claims'][0]['citations'][0]['chunk_id'] = chunk_id
            with self.subTest(chunk_id=chunk_id):
                audit = self.audit(output)
                self.assertEqual(audit['mechanically_valid_citations'], 0)
                self.assertIn('unknown_chunk', audit['citations'][0]['failures'])

    def test_invalid_quote_ids_cannot_crash_or_validate_the_audit(self):
        for quote_id in (None, [], 'Q0', 'Q-1', 'Q99999', 'Q' + '9' * 5000):
            output = cited_result(self.current)
            output['claims'][0]['citations'][0]['quote_id'] = quote_id
            with self.subTest(quote_id=str(quote_id)[:30]):
                audit = self.audit(output)
                self.assertEqual(audit['mechanically_valid_citations'], 0)

    def test_abstention_with_partial_claim_is_a_contract_failure(self):
        output = cited_result(self.current)
        output['status'] = 'abstained'
        audit = self.audit(output)
        self.assertFalse(audit['output_contract_valid'])
        self.assertIn('withheld_output_contains_partial_answer', audit['output_problems'])

    def test_invalid_claims_and_unquoted_claims_are_not_clean_outputs(self):
        for claims in (None, [], ['malformed'], [{'text': 'A claim', 'citations': []}]):
            output = cited_result(self.current)
            output['claims'] = claims
            with self.subTest(claims=claims):
                audit = self.audit(output)
                self.assertFalse(audit['output_contract_valid'])


class SupportEvaluationRunnerTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.index = self.root / 'source.sqlite3'
        self.vectors = self.root / 'vectors.sqlite3'
        self.dataset = self.root / 'questions.json'
        self.public = example_source(text=PUBLIC_TEXT)
        self.previous = example_source('0.27.2', OLD_TEXT)
        self.restricted = synthetic_source()
        sources = (self.public, self.previous, self.restricted)
        texts = (PUBLIC_TEXT, OLD_TEXT, RESTRICTED_TEXT)
        self.chunks = tuple(chunk for source, text in zip(sources, texts) for chunk in chunk_markdown(source, text))
        self.corpus = Corpus(sources, self.chunks)
        replace_corpus(self.index, self.corpus)
        self.embedding = FakeEmbeddingClient()
        build_vector_index(self.index, self.vectors, self.embedding)
        self.generator = FakeGenerator(ABSTAIN)
        self.data = {
            'schema_version': 2, 'kind': 'question_review_candidates', 'review_status': 'draft',
            'label_origin': 'Fictional unit-test fixtures, not independent human review.',
            'protocol': {'top_k': 5, 'candidate_pool': 20, 'rrf_constant': 60},
            'corpus_fingerprint': corpus_fingerprint(self.chunks),
            'cases': [case('D1', 'public-timeout', 'default timeout', self.public, text=PUBLIC_TEXT),
                      case('D2', 'orion-support', 'orion code', self.restricted, profile='support',
                           text='The orion timeout escalation code is AMBER-NINE'),
                      case('D3', 'unknown-feature', 'unicornnoevidence', category='missing_evidence'),
                      case('H1', 'old-snapshot', 'older timeout', self.previous, version='0.27.2',
                           split='candidate_holdout', text=OLD_TEXT)],
        }
        self.write_dataset()

    def write_dataset(self):
        self.dataset.write_text(json.dumps(self.data), encoding='utf-8')

    def run_observations(self, **kwargs):
        options = {'embedding_client': self.embedding, 'generator': self.generator}
        options.update(kwargs)
        return run_evaluation(self.index, self.vectors, self.dataset, **options)

    def test_development_executes_only_development_cases_across_requested_engines(self):
        report = self.run_observations(generate=True)
        self.assertEqual(report['cases_executed'], 3)
        self.assertEqual(report['candidate_holdout_cases_executed'], 0)
        self.assertEqual(len(report['results']), 9)
        self.assertEqual({row['case_id'] for row in report['results']}, {'D1', 'D2', 'D3'})
        self.assertFalse(report['held_out_benchmark'])
        self.assertTrue(report['candidate_labels_provisional'])
        for row in report['results']:
            self.assertIsNone(row['error'])
            self.assertTrue(row['retrieval_completed'])
            self.assertEqual(row['version_violations'], 0)
            self.assertEqual(row['access_violations'], 0)
            self.assertTrue(all(hit['access'] == 'public' or row['access_profile'] == 'support' for hit in row['hits']))
        for summary in report['summary'].values():
            self.assertEqual(summary['positive_anchor_cases'], 2)
            self.assertIsNone(summary['citation_semantic_correctness'])
            self.assertIsNone(summary['unsupported_answer_rate'])
            self.assertEqual(summary['api_fee_usd'], 0)
        self.assertNotIn('older timeout', self.embedding.query_calls)
        self.assertNotIn('older timeout', [call[1]['question'] for call in self.generator.calls])

    def test_retrieval_only_keyword_run_never_constructs_model_clients(self):
        with patch('versionlens.local_model.LocalModelClient') as generator, \
                patch('versionlens.embeddings.LocalEmbeddingClient') as embedding:
            report = self.run_observations(methods=('keyword',), generate=False)
        generator.assert_not_called()
        embedding.assert_not_called()
        summary = report['summary']['keyword']
        self.assertEqual(summary['model_calls'], 0)
        self.assertEqual(summary['citation_count'], 0)
        self.assertIsNone(summary['mechanical_citation_validity_fraction'])
        self.assertEqual(summary['answer_status_counts'], {})

    def test_holdout_requires_lock_before_constructing_or_calling_models(self):
        with patch('versionlens.benchmark.retrieve') as retrieval, \
                patch('versionlens.local_model.LocalModelClient') as generator, \
                patch('versionlens.embeddings.LocalEmbeddingClient') as embedding:
            with self.assertRaises(ValidationError):
                self.run_observations(split='holdout', generate=True)
        retrieval.assert_not_called()
        generator.assert_not_called()
        embedding.assert_not_called()
        self.assertEqual(self.generator.calls, [])

    def test_pending_review_cannot_be_used_to_run_a_holdout(self):
        review = make_review_template(self.data, sha256(self.dataset.read_bytes()).hexdigest())
        review_path = self.root / 'pending-review.json'
        review_path.write_text(json.dumps(review))
        lock_path = self.root / 'forged-lock.json'
        lock_path.write_text('{}')
        with patch('versionlens.benchmark.retrieve') as retrieval, self.assertRaises(ValidationError):
            self.run_observations(split='holdout', review_path=review_path, lock_path=lock_path)
        retrieval.assert_not_called()

    def test_valid_fictional_review_fixture_releases_only_the_frozen_members(self):
        # This file exists only in a temporary unit-test directory, never as real review evidence.
        review = make_review_template(self.data, sha256(self.dataset.read_bytes()).hexdigest())
        held_out = next(record for record in review['records'] if record['case_id'] == 'H1')
        held_out.update(status='approved', reviewer_type='human', reviewer='FICTIONAL UNIT-TEST REVIEWER',
                        reviewed_at='2026-10-24T10:00:00+00:00', notes='Test fixture; no real human approval occurred.')
        review_path, lock_path = self.root / 'fixture-review.json', self.root / 'fixture-lock.json'
        review_path.write_text(json.dumps(review))
        freeze_holdout(self.dataset, review_path, self.chunks, lock_path)
        report = self.run_observations(split='holdout', methods=('keyword',), review_path=review_path, lock_path=lock_path)
        self.assertEqual(report['cases_executed'], 1)
        self.assertEqual(report['candidate_holdout_cases_executed'], 1)
        self.assertEqual([row['case_id'] for row in report['results']], ['H1'])

    def test_engine_errors_are_retained_and_positive_denominator_does_not_shrink(self):
        from versionlens.search_service import retrieve
        def sometimes_fail(index, request, *, method, **kwargs):
            if method == 'vector':
                raise ValidationError('Deliberate unit-test engine failure')
            return retrieve(index, request, method=method, **kwargs)
        with patch('versionlens.benchmark.retrieve', side_effect=sometimes_fail):
            report = self.run_observations(methods=('keyword', 'vector'))
        self.assertEqual(len(report['results']), 6)
        vector = report['summary']['vector']
        self.assertEqual(vector['case_errors'], 3)
        self.assertEqual(vector['positive_anchor_cases'], 2)
        self.assertEqual(vector['positive_anchor_case_errors'], 2)
        self.assertEqual(vector['known_anchor_hit_at_5_errors_as_misses'], 0)
        self.assertIsNone(vector['known_anchor_hit_at_5_successful_calls_only'])
        self.assertEqual(report['summary']['keyword']['known_anchor_hit_at_5_errors_as_misses'], 1)

    def test_answer_stage_failure_does_not_corrupt_successful_retrieval_metrics(self):
        with patch('versionlens.benchmark.answer', side_effect=RuntimeError('Deliberate answer fixture failure')):
            report = self.run_observations(methods=('keyword',), generate=True)
        summary = report['summary']['keyword']
        self.assertEqual(summary['case_errors'], 3)
        self.assertEqual(summary['positive_anchor_case_errors'], 0)
        self.assertEqual(summary['known_anchor_hit_at_5_errors_as_misses'], 1)
        for row in report['results']:
            self.assertTrue(row['retrieval_completed'])
            self.assertEqual(row['error']['stage'], 'answering')

    def test_operational_model_failures_are_not_counted_as_evidence_abstentions(self):
        self.generator = FakeGenerator(error=LocalModelError('Unit-test model unavailable'))
        report = self.run_observations(methods=('keyword',), generate=True)
        summary = report['summary']['keyword']
        self.assertEqual(summary['answer_status_counts'], {'error': 2, 'abstained': 1})
        self.assertEqual(summary['model_calls'], 2)
        self.assertIsNone(summary['unsupported_answer_rate'])

    def test_no_positive_cases_produces_unavailable_retrieval_fraction(self):
        for item in self.data['cases']:
            if item['case_id'] != 'D3':
                item['split'] = 'candidate_holdout'
        self.write_dataset()
        summary = self.run_observations(methods=('keyword',))['summary']['keyword']
        self.assertEqual(summary['attempted_cases'], 1)
        self.assertEqual(summary['positive_anchor_cases'], 0)
        self.assertIsNone(summary['known_anchor_hit_at_5_errors_as_misses'])
        self.assertIsNone(summary['mechanical_citation_validity_fraction'])

    def test_changed_dataset_during_execution_prevents_final_report(self):
        self.embedding.on_query = lambda client: self.dataset.write_text(self.dataset.read_text() + '\n')
        with self.assertRaisesRegex(ValidationError, 'changed'):
            self.run_observations(methods=('vector',))

    def test_changed_corpus_during_execution_prevents_final_report(self):
        altered_source = replace(self.public, title='Changed source title')
        altered_chunks = tuple(replace(chunk, source=altered_source) if chunk.source == self.public else chunk for chunk in self.chunks)
        altered = Corpus((altered_source, self.previous, self.restricted), altered_chunks)
        self.embedding.on_query = lambda client: replace_corpus(self.index, altered)
        with self.assertRaisesRegex(ValidationError, 'changed'):
            self.run_observations(methods=('vector',))

    def test_changed_embedding_identity_prevents_final_report(self):
        def swap_identity(client):
            client.current_identity = replace(client.current_identity, digest='b' * 64)
        self.embedding.on_query = swap_identity
        with self.assertRaisesRegex(ValidationError, 'changed'):
            self.run_observations(methods=('vector',))


if __name__ == '__main__':
    unittest.main()
