"""Local, deterministic candidate assessment; no API calls and no execution authority."""
import datetime as dt, hashlib, json, sqlite3
import github_verify, tracker

def initialize(db):
 db.executescript("""
 CREATE TABLE IF NOT EXISTS assessments
 (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL REFERENCES opportunities(url),
 fingerprint TEXT NOT NULL, created_at TEXT NOT NULL, score INTEGER NOT NULL,
 confidence TEXT NOT NULL, factors_json TEXT NOT NULL, explanation TEXT NOT NULL,
 UNIQUE(url,fingerprint));
 CREATE TABLE IF NOT EXISTS approval_decisions
 (id INTEGER PRIMARY KEY AUTOINCREMENT, event_id TEXT NOT NULL UNIQUE,
 url TEXT NOT NULL REFERENCES opportunities(url), action TEXT NOT NULL,
 decision TEXT NOT NULL, approver TEXT NOT NULL, evidence TEXT NOT NULL,
 created_at TEXT NOT NULL);
 CREATE TABLE IF NOT EXISTS notification_outbox
 (event_id TEXT PRIMARY KEY, url TEXT NOT NULL REFERENCES opportunities(url),
 assessment_id INTEGER NOT NULL REFERENCES assessments(id), payload_json TEXT NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('pending','sent','failed','delivery_uncertain')),
 attempts INTEGER NOT NULL DEFAULT 0, last_error TEXT);
 """)
 db.commit()

def assess(db,url,now=None,threshold=60):
 if not 0<=threshold<=100: raise ValueError("Invalid threshold")
 initialize(db)
 key=tracker.existing_url(db,tracker.canonical_url(url))
 if not key:raise ValueError("Candidate not found")
 v=github_verify.verify(db,key,now)
 checks=v["checks"]
 factors={
  "reward": {"points": 10 if checks["reward"]["advertised"] else 0,"reason":"Advertised amount found; funding unknown" if checks["reward"]["advertised"] else "No explicit advertised amount"},
  "deadline": {"points":0,"reason":"No reliable time estimate; deadline scored neutral"},
  "eligibility":{"points":0,"reason":"Eligibility unknown; not treated as satisfied"},
  "complexity":{"points":0,"reason":"Complexity unknown"},
  "repository_activity":{"points":0,"reason":"Repository activity not measured"},
  "suspicious":{"points":-40 if checks["suspicious"]["value"] else 0,"reason":checks["suspicious"]["reason"]},
  "verification":{"points":10 if v["status"]=="PARTIALLY_VERIFIED" else -50 if v["status"]=="EXPIRED" else 0,"reason":v["reason"]},
 }
 score=max(0,min(100,40+sum(x["points"] for x in factors.values())))
 confidence="low"
 explanation="Deterministic preliminary assessment, not AI. Funding, eligibility, claim and completion time remain unknown."
 stable={"status":v["status"],"checks":checks,"factors":factors,"score":score}
 fingerprint=hashlib.sha256(json.dumps(stable,sort_keys=True).encode()).hexdigest()
 created=(now or dt.datetime.now(dt.timezone.utc)).isoformat()
 with db:
  db.execute("INSERT OR IGNORE INTO assessments(url,fingerprint,created_at,score,confidence,factors_json,explanation) VALUES(?,?,?,?,?,?,?)",(key,fingerprint,created,score,confidence,json.dumps(factors),explanation))
  aid=db.execute("SELECT id FROM assessments WHERE url=? AND fingerprint=?",(key,fingerprint)).fetchone()[0]
  current=db.execute("SELECT state FROM opportunities WHERE url=?",(key,)).fetchone()[0]
  if current=="discovered":
   db.execute("UPDATE opportunities SET state='scored',updated_at=CURRENT_TIMESTAMP WHERE url=?",(key,))
   db.execute("INSERT INTO tracker_events(url,old_state,new_state,note,source) VALUES(?,?,?,?,?)",(key,"discovered","scored","Local deterministic assessment "+str(aid),"assessment"))
  if score>=threshold and v["status"] not in ("EXPIRED","SUSPICIOUS"):
   payload={"url":v["source_url"],"score":score,"confidence":confidence,"reasons":["Advertised reward unverified","Funding and eligibility unknown"]}
   eid=hashlib.sha256(("assessment:"+key+":"+fingerprint).encode()).hexdigest()
   db.execute("INSERT OR IGNORE INTO notification_outbox(event_id,url,assessment_id,payload_json,state) VALUES(?,?,?,?,?)",(eid,key,aid,json.dumps(payload),"pending"))
 return {"assessment_id":aid,"score":score,"confidence":confidence,"factors":factors,"explanation":explanation,"verification":v["status"]}

def decide(db,url,event_id,action,decision,approver,evidence):
 initialize(db)
 key=tracker.existing_url(db,tracker.canonical_url(url))
 if not key or not all(isinstance(x,str) and x.strip() for x in (event_id,action,approver,evidence)):
  raise ValueError("Candidate, event ID, action, approver and evidence are required")
 if decision not in ("approved","rejected"):raise ValueError("Invalid decision")
 with db:
  previous=db.execute("SELECT url,action,decision,approver,evidence FROM approval_decisions WHERE event_id=?",(event_id,)).fetchone()
  expected=(key,action,decision,approver,evidence)
  if previous:
   if previous!=expected:raise ValueError("Event ID conflicts with an earlier decision")
   return False
  db.execute("INSERT INTO approval_decisions(event_id,url,action,decision,approver,evidence,created_at) VALUES(?,?,?,?,?,?,?)",(event_id,key,action,decision,approver,evidence,dt.datetime.now(dt.timezone.utc).isoformat()))
 return True

def record_delivery(db,event_id,outcome):
 if outcome not in ("sent","failed","delivery_uncertain"):raise ValueError("Invalid outcome")
 initialize(db)
 with db:
  row=db.execute("SELECT state FROM notification_outbox WHERE event_id=?",(event_id,)).fetchone()
  if not row:raise ValueError("Unknown notification")
  if row[0]!="pending":return False
  db.execute("UPDATE notification_outbox SET state=?,attempts=attempts+1 WHERE event_id=?",(outcome,event_id))
 return True
