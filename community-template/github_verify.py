"""Conservative verification of a stored GitHub discovery observation."""
import datetime as dt, json, re
import github_sync

DEADLINE=re.compile(r"\b(?:deadline|due date|closes on)\s*[:=-]?\s*(\d{4}-\d{2}-\d{2})\b",re.I)
RISK=re.compile(r"\b(?:pay (?:an? )?(?:fee|deposit)|send (?:a )?deposit|share (?:your )?private key)\b",re.I)

def verify(db,url,now=None):
 github_sync.initialize(db)
 key=github_sync.tracker.existing_url(db,github_sync.tracker.canonical_url(url))
 row=db.execute("SELECT source_url,observed_at,issue_state,advertised_reward,reward_evidence,body FROM github_discovery WHERE url=?",(key,)).fetchone()
 if not row:raise ValueError("No GitHub discovery observation")
 source,observed,state,reward,quote,body=row
 checked=now or dt.datetime.now(dt.timezone.utc)
 match=DEADLINE.search(body)
 deadline=None
 if match:
  try:deadline=dt.date.fromisoformat(match.group(1))
  except ValueError:pass
 suspicious=bool(RISK.search(body))
 expired=state=="closed" or (deadline is not None and deadline<checked.date())
 status="SUSPICIOUS" if suspicious else "EXPIRED" if expired else "PARTIALLY_VERIFIED" if state=="open" else "UNVERIFIED"
 checks={"open":{"value":state=="open","observed_at":observed,"source_url":source},
         "deadline":{"value":deadline.isoformat() if deadline else None,"source_url":source},
         "reward":{"advertised":reward,"quote":quote,"funded":"unknown","source_url":source},
         "eligibility":{"value":"unknown","reason":"No authoritative user-specific eligibility evidence"},
         "claim":{"value":"unknown","reason":"Claim status not established"},
         "suspicious":{"value":suspicious,"reason":"Potential fee, deposit, or private-key request" if suspicious else "No matching phrase; other risks may exist"}}
 result={"status":status,"checked_at":checked.isoformat(),"source_url":source,"checks":checks,
         "reason":"Based on stored GitHub observation; funding, claim and eligibility remain unverified."}
 db.execute("""CREATE TABLE IF NOT EXISTS github_verifications
 (id INTEGER PRIMARY KEY AUTOINCREMENT,url TEXT NOT NULL REFERENCES opportunities(url),
 checked_at TEXT NOT NULL,status TEXT NOT NULL,evidence_json TEXT NOT NULL)""")
 with db:db.execute("INSERT INTO github_verifications(url,checked_at,status,evidence_json) VALUES(?,?,?,?)",(key,result["checked_at"],status,json.dumps(result)))
 return result
