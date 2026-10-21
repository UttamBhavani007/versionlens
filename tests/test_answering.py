import json
from pathlib import Path
from unittest.mock import patch
import unittest

from test_models import example_source
from versionlens.answering import MAX_CONTEXT_CHARS, answer, quote_spans, select_evidence, validate_draft
from versionlens.config import LocalModelConfig
from versionlens.local_model import LocalModelError, ModelResponse
from versionlens.models import Chunk, SearchRequest, ValidationError
from versionlens.retrieval import SearchHit


QUOTE = "The proxies argument has been removed."


def hit(version="0.28.1", text=QUOTE):
    return SearchHit(Chunk.create(example_source(version, text), "Changelog > 0.28.0", 1, 1, text), 1.0)


def draft(text="The deprecated proxies argument was removed.", quote_id="Q1", evidence_id="E1"):
    return {"decision": "answer", "claims": [{"text": text,
            "citations": [{"evidence_id": evidence_id, "quote_id": quote_id}]}]}


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
        invented_quote = draft()
        invented_quote["claims"][0]["citations"][0]["quote"] = "This text is not in the document."
        cases = [draft(evidence_id="E99"), draft(quote_id="Q99"), invented_quote,
                 draft(quote_id=" "), invented_url, {"decision": "answer", "claims": []}]
        for value in cases:
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_draft(json.dumps(value), self.evidence)

    def test_duplicate_keys_nonstandard_numbers_and_empty_claims_are_rejected(self):
        values = ['{"decision":"answer","decision":"unrelated_evidence","claims":[]}',
                  '{"decision":NaN,"claims":[]}', json.dumps(draft(text=" ")),
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

    def test_menu_spans_are_exact_bounded_and_long_prose_is_omitted(self):
        text = "  " + QUOTE + "  \n\n" + "x" * 601
        self.assertEqual(quote_spans(text), (QUOTE,))
        self.assertTrue(all(span in text and len(span) <= 600 for span in quote_spans(text)))

    def test_long_lists_split_at_whole_item_boundaries(self):
        first = "* " + "a" * 350 + "\n  continuation preserving the item."
        second = "* " + "b" * 350
        text = first + "\n" + second
        self.assertEqual(quote_spans(text), (first, second))

    def test_visible_code_fences_are_omitted_even_with_blank_lines(self):
        code = '```python\nclient = httpx.Client()\n\nresponse = client.get("example")\n```'
        self.assertEqual(quote_spans(code), ())
        prose = "An ordinary source paragraph survives."
        self.assertEqual(quote_spans(prose + "\n\n" + code), (prose,))

    def test_quote_from_other_chunk_is_not_accepted_for_selected_id(self):
        other = hit(text="Use the proxy argument for a single proxy.\n\nAnother valid quote exists only here.")
        evidence = select_evidence((hit(), other), "0.28.1")
        with self.assertRaises(ValidationError):
            validate_draft(json.dumps(draft(quote_id="Q2", evidence_id="E1")), evidence)

    def test_abstention_cannot_smuggle_claims_or_freeform_advice(self):
        for value in ({"decision": "insufficient_evidence", "claims": draft()["claims"]},
                      {"decision": "Try inventing a new API", "claims": []}):
            with self.subTest(value=value), self.assertRaises(ValidationError):
                validate_draft(json.dumps(value), self.evidence)

    def test_valid_evidence_abstention_has_no_generated_advice(self):
        value = {"decision": "conflicting_evidence", "claims": []}
        self.assertEqual(validate_draft(json.dumps(value), self.evidence),
                         {"status": "abstained", "claims": [], "reason": "conflicting_evidence"})

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

    def test_unquotable_sources_and_context_overflow_are_distinct(self):
        model = FakeGenerator(draft())
        result = self.run_with((hit(text="x" * 601),), model)
        self.assertEqual(result["reason"], "no_usable_quote_spans")
        self.assertEqual(model.calls, [])
        model.config = LocalModelConfig(num_ctx=512, max_output_tokens=100)
        result = self.run_with((hit(),), model)
        self.assertEqual(result["reason"], "context_budget_exceeded")
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
