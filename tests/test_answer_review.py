"""Human-answer review validation using explicitly fictional temporary attestations."""

from copy import deepcopy
from datetime import datetime, timedelta, timezone
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from versionlens.answer_review import make_answer_review_template, validate_and_score_answer_review
from versionlens.models import ValidationError


def trial(case_id, method, claims=None, status='answered'):
    return {'case_id': case_id, 'method': method, 'question': 'A fictional test question.',
            'version': '0.28.1', 'access_profile': 'public',
            'answer': {'status': status, 'answer': 'Fixture answer.' if status == 'answered' else None,
                       'claims': [{'text': text, 'citations': []} for text in (claims or [])]}}


class HumanAnswerReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.report_path, self.review_path = self.root/'report.json', self.root/'review.json'
        self.report = {'schema_version': 1, 'kind': 'support_evaluation_observations', 'results': [
            trial('D1', 'keyword', ['First fictional claim.', 'Second fictional claim.']),
            trial('D2', 'vector', ['Third fictional claim.']),
            trial('D3', 'keyword', status='abstained'), trial('D4', 'keyword', status='error'),
            {'case_id': 'D5', 'method': 'hybrid', 'answer': None}]}
        self.write_report()
        self.review = make_answer_review_template(self.report, sha256(self.report_path.read_bytes()).hexdigest())

    def write_report(self):
        self.report_path.write_text(json.dumps(self.report))

    def completed(self):
        # These attestations exist solely in a temporary unit-test directory.
        review = deepcopy(self.review)
        for record in review['records']:
            record.update(status='completed', reviewer_type='human', reviewer='FICTIONAL UNIT-TEST REVIEWER',
                          reviewed_at='2026-10-24T10:00:00+00:00', notes='Fixture only; no real human review occurred.')
            for claim in record['claims']:
                claim.update(status='completed', supported=True, correct=True, notes='Unit-test judgment fixture.')
        return review

    def score(self, review=None):
        self.review_path.write_text(json.dumps(self.completed() if review is None else review))
        return validate_and_score_answer_review(self.report_path, self.review_path)

    def test_template_is_pending_and_covers_only_answered_trials_and_all_claims(self):
        self.assertEqual(len(self.review['records']), 2)
        self.assertEqual(sum(len(record['claims']) for record in self.review['records']), 3)
        for record in self.review['records']:
            self.assertEqual(record['status'], 'pending')
            self.assertIsNone(record['reviewer_type'])
            self.assertIsNone(record['reviewer'])
            self.assertIsNone(record['reviewed_at'])
            for claim in record['claims']:
                self.assertEqual(claim['status'], 'pending')
                self.assertIsNone(claim['supported'])
                self.assertIsNone(claim['correct'])

    def test_pending_templates_cannot_be_scored_as_completed_human_review(self):
        with self.assertRaises(ValidationError):
            self.score(self.review)

    def test_supported_and_correct_are_scored_independently(self):
        review = self.completed()
        review['records'][0]['claims'][0]['supported'] = False
        review['records'][0]['claims'][1]['correct'] = False
        scores = self.score(review)
        self.assertEqual(scores['reviewed_answer_count'], 2)
        self.assertEqual(scores['reviewed_claim_count'], 3)
        self.assertEqual(scores['unsupported_claim_count'], 1)
        self.assertAlmostEqual(scores['unsupported_claim_rate'], 1/3)
        self.assertEqual(scores['unsupported_answer_count'], 1)
        self.assertEqual(scores['unsupported_answer_rate'], .5)
        self.assertAlmostEqual(scores['claim_correctness_rate'], 2/3)
        self.assertEqual(scores['all_claims_correct_answer_count'], 1)
        self.assertEqual(scores['by_method']['keyword']['unsupported_answer_rate'], 1)
        self.assertEqual(scores['by_method']['vector']['unsupported_answer_rate'], 0)
        self.assertIsNone(scores['semantic_citation_support_rate'])

    def test_correct_but_unsupported_claim_does_not_merge_support_into_correctness(self):
        for row in self.report['results']:
            if row['case_id'] == 'D1':
                row['answer']['claims'] = row['answer']['claims'][:1]
            elif row['case_id'] == 'D2':
                row['answer'] = None
        self.write_report()
        self.review = make_answer_review_template(self.report, sha256(self.report_path.read_bytes()).hexdigest())
        review = self.completed()
        review['records'][0]['claims'][0]['supported'] = False
        scores = self.score(review)
        self.assertEqual(scores['unsupported_answer_rate'], 1)
        self.assertEqual(scores['all_claims_correct_answer_rate'], 1)

    def test_missing_duplicate_and_extra_trial_records_are_rejected(self):
        complete = self.completed()
        variants = []
        missing = deepcopy(complete); missing['records'].pop(); variants.append(missing)
        duplicate = deepcopy(complete); duplicate['records'][1] = deepcopy(duplicate['records'][0]); variants.append(duplicate)
        extra = deepcopy(complete); extra['records'].append(deepcopy(extra['records'][0])); variants.append(extra)
        wrong = deepcopy(complete); wrong['records'][0]['case_id'] = 'unknown'; variants.append(wrong)
        wrong_method = deepcopy(complete); wrong_method['records'][0]['method'] = 'hybrid'; variants.append(wrong_method)
        for index, review in enumerate(variants):
            with self.subTest(index=index), self.assertRaises(ValidationError):
                self.score(review)

    def test_missing_duplicate_and_unknown_claims_are_rejected(self):
        complete = self.completed()
        variants = []
        missing = deepcopy(complete); missing['records'][0]['claims'].pop(); variants.append(missing)
        duplicate = deepcopy(complete); duplicate['records'][0]['claims'][1] = deepcopy(duplicate['records'][0]['claims'][0]); variants.append(duplicate)
        unknown = deepcopy(complete); unknown['records'][0]['claims'][0]['claim_index'] = 99; variants.append(unknown)
        boolean = deepcopy(complete); boolean['records'][0]['claims'][0]['claim_index'] = True; variants.append(boolean)
        for index, review in enumerate(variants):
            with self.subTest(index=index), self.assertRaises(ValidationError):
                self.score(review)

    def test_both_judgments_require_real_booleans(self):
        for field in ('supported', 'correct'):
            for value in (None, 0, 1, 'true', [], {}):
                review = self.completed()
                review['records'][0]['claims'][0][field] = value
                with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                    self.score(review)

    def test_every_claim_must_be_completed(self):
        review = self.completed()
        review['records'][0]['claims'][0]['status'] = 'pending'
        with self.assertRaises(ValidationError):
            self.score(review)

    def test_empty_or_nonhuman_attestations_are_rejected(self):
        for field, value in (('reviewer', ''), ('reviewer', '   '), ('reviewer_type', 'ai'),
                             ('reviewer_type', None), ('status', 'pending'), ('reviewer', None)):
            review = self.completed(); review['records'][0][field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValidationError):
                self.score(review)

    def test_review_time_requires_a_valid_nonfuture_timezone(self):
        future = (datetime.now(timezone.utc)+timedelta(days=1)).isoformat()
        for timestamp in ('not a date', '2026-10-24T10:00:00', '', None, future):
            review = self.completed(); review['records'][0]['reviewed_at'] = timestamp
            with self.subTest(timestamp=timestamp), self.assertRaises(ValidationError):
                self.score(review)

    def test_changed_report_or_stale_case_and_claim_digests_are_rejected(self):
        for location in ('report_sha256', 'case_sha256', 'claim_sha256'):
            review = self.completed()
            if location == 'report_sha256': review[location] = '0'*64
            elif location == 'case_sha256': review['records'][0][location] = '0'*64
            else: review['records'][0]['claims'][0][location] = '0'*64
            with self.subTest(location=location), self.assertRaises(ValidationError):
                self.score(review)
        review = self.completed()
        self.report['results'][0]['answer']['claims'][0]['text'] = 'Changed after judgment.'
        self.write_report()
        review['report_sha256'] = sha256(self.report_path.read_bytes()).hexdigest()
        with self.assertRaisesRegex(ValidationError, 'stale'):
            self.score(review)

    def test_extra_or_missing_review_fields_fail_closed(self):
        for level in ('root', 'record', 'claim'):
            for operation in ('extra', 'missing'):
                review = self.completed()
                target = review if level == 'root' else review['records'][0] if level == 'record' else review['records'][0]['claims'][0]
                if operation == 'extra': target['unrecognized'] = True
                else: target.pop(next(iter(target)))
                with self.subTest(level=level, operation=operation), self.assertRaises(ValidationError):
                    self.score(review)

    def test_zero_answered_outputs_have_null_rates_and_no_claimed_human_review(self):
        self.report['results'] = [trial('A', 'keyword', status='abstained'), trial('E', 'vector', status='error')]
        self.write_report()
        self.review = make_answer_review_template(self.report, sha256(self.report_path.read_bytes()).hexdigest())
        self.assertEqual(self.review['records'], [])
        scores = self.score(self.review)
        self.assertEqual(scores['reviewed_answer_count'], 0)
        self.assertEqual(scores['reviewed_claim_count'], 0)
        self.assertFalse(scores['human_review_attestations_validated'])
        for key in ('unsupported_claim_rate', 'unsupported_answer_rate', 'claim_correctness_rate',
                    'all_claims_correct_answer_rate', 'semantic_citation_support_rate'):
            self.assertIsNone(scores[key])

    def test_same_question_across_methods_counts_trials_and_unique_questions_separately(self):
        self.report['results'][1]['case_id'] = 'D1'
        self.write_report()
        self.review = make_answer_review_template(self.report, sha256(self.report_path.read_bytes()).hexdigest())
        scores = self.score()
        self.assertEqual(scores['reviewed_answer_count'], 2)
        self.assertEqual(scores['reviewed_unique_question_count'], 1)

    def test_duplicate_result_pairs_or_empty_answered_claims_are_invalid_reports(self):
        duplicate = deepcopy(self.report); duplicate['results'].append(deepcopy(duplicate['results'][0]))
        empty = deepcopy(self.report); empty['results'][0]['answer']['claims'] = []
        partial = deepcopy(self.report); partial['results'][2]['answer']['claims'] = [{'text': 'Leaked partial draft.'}]
        missing = deepcopy(self.report); missing['results'][0].pop('answer')
        malformed = deepcopy(self.report); malformed['results'][0]['answer']['status'] = []
        for report in (duplicate, empty, partial, missing, malformed):
            with self.subTest(report=report), self.assertRaises(ValidationError):
                make_answer_review_template(report, 'a'*64)

    def test_review_changed_while_scoring_cannot_return_stale_scores(self):
        from versionlens.answer_review import _read
        self.review_path.write_text(json.dumps(self.completed()))
        review_reads = 0
        def racing_read(path):
            nonlocal review_reads
            data, digest = _read(path)
            if Path(path) == self.review_path:
                review_reads += 1
                if review_reads == 1:
                    self.review_path.write_text(self.review_path.read_text()+'\n')
            return data, digest
        with patch('versionlens.answer_review._read', side_effect=racing_read), self.assertRaisesRegex(ValidationError, 'changed'):
            validate_and_score_answer_review(self.report_path, self.review_path)

    def test_duplicate_key_and_nonfinite_json_are_not_accepted(self):
        self.review_path.write_text('{"schema_version":1,"schema_version":1}')
        with self.assertRaises(ValidationError):
            validate_and_score_answer_review(self.report_path, self.review_path)
        raw = json.dumps(self.completed()).replace('"supported": true', '"supported": NaN', 1)
        self.review_path.write_text(raw)
        with self.assertRaises(ValidationError):
            validate_and_score_answer_review(self.report_path, self.review_path)


if __name__ == '__main__':
    unittest.main()
