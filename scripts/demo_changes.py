#!/usr/bin/env python3
"""Record real local snapshot/access changes in an isolated scratch index."""

import argparse
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import shutil
import sys
from tempfile import TemporaryDirectory
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from versionlens.api import ApiNotFound, ApiService
from versionlens.ingest import Corpus, load_demo_corpus
from versionlens.models import ValidationError
from versionlens.store import replace_corpus
from versionlens.updates import delete_snapshot, sync_snapshot
from versionlens.vector_store import VectorIndexError, build_vector_index


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT/'reports/local/day5-changes.json')
    parser.add_argument('--generate', action='store_true', help='Call only the configured free local model')
    parser.add_argument('--vectors', action='store_true', help='Build real local embeddings and probe all retrievers')
    args = parser.parse_args()
    if args.output.exists():
        parser.error('Choose a new report path; existing observations are preserved.')
    steps = []

    def record(name, operation):
        started = perf_counter()
        result = operation()
        steps.append({'case_id': name, 'latency_ms': round((perf_counter()-started)*1000,3), 'result': result})
        print(json.dumps({'case_id':name,'status':result.get('status',result.get('operation','recorded'))}), flush=True)
        return result

    def missing(operation):
        try:
            operation()
        except ApiNotFound:
            return {'status': 'not_found', 'equivalent_http_status': 404}
        raise AssertionError('Restricted or obsolete source was unexpectedly returned')

    with TemporaryDirectory(prefix='versionlens-changes-') as temporary:
        work = Path(temporary)
        shutil.copytree(ROOT/'data/corpus', work/'data/corpus')
        shutil.copytree(ROOT/'data/synthetic', work/'data/synthetic')
        shutil.copyfile(ROOT/'data/sources.json', work/'data/sources.json')
        index, vectors = work/'source.sqlite3', work/'vectors.sqlite3'
        corpus = load_demo_corpus(work)
        record('initial_ingestion', lambda: replace_corpus(index, corpus))
        public, support = ApiService(index,vectors), ApiService(index,vectors,'support')
        record('public_catalog', public.catalog)
        record('support_catalog', support.catalog)
        if args.vectors:
            record('real_vector_build', lambda: build_vector_index(index,vectors))
        for method in (('keyword','vector','hybrid') if args.vectors else ('keyword',)):
            for profile, service in (('public',public),('support',support)):
                result = record(profile+'_'+method, lambda service=service,method=method: service.search({'question':'orchidrelay','version':'0.28.1','retriever':method}))
                assert all(hit['access']=='public' or profile=='support' for hit in result['hits'])
                if profile=='public': assert all(hit['source_kind']!='synthetic' for hit in result['hits'])
        allowed = support.search({'question':'orchidrelay','version':'0.28.1'})['hits'][0]
        record('support_source',lambda:support.chunk(allowed['chunk_id'],'0.28.1'))
        record('public_source_denied',lambda:missing(lambda:public.chunk(allowed['chunk_id'],'0.28.1')))
        denied = record('public_missing_answer',lambda:public.ask({'question':'orchidrelay','version':'0.28.1'}))
        assert denied['status']=='abstained' and denied['model_called'] is False
        if args.generate:
            for version in ('0.27.2','0.28.1'):
                record('support_draft_'+version,lambda version=version:support.ask({'question':'orchidrelay','version':version}))

        manifest_path = work/'data/synthetic/sources.json'
        manifest = json.loads(manifest_path.read_text())
        selected = next(source for source in manifest['sources'] if source['version']=='0.28.1')
        document_path = work/selected['path']
        document = document_path.read_text().replace('3 attempts','4 attempts')
        assert document != document_path.read_text()
        digest = sha256(document.encode()).hexdigest()
        document_path.write_text(document)
        selected.update(sha256=digest,commit=digest,url=selected['url'].split('?')[0]+'?sha256='+digest)
        manifest_path.write_text(json.dumps(manifest))

        def synchronize():
            fresh = load_demo_corpus(work)  # Recheck actual bytes and manifest before every write.
            snapshot = Corpus(tuple(source for source in fresh.sources if source.version=='0.28.1'),
                              tuple(chunk for chunk in fresh.chunks if chunk.source.version=='0.28.1'))
            return sync_snapshot(index,snapshot,'0.28.1')

        changed = record('update_document_revision',synchronize)
        assert changed['updated']==1 and changed['unchanged']==16
        revised = record('updated_support_evidence',lambda:support.search({'question':'orchidrelay','version':'0.28.1'}))
        assert '4 attempts' in revised['hits'][0]['text'] and revised['hits'][0]['chunk_id']!=allowed['chunk_id']
        previous = record('other_version_unchanged',lambda:support.search({'question':'orchidrelay','version':'0.27.2'}))
        assert '2 attempts' in previous['hits'][0]['text']
        record('old_revision_source_removed',lambda:missing(lambda:support.chunk(allowed['chunk_id'],'0.28.1')))
        if args.vectors:
            def stale_cache():
                try:
                    support.search({'question':'orchidrelay','version':'0.28.1','retriever':'vector'})
                except VectorIndexError:
                    return {'status':'rejected','reason':'stale_vector_cache','automatic_fallback':False}
                raise AssertionError('A stale vector index was accepted')
            record('changed_corpus_rejects_old_vectors',stale_cache)
        if args.generate:
            record('revised_support_draft',lambda:support.ask({'question':'orchidrelay','version':'0.28.1'}))

        selected['access']='public'
        manifest_path.write_text(json.dumps(manifest))
        record('grant_public_demo_access',synchronize)
        visible = record('newly_public_evidence',lambda:public.search({'question':'orchidrelay','version':'0.28.1'}))
        assert visible['hits'] and visible['hits'][0]['access']=='public'
        if args.generate:
            record('newly_public_draft',lambda:public.ask({'question':'orchidrelay','version':'0.28.1'}))
        selected['access']='support'
        manifest_path.write_text(json.dumps(manifest))
        record('revoke_public_demo_access',synchronize)
        revoked = record('revoked_public_answer',lambda:public.ask({'question':'orchidrelay','version':'0.28.1'}))
        assert revoked['status']=='abstained' and revoked['model_called'] is False
        record('previously_known_id_denied',lambda:missing(lambda:public.chunk(visible['hits'][0]['chunk_id'],'0.28.1')))
        deletion = record('delete_selected_snapshot',lambda:delete_snapshot(index,'0.28.1'))
        assert deletion['index']['versions']==['0.27.2'] and deletion['deleted']==17
        record('remaining_version_still_available',lambda:support.search({'question':'orchidrelay','version':'0.27.2'}))

    report = {'kind':'local_synthetic_update_and_permission_demo','recorded_at_utc':datetime.now(timezone.utc).isoformat(),
              'synthetic_documents':True,'isolated_scratch_index':True,'real_local_generation':args.generate,
              'real_local_embeddings':args.vectors,'api_fee_usd':0,'human_reviewed':False,'held_out_benchmark':False,
              'semantic_support_verified':False,'steps':steps,
              'implementation_sha256':{str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in sorted((ROOT/'src/versionlens').glob('*.py'))},
              'script_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
              'limitations':['Profiles simulate permissions; this is not production authentication.',
                             'Synthetic facts are fictional, not HTTPX guidance.',
                             'Generated outcomes are retained as observed; no answer-accuracy or entailment score is inferred.',
                             'Fixed-order repeated development probes include model loading and swapping.']}
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('x') as output:
        json.dump(report,output,indent=2,ensure_ascii=False,allow_nan=False)
        output.write('\n')
    return 0


if __name__=='__main__':
    raise SystemExit(main())
