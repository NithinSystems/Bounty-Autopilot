import json, subprocess, tempfile, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VALIDATOR = ROOT / 'scripts' / 'validate-evidence.py'

def valid_doc():
    run = {'exit_code': 1, 'test_count': 1, 'stdout_sha256':'a'*64,
           'stderr_sha256':'b'*64, 'tree_sha256':'c'*64}
    return {'collector':'trusted-github-worker-v1','baseline_commit':'1'*40,
            'final_commit':'2'*40,'command':'python -m unittest discover',
            'baseline':run,'patched':{**run,'exit_code':0},
            'submission_ready':False,'approval_eligible':False}

class EvidenceTests(unittest.TestCase):
    def check(self, doc):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'evidence.json'; path.write_text(json.dumps(doc))
            return subprocess.run(['python3',str(VALIDATOR),str(path)],capture_output=True,text=True)
    def test_valid(self): self.assertEqual(self.check(valid_doc()).returncode,0)
    def test_empty_suite_blocked(self):
        d=valid_doc(); d['baseline']['test_count']=d['patched']['test_count']=0
        self.assertNotEqual(self.check(d).returncode,0)
    def test_passing_baseline_blocked(self):
        d=valid_doc(); d['baseline']['exit_code']=0
        self.assertNotEqual(self.check(d).returncode,0)
    def test_failed_patch_blocked(self):
        d=valid_doc(); d['patched']['exit_code']=1
        self.assertNotEqual(self.check(d).returncode,0)
    def test_approval_forgery_blocked(self):
        d=valid_doc(); d['approval_eligible']=True
        self.assertNotEqual(self.check(d).returncode,0)

if __name__ == '__main__': unittest.main()
