import argparse, hashlib, json
from pathlib import Path

p = argparse.ArgumentParser()
for name in ('output','bounty-id','repository-url','baseline-ref','patched-ref','image','command','baseline-tree','patched-tree'):
    p.add_argument('--'+name, required=True)
for name in ('baseline-code','patched-code','test-count'):
    p.add_argument('--'+name, required=True, type=int)
a = p.parse_args()

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

doc = {
    'schema': 1,
    'collector': 'trusted-github-worker-v1',
    'bounty_id': a.bounty_id,
    'repository_url': a.repository_url,
    'baseline_commit': a.baseline_ref,
    'final_commit': a.patched_ref,
    'command': a.command,
    'image': a.image,
    'baseline': {'exit_code': a.baseline_code, 'test_count': a.test_count,
                 'stdout_sha256': digest('evidence/baseline.stdout.log'),
                 'stderr_sha256': digest('evidence/baseline.stderr.log'),
                 'tree_sha256': a.baseline_tree},
    'patched': {'exit_code': a.patched_code, 'test_count': a.test_count,
                'stdout_sha256': digest('evidence/patched.stdout.log'),
                'stderr_sha256': digest('evidence/patched.stderr.log'),
                'tree_sha256': a.patched_tree},
    'regression_demonstrated': a.baseline_code != 0 and a.patched_code == 0,
    'submission_ready': False,
    'approval_eligible': False,
}
Path(a.output).write_text(json.dumps(doc, indent=2) + '\n', encoding='utf-8')
