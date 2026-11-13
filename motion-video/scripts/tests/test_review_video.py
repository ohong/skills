"""Offline regression tests; all media and budget fixtures live in temporary directories."""
import contextlib
from datetime import date
import importlib.util
import io
import json
import multiprocessing
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

spec=importlib.util.spec_from_file_location('review_video',Path(__file__).resolve().parents[1] / 'review_video.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)

def contender(path, plan, queue):
    try:m.reserve_attempt(Path(path),'1.00',4,plan);queue.put(True)
    except m.ReviewError:queue.put(False)

class ReviewTest(unittest.TestCase):
    def setUp(self):
        class FixedDate(date):
            @classmethod
            def today(cls): return date.fromisoformat(m.RATE_DATE)
        clock = patch.object(m, 'date', FixedDate)
        clock.start(); self.addCleanup(clock.stop)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.video=self.root/'clip.mp4';self.video.write_bytes(b'local-offline-fixture')
        self.args=m.parser().parse_args([str(self.video)])
    def prep(self):return m.prepare(self.args)
    def execution(self):
        self.args.execute=True;self.args.approved_cap_usd='2.00';self.args.budget_ledger=self.root/'budget.json';self.args.output_dir=self.root/'review'
        return self.prep()
    def test_dry_run_never_uses_network(self):
        with patch.object(m,'post',side_effect=AssertionError('NETWORK')),patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),contextlib.redirect_stdout(io.StringIO()) as out:
            self.assertEqual(m.main([str(self.video)]),0)
        self.assertNotIn('fake-secret',out.getvalue());self.assertFalse((self.root/'budget.json').exists())
    def test_payload_and_caps(self):
        plan,payload,count=self.prep();part=payload['contents'][0]['parts'][1]
        self.assertEqual(part['videoMetadata'],{'fps':4});self.assertEqual(part['inlineData']['mimeType'],'video/mp4')
        self.assertEqual(count['generateContentRequest']['contents'],payload['contents'])
        self.assertEqual(plan['maximum_reserved_usd'],'0.342160');self.assertEqual(plan['model'],'gemini-2.5-pro')
        self.assertEqual(payload['generationConfig']['thinkingConfig']['thinkingBudget'],1024)
        self.assertEqual(plan['requested_thinking_budget_advisory'],1024)
        self.assertIn('unverified',plan['compatibility']['eligibility'])
    def test_invalid_input_limits(self):
        for key,value in [('fps',float('nan')),('max_input_tokens',200001),('max_output_tokens',8193),('thinking_budget',127),('max_calls',5)]:
            with self.subTest(key=key):
                old=getattr(self.args,key);setattr(self.args,key,value)
                with self.assertRaises(m.ReviewError):self.prep()
                setattr(self.args,key,old)
    def test_expired_and_partial_rates(self):
        with self.assertRaises(m.ReviewError):m.rates(self.args,date(2027,1,1))
        self.args.input_usd_per_million='2'
        with self.assertRaises(m.ReviewError):m.rates(self.args)
    def test_size_limit_accounts_for_base64(self):
        self.video.write_bytes(b'x'*15_000_000)
        with self.assertRaisesRegex(m.ReviewError,'JSON request'):self.prep()
    def test_ledger_cannot_increase_caps(self):
        plan,_,_=self.prep();p=self.root/'budget.json';m.reserve_attempt(p,'2',2,plan)
        for cap,calls in [('3',2),('2',3)]:
            with self.assertRaises(m.ReviewError):m.reserve_attempt(p,cap,calls,plan)
        self.assertEqual(len(json.loads(p.read_text())['attempts']),1)
    def test_missing_authorization_blocks_transport(self):
        plan,payload,count=self.prep()
        with patch.object(m,'post',side_effect=AssertionError('NETWORK')):
            with self.assertRaises(m.ReviewError):m.execute(self.args,plan,payload,count)
    def test_over_cap_count_never_generates(self):
        args=self.execution()
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',return_value={'totalTokens':200001}) as post:
            with self.assertRaises(m.ReviewError):m.execute(self.args,*args)
        self.assertEqual(post.call_count,1)
        ledger=json.loads(self.args.budget_ledger.read_text());self.assertEqual(ledger['attempts'][0]['reserved_usd'],'0.342160')
    def test_ambiguous_generation_keeps_reservation(self):
        args=self.execution()
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',side_effect=[{'totalTokens':100},m.ReviewError('ambiguous')]) as post:
            with self.assertRaises(m.ReviewError):m.execute(self.args,*args)
        self.assertEqual(post.call_count,2)
        self.assertEqual(json.loads(self.args.budget_ledger.read_text())['attempts'][0]['status'],'failed-or-ambiguous')
    def test_success_preserves_opinion_usage_and_no_base64(self):
        args=self.execution();opinion='Video 1, 00:01.25: cue arrives late.\nConfidence: medium.\n'
        response={'candidates':[{'content':{'parts':[{'text':opinion}]},'finishReason':'STOP'}],
        'usageMetadata':{'promptTokenCount':100,'candidatesTokenCount':50,'thoughtsTokenCount':100,'totalTokenCount':250}}
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',side_effect=[{'totalTokens':100},response]),contextlib.redirect_stdout(io.StringIO()):
            m.execute(self.args,*args)
        self.assertEqual((self.args.output_dir/'opinion.txt').read_text(),opinion)
        self.assertEqual(json.loads((self.args.output_dir/'response.json').read_text())['usageMetadata'],response['usageMetadata'])
        saved=''.join(p.read_text() for p in self.args.output_dir.glob('*'))
        self.assertNotIn('fake-secret',saved);self.assertNotIn('inlineData',saved)
    def generated_response(self, output_tokens, thinking_tokens, finish_reason='STOP'):
        return {'candidates':[{'content':{'parts':[{'text':'Exact model opinion.\n'}]},'finishReason':finish_reason}],
                'usageMetadata':{'promptTokenCount':100,'candidatesTokenCount':output_tokens,
                                 'thoughtsTokenCount':thinking_tokens,'totalTokenCount':100+output_tokens+thinking_tokens}}
    def assert_preserved(self, response, status):
        report=json.loads((self.args.output_dir/'response.json').read_text())
        self.assertEqual(report['usageMetadata'],response['usageMetadata'])
        self.assertEqual((self.args.output_dir/'opinion.txt').read_text(),'Exact model opinion.\n')
        attempt=json.loads(self.args.budget_ledger.read_text())['attempts'][0]
        self.assertEqual(attempt['reserved_usd'],'0.342160')
        self.assertEqual(attempt['status'],status)
    def test_advisory_thinking_overflow_fits_combined_boundary(self):
        args=self.execution();response=self.generated_response(6144,2048)
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',side_effect=[{'totalTokens':100},response]),contextlib.redirect_stdout(io.StringIO()):
            m.execute(self.args,*args)
        self.assert_preserved(response,'complete')
    def test_combined_output_overflow_preserves_evidence(self):
        args=self.execution();response=self.generated_response(6145,2048)
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',side_effect=[{'totalTokens':100},response]):
            with self.assertRaisesRegex(m.ReviewError,'combined response output and thinking'):
                m.execute(self.args,*args)
        self.assert_preserved(response,'failed-or-ambiguous')
    def test_truncated_response_preserves_evidence(self):
        args=self.execution();response=self.generated_response(6144,2048,'MAX_TOKENS')
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',side_effect=[{'totalTokens':100},response]):
            with self.assertRaisesRegex(m.ReviewError,'truncated'):m.execute(self.args,*args)
        self.assert_preserved(response,'failed-or-ambiguous')
    def test_invalid_usage_preserves_evidence(self):
        args=self.execution();response=self.generated_response(20,10);response['usageMetadata']='invalid usage schema'
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',side_effect=[{'totalTokens':100},response]):
            with self.assertRaisesRegex(m.ReviewError,'Invalid usage response schema'):m.execute(self.args,*args)
        self.assert_preserved(response,'failed-or-ambiguous')
    def test_bad_response_schema_keeps_reservation(self):
        args=self.execution()
        with patch.dict(m.os.environ,{'GEMINI_API_KEY':'fake-secret'}),patch.object(m,'post',side_effect=[{'totalTokens':100},{'candidates':[{'content':[] }]}]):
            with self.assertRaises(m.ReviewError):m.execute(self.args,*args)
        self.assertEqual(len(json.loads(self.args.budget_ledger.read_text())['attempts']),1)
    def test_concurrent_reservations_obey_shared_cap(self):
        plan,_,_=self.prep();ctx=multiprocessing.get_context('fork');q=ctx.Queue();path=self.root/'shared.json'
        workers=[ctx.Process(target=contender,args=(str(path),plan,q)) for _ in range(8)]
        for p in workers:p.start()
        for p in workers:p.join(10);self.assertEqual(p.exitcode,0)
        outcomes=[q.get(timeout=1) for _ in workers];self.assertEqual(sum(outcomes),2)
        ledger=json.loads(path.read_text());self.assertEqual(len(ledger['attempts']),2)
    def test_transport_header_and_redirect_policy(self):
        class Response:
            def __enter__(self):return self
            def __exit__(self,*args):pass
            def read(self,n):return b'{"totalTokens":100}'
        with patch.object(m.urllib.request,'build_opener') as build:
            build.return_value.open.return_value=Response()
            self.assertEqual(m.post('countTokens',{},'fake-secret'),{'totalTokens':100})
            request=build.return_value.open.call_args.args[0]
            self.assertNotIn('fake-secret',request.full_url)
            self.assertEqual(request.get_header('X-goog-api-key'),'fake-secret')
        self.assertIsNone(m.NoRedirect().redirect_request(None,None,302,None,None,'https://example.com'))

if __name__=='__main__':unittest.main(verbosity=2)
