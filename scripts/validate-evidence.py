import json, re, sys
from pathlib import Path

def blocked(message):
    raise SystemExit('BLOCKED: ' + message)

doc = json.loads(Path(sys.argv[1]).read_text(encoding='utf-8'))
if doc.get('collector') != 'trusted-github-worker-v1': blocked('untrusted collector')
if not re.fullmatch(r'[0-9a-f]{40}', doc.get('baseline_commit','')): blocked('invalid baseline commit')
if not re.fullmatch(r'[0-9a-f]{40}', doc.get('final_commit','')): blocked('invalid final commit')
if doc['baseline_commit'] == doc['final_commit']: blocked('refs are identical')
if doc.get('command') != 'python -m unittest discover': blocked('unexpected command')
b, p = doc.get('baseline',{}), doc.get('patched',{})
if b.get('exit_code') == 0: blocked('baseline does not reproduce failure')
if p.get('exit_code') != 0: blocked('patched run does not pass')
if not isinstance(b.get('test_count'), int) or b['test_count'] < 1: blocked('empty baseline suite')
if b.get('test_count') != p.get('test_count'): blocked('test counts differ')
for run in (b,p):
    for key in ('stdout_sha256','stderr_sha256','tree_sha256'):
        if not re.fullmatch(r'[0-9a-f]{64}', run.get(key,'')): blocked('invalid '+key)
if doc.get('submission_ready') is not False or doc.get('approval_eligible') is not False:
    blocked('collector cannot approve submission')
print('Evidence valid; human review and separate submission approval still required.')
