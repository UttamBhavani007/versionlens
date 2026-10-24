from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict
from hashlib import sha256
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from test_models import example_source
from versionlens.cli import main
from versionlens.ingest import load_corpus, load_demo_corpus
from versionlens.models import ValidationError
from versionlens.store import index_stats


class SyntheticIngestionAndCliTests(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.index = self.root / 'data/versionlens.sqlite3'
        upstream = []
        for version in ('0.27.2', '0.28.1'):
            text = '# Public\nPublic timeout guidance.\n'
            source = example_source(version, text)
            target = self.root / source.path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text)
            upstream.append(asdict(source))
        (self.root / 'data/sources.json').write_text(json.dumps({'schema_version': 1, 'sources': upstream}))
        project = Path(__file__).resolve().parents[1]
        manifest = json.loads((project / 'data/synthetic/sources.json').read_text())
        for source in manifest['sources']:
            target = self.root / source['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((project / source['path']).read_bytes())
        self.demo_manifest = self.root / 'data/synthetic/sources.json'
        self.demo_manifest.write_text(json.dumps(manifest))

    def cli(self, *arguments):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = main(['--root', str(self.root), *arguments])
        return code, json.loads(output.getvalue() or errors.getvalue())

    def test_default_ingestion_excludes_synthetic_documents(self):
        self.assertEqual(len(load_corpus(self.root).sources), 2)
        self.assertEqual(self.cli('ingest')[1]['sources'], 2)
        self.assertEqual(self.cli('search', 'orchidrelay', '--version', '0.28.1', '--demo-profile', 'support')[1]['hits'], [])

    def test_separate_manifest_requires_explicit_synthetic_opt_in(self):
        with self.assertRaises(ValidationError):
            load_corpus(self.root, 'data/synthetic/sources.json')
        corpus = load_demo_corpus(self.root)
        self.assertEqual(len(corpus.sources), 4)
        self.assertEqual(sum(source.source_kind == 'synthetic' for source in corpus.sources), 2)

    def test_checksum_failure_prevents_partial_reingestion(self):
        self.cli('ingest', '--include-synthetic')
        before = index_stats(self.index)
        source = json.loads(self.demo_manifest.read_text())['sources'][0]
        (self.root / source['path']).write_text('Altered bytes without updating metadata.')
        code, result = self.cli('ingest', '--include-synthetic')
        self.assertEqual(code, 2)
        self.assertIn('Checksum mismatch', result['error'])
        self.assertEqual(index_stats(self.index), before)

    def test_digest_valid_document_still_requires_prominent_synthetic_label(self):
        manifest = json.loads(self.demo_manifest.read_text())
        source = manifest['sources'][0]
        content = 'This fictional document lacks the required visible heading.\n'
        digest = sha256(content.encode()).hexdigest()
        source.update(sha256=digest, commit=digest, url=source['url'].split('?')[0]+'?sha256='+digest)
        (self.root / source['path']).write_text(content)
        self.demo_manifest.write_text(json.dumps(manifest))
        with self.assertRaisesRegex(ValidationError, 'SYNTHETIC DEMO'):
            load_demo_corpus(self.root)

    def test_cli_profile_changes_evidence_without_changing_the_corpus(self):
        self.assertEqual(self.cli('ingest', '--include-synthetic')[0], 0)
        public = self.cli('search', 'orchidrelay', '--version', '0.28.1')[1]
        support = self.cli('search', 'orchidrelay', '--version', '0.28.1', '--demo-profile', 'support')[1]
        self.assertEqual(public['hits'], [])
        self.assertTrue(support['hits'])
        self.assertEqual(support['hits'][0]['source_kind'], 'synthetic')
        self.assertTrue(support['hits'][0]['citation_url'].startswith('/api/chunks/'))
        self.assertEqual(self.cli('stats')[1]['sources'], 2)
        self.assertEqual(self.cli('stats', '--demo-profile', 'support')[1]['sources'], 4)

    def test_sync_without_opt_in_deletes_only_selected_versions_synthetic_source(self):
        self.cli('ingest', '--include-synthetic')
        code, result = self.cli('sync', '--version', '0.28.1')
        self.assertEqual(code, 0)
        self.assertEqual(result['deleted'], 1)
        self.assertEqual(result['unchanged'], 1)
        self.assertEqual(self.cli('search', 'orchidrelay', '--version', '0.28.1', '--demo-profile', 'support')[1]['hits'], [])
        self.assertTrue(self.cli('search', 'orchidrelay', '--version', '0.27.2', '--demo-profile', 'support')[1]['hits'])

    def test_metadata_only_policy_sync_changes_public_visibility(self):
        self.cli('ingest', '--include-synthetic')
        manifest = json.loads(self.demo_manifest.read_text())
        next(source for source in manifest['sources'] if source['version'] == '0.28.1')['access'] = 'public'
        self.demo_manifest.write_text(json.dumps(manifest))
        code, result = self.cli('sync', '--version', '0.28.1', '--include-synthetic')
        self.assertEqual(code, 0)
        self.assertEqual(result['updated'], 1)
        self.assertTrue(self.cli('search', 'orchidrelay', '--version', '0.28.1')[1]['hits'])
        self.assertEqual(self.cli('search', 'orchidrelay', '--version', '0.27.2')[1]['hits'], [])

    def test_explicit_delete_snapshot_keeps_the_other_version(self):
        self.cli('ingest', '--include-synthetic')
        code, result = self.cli('delete-snapshot', '--version', '0.28.1')
        self.assertEqual(code, 0)
        self.assertEqual(result['deleted'], 2)
        self.assertEqual(result['index']['versions'], ['0.27.2'])


if __name__ == '__main__':
    unittest.main()
