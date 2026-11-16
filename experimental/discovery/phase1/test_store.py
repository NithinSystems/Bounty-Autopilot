import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

class StoreTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        p=Path(self.temp.name)/'phase1';p.mkdir()
        shutil.copy(Path(__file__).with_name('radar_store.py'),p/'radar_store.py')
        spec=importlib.util.spec_from_file_location('test_store_module',p/'radar_store.py')
        self.s=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.s)
    def tearDown(self):
        self.temp.cleanup()
    def item(self):
        return {'created_at':self.s.now(),'html_url':'https://github.com/example/repo/issues/123','state':'open','title':'<script>fix()</script> Python docs bounty','body':'Reward: $100. Deadline: 2026-11-01','labels':[{'name':'bounty'}],'comments':25}
    def post(self,run_id='one'):
        return self.s.ingest({'source':'github','run_id':run_id,'response':{'statusCode':200,'body':{'items':[self.item()]},'headers':{}}})
    def test_replay_and_cross_run_dedup(self):
        self.assertEqual(self.post()['inserted'],1)
        self.assertTrue(self.post()['replayed'])
        self.assertEqual(self.post('two')['inserted'],0)
        self.assertEqual(len(self.s.snapshot()['bounties']),1)
    def test_unknowns_and_html(self):
        self.post();b=self.s.snapshot()['bounties'][0]
        self.assertIsNone(b['applicants']);self.assertIsNone(b['reward_usd'])
        self.assertEqual(b['comments'],25)
        self.assertNotIn('<script>',self.s.page())
        self.assertEqual(b['deadline'],'2026-11-01')
    def test_invalid_amount_does_not_break_ingestion(self):
        item = self.item()
        item['body'] = 'Reward: $,,, and ,,, USD. Verify before relying on this.'
        result = self.s.infer(item, 'github')
        self.assertIsNotNone(result)
        self.assertIsNone(result['reward'])
    def test_rate_gate(self):
        self.assertTrue(self.s.gate('github')['allowed'])
        self.assertFalse(self.s.gate('github')['allowed'])
    def test_failures_and_cooldown(self):
        for i in range(3):
            self.s.ingest({'source':'github','run_id':str(i),'response':{'statusCode':429,'headers':{'retry-after':'7200'}}})
        self.assertFalse(self.s.gate('github')['allowed'])
        with self.s.connect() as d:
            self.assertEqual(d.execute('SELECT COUNT(*) FROM alerts').fetchone()[0],1)
    def test_algora_false_positive(self):
        i=self.item();i['body']='An icon for https://algora.io'
        self.assertIsNone(self.s.infer(i,'algora-github'))
    def test_preserves_status(self):
        self.post()
        with self.s.connect() as d:
            d.execute("UPDATE bounties SET status='submitted',lessons_learned='keep me'")
        self.post('two')
        with self.s.connect() as d:
            b=d.execute('SELECT status,lessons_learned FROM bounties').fetchone()
            self.assertEqual(tuple(b),('submitted','keep me'))
    def test_polar_donations_are_not_bounties(self):
        i=self.item();i['title']='Please support this project';i['body']='Donate at https://polar.sh/example/repo'
        self.assertIsNone(self.s.infer(i,'polar-github'))
        i['body']='Bounty: $100 https://polar.sh/example/repo'
        b=self.s.infer(i,'polar-github')
        self.assertEqual(b['platform'],'Polar-linked / GitHub')
        self.assertIsNone(b['reward_usd'])
        self.assertIn('legacy',b['risk_flags'])

if __name__=='__main__':
    unittest.main()
