import json
from pathlib import Path
from unittest.mock import patch
import unittest

from test_models import example_source
from versionlens.answering import MAX_CONTEXT_CHARS, answer, select_evidence, validate_draft
from versionlens.config import LocalModelConfig
from versionlens.local_model import LocalModelError, ModelResponse
from versionlens.models import Chunk, SearchRequest, ValidationError
from versionlens.retrieval import SearchHit


QUOTE = "The proxies argument has been removed."


def hit(version="0.28.1", text=QUOTE):
    return SearchHit(Chunk.create(example_source(version, text), "Changelog > 0.28.0", 1, 1, text), 1.0)


def draft(text="The deprecated proxies argument was removed.", quote=QUOTE, evidence_id="E1"):
    return {"status": "answered", "reason": "", "claims": [{"text": text,
            "citations": [{"evidence_id": evidence_id, "quote": quote}]}]}


class FakeGenerator:
    def __init__(self, output=None, error=None):
        self.output, self.error, self.calls = output, error, []

    def generate(self, system, prompt, schema):
        self.calls.append((system, json.loads(prompt), schema))
        if self.error:
            raise self.error
        return ModelResponse(response=json.dumps(self.output), model="qwen3:1.7b",
                             prompt_tokens=100, output_tokens=25, total_duration_ns=1000)


class DraftValidationTests(unittest.TestCase):
    def setUp(self):
        self.evidence = select_evidence((hit(),), "0.28.1")

    def test_valid_quotes_receive_server_owned_source_metadata(self):
        result = validate_draft(json.dumps(draft()), self.evidence)
        cite = result["claims"][0]["citations"][0]
        self.assertEqual(cite["version"], "0.28.1")
        self.assertEqual(cite["quote"], QUOTE)
        self.assertEqual(cite["citation_url"], self.evidence[0].hit.chunk.citation_url)

    def test_unknown_citation_fabricated_quote_and_extra_url_fail_closed(self):
        invented_url = draft()
        invented_url["claims"][0]["citations"][0]["url"] = "https://untrusted.example"
        cases = [draft(evidence_id="E99"), draft(quote="This text is not in the document."),
                 draft(quote=" "), invented_url, {"status": "answered", "reason": "", "claims": []}]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_draft(json.dumps(value), self.evidence)

    def test_duplicate_keys_nonstandard_numbers_and_empty_claims_are_rejected(self):
        values = ['{"status":"answered","status":"abstained","claims":[],"reason":"unrelated_evidence"}',
                  '{"status":"abstained","claims":[],"reason":NaN}', json.dumps(draft(text=" ")),
                  "[1,2,3]", "{" * 1000]
        for value in values:
            with self.subTest(value=value[:40]), self.assertRaises(ValidationError):
                validate_draft(value, self.evidence)

    def test_invalid_unicode_and_forged_inline_links_are_rejected(self):
        for text in ("claim " + chr(0xd800), "[E99](https://untrusted.example)",
                     "A claim [E99]", "Go to https://untrusted.example", "<script>do bad things</script>",
                     "A claim [source].\n\n[source]: //untrusted.example"):
            with self.subTest(text=repr(text)), self.assertRaises(ValidationError):
                validate_draft(json.dumps(draft(text=text)), self.evidence)

    def test_whitespace_cannot_bypass_supporting_quote_length_bound(self):
        quote = " " * 600 + QUOTE
        evidence = select_evidence((hit(text=quote),), "0.28.1")
        with self.assertRaises(ValidationError):
            validate_draft(json.dumps(draft(quote=quote)), evidence)

    def test_quote_from_other_chunk_is_not_accepted_for_selected_id(self):
        other = hit(text="Use the proxy argument for a single proxy.")
        evidence = select_evidence((hit(), other), "0.28.1")
        with self.assertRaises(ValidationError):
            validate_draft(json.dumps(draft(quote=other.chunk.text)), evidence)

    def test_abstention_cannot_smuggle_claims_or_freeform_advice(self):
        for value in ({"status": "abstained", "claims": draft()["claims"], "reason": "insufficient_evidence"},
                      {"status": "abstained", "claims": [], "reason": "Try inventing a new API"}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_draft(json.dumps(value), self.evidence)

    def test_context_is_bounded_and_mixed_versions_are_rejected(self):
        large = hit(text="x" * (MAX_CONTEXT_CHARS + 1))
        self.assertEqual(select_evidence((large,), "0.28.1"), ())
        with self.assertRaises(ValidationError):
            select_evidence((hit(), hit(version="0.27.2")), "0.28.1")
        self.assertEqual(len(select_evidence((hit(), hit()), "0.28.1")), 1)

    def test_question_and_unicode_bytes_count_toward_full_input_budget(self):
        small_config = LocalModelConfig(num_ctx=512, max_output_tokens=100)
        self.assertEqual(select_evidence((hit(),), "0.28.1", config=small_config), ())
        self.assertEqual(select_evidence((hit(),), "0.28.1", question="界" * 2000), ())


class AnswerPipelineTests(unittest.TestCase):
    def run_with(self, hits, generator):
        with patch("versionlens.answering.search", return_value=hits):
            return answer(Path("unused.sqlite3"), SearchRequest("Why proxies?", "0.28.1"), generator)

    def test_no_matches_do_not_call_model(self):
        model = FakeGenerator(draft())
        result = self.run_with((), model)
        self.assertEqual(result["reason"], "no_matching_evidence")
        self.assertEqual(result["status"], "abstained")
        self.assertFalse(result["model_called"])
        self.assertEqual(model.calls, [])

    def test_success_is_cited_but_never_claims_semantic_verification(self):
        model = FakeGenerator(draft())
        result = self.run_with((hit(),), model)
        self.assertEqual(result["status"], "answered")
        self.assertTrue(result["citation_identity_and_quotes_checked"])
        self.assertFalse(result["semantic_support_verified"])
        self.assertEqual(model.calls[0][1]["requested_version"], "0.28.1")
        self.assertIn("Changelog > 0.28.0", model.calls[0][1]["evidence"][0]["section"])
        self.assertIn("?plain=1#L", result["answer"])

    def test_opposite_claim_with_real_quote_is_not_marked_semantically_verified(self):
        # This deliberately documents the limit of a mechanical quote check.
        result = self.run_with((hit(),), FakeGenerator(draft(text="The proxies argument is still accepted.")))
        self.assertFalse(result["semantic_support_verified"])
        self.assertIn("semantic support", result["notice"])

    def test_invalid_generation_exposes_no_partial_answer(self):
        result = self.run_with((hit(),), FakeGenerator(draft(evidence_id="E99")))
        self.assertEqual(result["status"], "abstained")
        self.assertEqual(result["reason"], "invalid_generation")
        self.assertIsNone(result["answer"])
        self.assertEqual(result["claims"], [])

    def test_runtime_error_is_distinct_from_missing_evidence(self):
        result = self.run_with((hit(),), FakeGenerator(error=LocalModelError("test")))
        self.assertEqual(result["status"], "error")
        self.assertEqual(result["reason"], "local_model_error")
        self.assertTrue(result["model_called"])
        self.assertIsNone(result["usage"])
