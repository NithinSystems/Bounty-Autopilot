"""Local-only Bounty Autopilot store. No keys, model calls, submissions or shell execution."""
import datetime as dt
import html
import json
import re
import sqlite3
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlsplit, parse_qs

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'radar-data'
DATA.mkdir(exist_ok=True)
DB = DATA / 'radar.sqlite'
SOURCES = {'github': 'GitHub bounty label', 'algora-github': 'Algora-linked GitHub issues', 'polar-github': 'Polar-linked GitHub issues', 'superteam': 'Superteam official API', 'hackerone': 'HackerOne program discovery (credential pending)', 'bugcrowd': 'Bugcrowd program discovery (credential/access pending)'}

def now():
    return dt.datetime.now(dt.timezone.utc).isoformat()

class ClosingConnection(sqlite3.Connection):
    def __exit__(self, *args):
        try:
            return super().__exit__(*args)
        finally:
            self.close()

def connect():
    d = sqlite3.connect(DB, timeout=15, factory=ClosingConnection)
    d.row_factory = sqlite3.Row
    d.execute('PRAGMA journal_mode=WAL')
    return d

with connect() as d:
    d.executescript('''
    CREATE TABLE IF NOT EXISTS bounties(
      link TEXT PRIMARY KEY, title TEXT, platform TEXT, reward TEXT, reward_usd REAL,
      deadline TEXT, required_skills TEXT, applicants INTEGER, comments INTEGER,
      found_at TEXT, updated_at TEXT, status TEXT DEFAULT 'found', submitted_date TEXT,
      outcome TEXT, lessons_learned TEXT, brief TEXT, risk_flags TEXT, source TEXT);
    CREATE TABLE IF NOT EXISTS source_state(
      source TEXT PRIMARY KEY, last_attempt REAL DEFAULT 0, last_success TEXT,
      failures INTEGER DEFAULT 0, cooldown REAL DEFAULT 0, etag TEXT, last_error TEXT);
    CREATE TABLE IF NOT EXISTS runs(
      run_id TEXT, source TEXT, at TEXT, status TEXT, received INTEGER, inserted INTEGER,
      updated INTEGER, message TEXT, UNIQUE(run_id,source));
    CREATE TABLE IF NOT EXISTS alerts(at TEXT, source TEXT, message TEXT);
    ''')
    cols={r[1] for r in d.execute('PRAGMA table_info(bounties)')}
    for name in ('source_created_at','source_updated_at'):
        if name not in cols:d.execute('ALTER TABLE bounties ADD COLUMN '+name+' TEXT')
    for s in SOURCES:
        d.execute('INSERT OR IGNORE INTO source_state(source) VALUES(?)', (s,))

def gate(source):
    if source not in SOURCES:
        raise ValueError('Unknown source')
    with connect() as d:
        d.execute('BEGIN IMMEDIATE')
        s = d.execute('SELECT * FROM source_state WHERE source=?', (source,)).fetchone()
        allowed = time.time() >= max(s['last_attempt']+1800, s['cooldown'])
        if allowed:
            d.execute('UPDATE source_state SET last_attempt=? WHERE source=?', (time.time(), source))
        return {'allowed': allowed, 'source': source, 'etag': s['etag'] or '',
                'reason': 'ready' if allowed else '30-minute interval or rate-limit cooldown'}

def infer(issue, source):
    link = str(issue.get('html_url') or '')
    if not re.fullmatch(r'https://github\.com/[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+/issues/\d+', link):
        return None
    if issue.get('pull_request') or issue.get('state') != 'open':
        return None
    try:
        created=dt.datetime.fromisoformat(issue['created_at'].replace('Z','+00:00'))
        age=dt.datetime.now(dt.timezone.utc)-created
        if not dt.timedelta(0)<=age<=dt.timedelta(days=30):return None
    except (KeyError,TypeError,ValueError):return None
    title = str(issue.get('title') or '')[:1000]
    body = str(issue.get('body') or '')[:65000]
    text = unquote(title + '\n' + body)
    algora = bool(re.search(r'https://(?:www\.)?algora\.io/(?:bounties?|claims?)/', text, re.I))
    polar = bool(re.search(r'https://(?:www\.)?polar\.sh/[A-Za-z0-9_.-]+', text, re.I))
    if source == 'algora-github' and not (algora and re.search(r'bounty', text, re.I)):
        return None
    if source == 'polar-github' and not (polar and re.search(r'\bbount(?:y|ies)\b', text, re.I)):
        return None
    labels = [str(x.get('name', '')) for x in issue.get('labels', []) if isinstance(x, dict)]
    amounts = re.findall(r'(?:\$\s*(\d[\d,]*(?:\.\d{1,2})?)|(\d[\d,]*(?:\.\d{1,2})?)\s*(?:USD|USDC|USDT)\b)', text, re.I)
    reward = None
    usd = None
    if amounts:
        vals = sorted(set(float((a or b).replace(',', '')) for a,b in amounts))
        reward = 'Mentioned amounts: ' + ', '.join('$'+format(v, 'g') for v in vals[:5]) + ' (verify bounty terms)'
        # An amount in a brief can be an example, not a payout. Never promote it to confirmed USD.
    else:
        token = re.search(r'(\d+(?:\.\d+)?)\s+(RTC|SOL|ETH|BTC|POINTS)\b', text, re.I)
        if token:
            reward = token.group(0) + ' (token value unverified)'
    deadline = None
    deadline_match = re.search(r'(?:deadline|due date|closes? on)\s*[:\-]?\s*(\d{4}-\d{2}-\d{2})\b', text, re.I)
    if deadline_match:
        try:
            deadline = dt.date.fromisoformat(deadline_match.group(1)).isoformat()
        except ValueError:
            pass
    vocabulary = ['python','typescript','javascript','rust','golang','react','next.js','sql','excel','canva','figma','writing','documentation','research','design','solidity','solana']
    skills = sorted(set([v for v in vocabulary if re.search(r'(?<!\w)'+re.escape(v)+r'(?!\w)', text, re.I)] + labels))
    flags = ['payout and sponsor not independently verified', 'applicant count unknown', 'AI-use policy requires review']
    if not reward:
        flags.append('reward unknown')
    if not deadline:
        flags.append('deadline unknown')
    if re.search(r'\b(upfront fee|registration fee|pay to join|buy tokens|seed phrase|private key)\b', text, re.I):
        flags.append('WARNING: payment or secret-request language; human review required')
    if re.search(r'\b(video|youtube|tiktok|twitter thread|tweet|social media)\b', title, re.I):
        flags.append('possible excluded video/social task')
    if reward and 'token' in reward:
        flags.append('not a confirmed $50-$500 cash reward')
    if polar:
        flags.append('Polar funding link may be legacy or a donation; verify current bounty and payout before work')
    platform = 'Algora-linked / GitHub' if algora else ('Polar-linked / GitHub' if polar else 'GitHub')
    return dict(link=link,title=title,platform=platform,reward=reward,reward_usd=usd,
                deadline=deadline,required_skills=json.dumps(skills),applicants=None,comments=issue.get('comments'),
                brief=body,risk_flags=json.dumps(flags),source=source,source_created_at=issue['created_at'],source_updated_at=issue.get('updated_at'))

def ingest(payload):
    source = payload.get('source')
    if source not in SOURCES:
        raise ValueError('Unknown source')
    run_id = str(payload.get('run_id') or '')[:100]
    if not run_id:
        raise ValueError('run_id required')
    response = payload.get('response') or {}
    code = int(response.get('statusCode', 0))
    headers = {str(k).lower(): v for k,v in (response.get('headers') or {}).items()}
    body = response.get('body') or {}
    if isinstance(body, str):
        try:
            body = json.loads(body)
        except ValueError:
            body = {}
    with connect() as d:
        d.execute('BEGIN IMMEDIATE')
        old = d.execute('SELECT * FROM runs WHERE run_id=? AND source=?', (run_id,source)).fetchone()
        if old:
            return {'replayed': True, **dict(old)}
        inserted = updated = 0
        received = 0
        status = 'ok'
        message = ''
        if code == 304:
            status = 'unchanged'
        elif code != 200 or not isinstance(body, dict) or not isinstance(body.get('items'), list):
            status = 'failed'
            message = 'Source fetch failed or unsupported response schema; HTTP '+str(code)
            state = d.execute('SELECT * FROM source_state WHERE source=?',(source,)).fetchone()
            failures = state['failures']+1
            delay = min(3600,60*2**min(failures,6))
            try:
                if headers.get('retry-after'):
                    delay = max(delay,float(headers['retry-after']))
                if str(headers.get('x-ratelimit-remaining')) == '0':
                    delay = max(delay,float(headers.get('x-ratelimit-reset',0))-time.time()+5)
            except (ValueError,TypeError):
                pass
            d.execute('UPDATE source_state SET failures=?,cooldown=?,last_error=? WHERE source=?',(failures,time.time()+delay,message,source))
            if failures == 3:
                d.execute('INSERT INTO alerts VALUES(?,?,?)',(now(),source,'Source failed 3 consecutive times; delivery integration pending'))
        else:
            for item in body['items'][:100]:
                received += 1
                b = infer(item,source)
                if b is None:
                    continue
                existing = d.execute('SELECT source FROM bounties WHERE link=?',(b['link'],)).fetchone()
                b.update(found_at=now(),updated_at=now())
                if existing:
                    d.execute('UPDATE bounties SET title=:title,platform=:platform,reward=:reward,reward_usd=:reward_usd,deadline=:deadline,required_skills=:required_skills,applicants=:applicants,comments=:comments,updated_at=:updated_at,brief=:brief,risk_flags=:risk_flags,source_created_at=:source_created_at,source_updated_at=:source_updated_at WHERE link=:link',b)
                    updated += 1
                else:
                    cols = ','.join(b)
                    d.execute('INSERT INTO bounties('+cols+') VALUES('+','.join(':'+k for k in b)+')',b)
                    inserted += 1
            if body.get('incomplete_results'):
                message = 'GitHub returned incomplete results; coverage is partial'
        if status != 'failed':
            d.execute('UPDATE source_state SET last_success=?,failures=0,cooldown=0,last_error=NULL,etag=? WHERE source=?',(now(),headers.get('etag'),source))
        d.execute('INSERT INTO runs VALUES(?,?,?,?,?,?,?,?)',(run_id,source,now(),status,received,inserted,updated,message))
        result=dict(run_id=run_id,source=source,status=status,received=received,inserted=inserted,updated=updated,message=message)
    with (DATA/'runs.jsonl').open('a',encoding='utf-8') as f:
        f.write(json.dumps({'at':now(),**result})+'\n')
    return result

def snapshot():
    with connect() as d:
        return {'bounties':[dict(x) for x in d.execute('SELECT link,title,platform,reward,reward_usd,deadline,required_skills,applicants,comments,found_at,status,risk_flags FROM bounties ORDER BY found_at DESC LIMIT 200')],
                'source_state':[dict(x) for x in d.execute('SELECT source,last_success,failures,last_error FROM source_state')],
                'runs':[dict(x) for x in d.execute('SELECT * FROM runs ORDER BY at DESC LIMIT 20')]}

def page():
    s=snapshot()
    rows=''.join('<tr><td><a target="_blank" rel="noopener noreferrer" href="'+html.escape(b['link'],quote=True)+'">'+html.escape(b['title'])+'</a><small>'+html.escape(b['platform'])+'</small></td><td>'+html.escape(b['reward'] or 'Unknown')+'</td><td>'+html.escape(b['deadline'] or 'Unknown')+'</td><td>Applicants: unknown<br>Comments: '+str(b['comments'] if b['comments'] is not None else 'unknown')+'</td><td>'+html.escape(b['status'])+'</td></tr>' for b in s['bounties'])
    states=''.join('<li>'+html.escape(x['source'])+': '+html.escape(x['last_success'] or 'not connected / not run')+'; failures '+str(x['failures'])+'</li>' for x in s['source_state'])
    return '<!doctype html><html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Bounty Radar</title><style>body{font:16px system-ui;background:#f5f6fa;color:#162135;margin:32px auto;max-width:1200px;padding:16px}h1{margin-bottom:6px}table{width:100%;border-collapse:collapse;background:white}td,th{padding:14px;text-align:left;border-bottom:1px solid #ddd}small{display:block;color:#64748b}a{color:#2456b5}.notice{padding:16px;background:#fff2d7;border-radius:10px;margin:20px 0}</style><h1>Bounty Autopilot · Radar</h1><p>Phase 1 · '+str(len(s['bounties']))+' candidates shown · India / Asia Kolkata</p><div class="notice">Candidates are not verified payouts. AI scoring and prep packs are not enabled yet. No submissions, comments, claims or PRs are created. Unknown applicant counts stay unknown.</div><ul>'+states+'</ul><table><thead><tr><th>Bounty</th><th>Reward evidence</th><th>Deadline</th><th>Competition evidence</th><th>Status</th></tr></thead><tbody>'+rows+'</tbody></table><p>Refresh this page after a radar run. Phase 1 shows up to 200 records; all records remain in SQLite.</p></html>'

class Handler(BaseHTTPRequestHandler):
    def log_message(self,*args):
        pass
    def safe(self):
        return self.headers.get('Host') in ('127.0.0.1:8787','localhost:8787') and self.headers.get('Origin') in (None,'http://localhost:8787','http://127.0.0.1:8787')
    def send(self,obj,code=200):
        raw=json.dumps(obj).encode()
        self.send_response(code);self.send_header('Content-Type','application/json');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(raw)
    def do_GET(self):
        if not self.safe():
            return self.send({'error':'Untrusted host or origin'},403)
        path=urlsplit(self.path).path
        if path=='/health':
            return self.send({'ok':True,'phase':1})
        if path=='/api/tracker':
            return self.send(snapshot())
        if path=='/':
            raw=page().encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Content-Security-Policy',"default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'");self.end_headers();return self.wfile.write(raw)
        return self.send({'error':'Not found'},404)
    def do_POST(self):
        if not self.safe() or self.headers.get('Content-Type','').split(';')[0] != 'application/json':
            return self.send({'error':'JSON from trusted local origin required'},403)
        try:
            length=int(self.headers.get('Content-Length',0))
            if not 0 < length <= 8000000:
                return self.send({'error':'Invalid payload size'},413)
            data=json.loads(self.rfile.read(length))
            if self.path=='/radar/gate':
                return self.send(gate(data.get('source')))
            if self.path=='/radar/ingest':
                return self.send(ingest(data))
            return self.send({'error':'Not found'},404)
        except (ValueError,TypeError,KeyError):
            return self.send({'error':'Invalid payload'},400)

if __name__=='__main__':
    print('Bounty Radar store listening on http://127.0.0.1:8787',flush=True)
    ThreadingHTTPServer(('127.0.0.1',8787),Handler).serve_forever()
