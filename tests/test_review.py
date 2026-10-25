"""Review-release validation using fictional reviewer attestations only.

Names, approvals and timestamps created here are isolated unit-test fixtures;
they are never actual reviews or evidence of the project's evaluation quality.
"""

from copy import deepcopy
from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from test_models import example_source
from test_permissions import synthetic_source
from versionlens.ingest import chunk_markdown
from versionlens.models import ValidationError
from versionlens.review import (case_digest, freeze_holdout, load_candidates,
                                make_review_template, validate_holdout_lock)
from versionlens.vector_store import corpus_fingerprint


class ReviewReleaseTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.dataset_path = self.root/'candidates.json'
        self.review_path = self.root/'review.json'
        self.lock_path = self.root/'holdout.lock.json'
        text = '# Guide\n\nNetwork inactivity times out after five seconds.\n'
        source = example_source(text=text)
        private_text = '# SYNTHETIC DEMO: Orion escalation\n\nThe orion procedure is fictional.\n'
        private = synthetic_source(private_text)
        self.chunks = chunk_markdown(source,text)+chunk_markdown(private,private_text)
        anchor = {'source_id': source.source_id,'source_sha256':source.sha256,
                  'section_contains':'Guide','text_contains':'Network inactivity times out after five seconds.'}
        case = {'case_id':'C001','group_id':'timeout','split':'candidate_holdout',
                'question':'What is the network inactivity timeout?','version':'0.28.1','access_profile':'public',
                'category':'answerable','expected_decision':'answer','anchors':[anchor],
                'reference_answer':'Five seconds.','review_notes':'Check inactivity qualification.',
                'prior_development_overlap':[]}
        development = {**deepcopy(case),'case_id':'D001','group_id':'development-probe','split':'development',
                       'question':'Which timeout is documented?','prior_development_overlap':['legacy-D04']}
        self.data = {'schema_version':2,'kind':'question_review_candidates','review_status':'draft',
                     'label_origin':'Fictional unit-test labels; never actual human review.',
                     'protocol':{'top_k':5,'candidate_pool':20,'rrf_constant':60},
                     'corpus_fingerprint':corpus_fingerprint(self.chunks),'cases':[case,development]}
        self.save_dataset()

    def save_dataset(self):
        self.dataset_path.write_text(json.dumps(self.data,indent=2))

    def template(self):
        return make_review_template(self.data,sha256(self.dataset_path.read_bytes()).hexdigest())

    def fixture_review(self):
        review = self.template()
        for record in review['records']:
            if record['case_id']=='C001':
                record.update(status='approved',reviewer_type='human',reviewer='Fictional test reviewer',
                              reviewed_at='2026-01-01T12:00:00+00:00',notes='Unit-test fixture, not real human review.')
        return review

    def save_review(self,review=None):
        self.review_path.write_text(json.dumps(review if review is not None else self.fixture_review(),indent=2))

    def freeze(self):
        return freeze_holdout(self.dataset_path,self.review_path,self.chunks,self.lock_path)

    def test_pending_template_cannot_freeze_or_claim_human_review(self):
        template = self.template()
        self.assertTrue(all(record['status']=='pending' and record['reviewer'] is None for record in template['records']))
        self.save_review(template)
        with self.assertRaises(ValidationError): self.freeze()
        self.assertFalse(self.lock_path.exists())

    def test_digest_bound_fixture_release_preserves_development_pending(self):
        self.save_review()
        locked = self.freeze()
        self.assertEqual(locked['case_ids'],['C001'])
        self.assertEqual(locked['case_sha256']['C001'],case_digest(self.data['cases'][0]))
        self.assertEqual(validate_holdout_lock(self.lock_path,self.dataset_path,self.review_path,self.chunks),locked)
        self.assertEqual(load_candidates(self.dataset_path,self.chunks),self.data)

    def test_freeze_never_overwrites_an_existing_release(self):
        self.save_review(); self.freeze()
        before = self.lock_path.read_bytes()
        with self.assertRaises(ValidationError): self.freeze()
        self.assertEqual(self.lock_path.read_bytes(),before)

    def test_changed_question_or_label_invalidates_prior_review(self):
        self.save_review()
        for field,value in (('question','A changed support question?'),('reference_answer','A changed reference answer.')):
            with self.subTest(field=field):
                changed = deepcopy(self.data)
                changed['cases'][0][field] = value
                self.dataset_path.write_text(json.dumps(changed))
                with self.assertRaises(ValidationError): self.freeze()
                self.assertFalse(self.lock_path.exists())

    def test_changed_corpus_and_missing_anchor_are_rejected(self):
        changed = replace(self.chunks[0],text='A changed source text.')
        with self.assertRaises(ValidationError): load_candidates(self.dataset_path,(changed,*self.chunks[1:]))
        for field,value in (('source_sha256','0'*64),('source_id','missing'),('text_contains','Absent source fragment.')):
            case = deepcopy(self.data)
            case['cases'][0]['anchors'][0][field]=value
            self.dataset_path.write_text(json.dumps(case))
            with self.subTest(field=field),self.assertRaises(ValidationError):
                load_candidates(self.dataset_path,self.chunks)

    def test_inaccessible_and_wrong_version_anchors_are_rejected(self):
        private = self.chunks[1]
        self.data['cases'][0]['anchors']=[{'source_id':private.source.source_id,
            'source_sha256':private.source.sha256,'section_contains':'SYNTHETIC DEMO','text_contains':'fictional'}]
        self.save_dataset()
        with self.assertRaises(ValidationError): load_candidates(self.dataset_path,self.chunks)
        self.data['cases'][0]['access_profile']='support'
        self.data['cases'][0]['version']='0.27.2'
        self.save_dataset()
        with self.assertRaises(ValidationError): load_candidates(self.dataset_path,self.chunks)

    def test_topic_groups_and_normalized_duplicate_questions_cannot_leak_across_splits(self):
        for change in ({'group_id':'timeout'}, {'question':'  WHAT IS THE NETWORK  INACTIVITY TIMEOUT? '}):
            data = deepcopy(self.data)
            data['cases'][1].update(change)
            self.dataset_path.write_text(json.dumps(data))
            with self.subTest(change=change),self.assertRaises(ValidationError):
                load_candidates(self.dataset_path,self.chunks)

    def test_cross_profile_permission_probes_are_not_duplicate_questions(self):
        case = deepcopy(self.data['cases'][0])
        case.update(case_id='C002',access_profile='support')
        self.data['cases'].append(case);self.save_dataset()
        self.assertEqual(len(load_candidates(self.dataset_path,self.chunks)['cases']),3)

    def test_prior_development_overlap_forces_development_split(self):
        self.data['cases'][0]['prior_development_overlap']=['legacy-D04'];self.save_dataset()
        with self.assertRaises(ValidationError): load_candidates(self.dataset_path,self.chunks)

    def test_case_ids_categories_decisions_and_protocol_fail_closed(self):
        changes=[lambda data:data['cases'][1].update(case_id='C001'),
                 lambda data:data['cases'][0].update(category='unknown'),
                 lambda data:data['cases'][0].update(expected_decision='abstain'),
                 lambda data:data['cases'][0].update(anchors=[]),
                 lambda data:data['protocol'].update(top_k=5.0),
                 lambda data:data.update(schema_version=True)]
        for change in changes:
            data = deepcopy(self.data);change(data);self.dataset_path.write_text(json.dumps(data))
            with self.assertRaises(ValidationError): load_candidates(self.dataset_path,self.chunks)

    def test_conflict_requires_two_distinct_accessible_sources(self):
        case = self.data['cases'][0]
        case.update(category='conflicting_evidence',expected_decision='abstain')
        self.save_dataset()
        with self.assertRaises(ValidationError): load_candidates(self.dataset_path,self.chunks)
        private=self.chunks[1]
        case['access_profile']='support'
        case['anchors'].append({'source_id':private.source.source_id,'source_sha256':private.source.sha256,
                                'section_contains':'SYNTHETIC DEMO','text_contains':'fictional'})
        self.save_dataset()
        self.assertEqual(load_candidates(self.dataset_path,self.chunks)['cases'][0]['category'],'conflicting_evidence')

    def test_abstention_categories_have_no_positive_answer_anchors(self):
        for category in ('missing_evidence','wrong_version_trap','permission_denied'):
            data=deepcopy(self.data)
            data['cases'][0].update(category=category,expected_decision='abstain')
            self.dataset_path.write_text(json.dumps(data))
            with self.subTest(category=category),self.assertRaises(ValidationError):
                load_candidates(self.dataset_path,self.chunks)

    def test_missing_extra_duplicate_or_stale_review_records_cannot_release(self):
        changes=[lambda review:review['records'].pop(),
                 lambda review:review['records'].append(deepcopy(review['records'][0])),
                 lambda review:review['records'][1].update(case_id='C001'),
                 lambda review:review['records'][0].update(case_sha256='0'*64),
                 lambda review:review['records'][0].update(case_id='unknown')]
        for change in changes:
            review=self.fixture_review();change(review);self.save_review(review)
            with self.assertRaises(ValidationError): self.freeze()

    def test_holdout_rejection_and_nonhuman_or_incomplete_approval_cannot_release(self):
        for change in ({'status':'rejected'},{'reviewer_type':'assistant'},{'reviewer':''},
                       {'reviewed_at':None},{'reviewed_at':'2026-01-01'},
                       {'reviewed_at':'2999-01-01T00:00:00+00:00'}):
            review=self.fixture_review();review['records'][0].update(change);self.save_review(review)
            with self.subTest(change=change),self.assertRaises(ValidationError): self.freeze()

    def test_changed_review_invalidates_lock_even_if_cases_remain_approved(self):
        self.save_review();self.freeze()
        review=json.loads(self.review_path.read_text());review['records'][0]['notes']='Changed human review notes.'
        self.save_review(review)
        with self.assertRaises(ValidationError):
            validate_holdout_lock(self.lock_path,self.dataset_path,self.review_path,self.chunks)

    def test_forged_lock_fields_membership_and_boolean_schema_are_rejected(self):
        self.save_review();self.freeze()
        original=json.loads(self.lock_path.read_text())
        for change in ({'schema_version':True},{'case_ids':['C001','D001']},
                       {'case_sha256':{'C001':'0'*64}},{'review_sha256':'0'*64},{'extra':'untrusted'}):
            self.lock_path.write_text(json.dumps({**original,**change}))
            with self.subTest(change=change),self.assertRaises(ValidationError):
                validate_holdout_lock(self.lock_path,self.dataset_path,self.review_path,self.chunks)

    def test_strict_json_rejects_duplicate_keys_nonfinite_values_and_extra_fields(self):
        for raw in ('{"schema_version":2,"schema_version":2}', '{"schema_version":NaN}', '[]'):
            self.dataset_path.write_text(raw)
            with self.assertRaises(ValidationError): load_candidates(self.dataset_path,self.chunks)
        self.data['untrusted']='extra';self.save_dataset()
        with self.assertRaises(ValidationError): load_candidates(self.dataset_path,self.chunks)

    def test_no_holdout_group_cannot_create_a_holdout_release(self):
        self.data['cases'][0]['split']='development';self.save_dataset()
        self.save_review(self.template())
        with self.assertRaises(ValidationError): self.freeze()
        self.assertFalse(self.lock_path.exists())


if __name__=='__main__':
    unittest.main()
