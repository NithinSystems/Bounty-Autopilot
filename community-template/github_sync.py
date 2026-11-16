"""Read-only GitHub bounty discovery and tracker import."""
import argparse, datetime as dt, json, os, re, urllib.error, urllib.parse, urllib.request
import tracker

API="https://api.github.com/search/issues"
ISSUE=re.compile(r"^https://github\.com/([A-Za-z0-9_.-]+)/([A-Za-z0-9_.-]+)/issues/([1-9][0-9]*)$",re.I)
AMOUNT=re.compile(r"(?:bounty|reward)\s*[:=-]\s*(\$\s*\d[\d,]*(?:\.\d{1,2})?)",re.I)

class DiscoveryError(Exception): pass
class RateLimited(DiscoveryError): pass

def initialize(db):
 db.execute("""CREATE TABLE IF NOT EXISTS github_discovery
 (url TEXT PRIMARY KEY REFERENCES opportunities(url), repository TEXT NOT NULL,
 issue_number INTEGER NOT NULL, source_url TEXT NOT NULL, discovered_at TEXT NOT NULL,
 observed_at TEXT NOT NULL, source_updated_at TEXT, issue_state TEXT,
 advertised_reward TEXT, reward_evidence TEXT, body TEXT NOT NULL)""")
 db.commit()

def parse_issue(item):
 if not isinstance(item,dict) or "pull_request" in item: return None
 raw=item.get("html_url")
 if not isinstance(raw,str): return None
 try: url=tracker.canonical_url(raw)
 except ValueError: return None
 match=ISSUE.fullmatch(url)
 if not match or item.get("state") not in ("open","closed"): return None
 title=item.get("title")
 if not isinstance(title,str) or not title.strip(): return None
 body=item.get("body") if isinstance(item.get("body"),str) else ""
 reward=AMOUNT.search(body)
 return {"url":url,"title":title[:1000],"repository":match.group(1)+"/"+match.group(2),
         "issue_number":int(match.group(3)),"state":item["state"],"body":body[:65000],
         "updated_at":item.get("updated_at") if isinstance(item.get("updated_at"),str) else None,
         "reward":reward.group(1) if reward else None,
         "reward_evidence":reward.group(0) if reward else None}

def import_issues(db,items,observed_at=None):
 initialize(db); now=observed_at or dt.datetime.now(dt.timezone.utc).isoformat()
 inserted=updated=skipped=0
 for item in items:
  issue=parse_issue(item)
  if not issue: skipped+=1;continue
  created=tracker.add(db,issue["url"],issue["title"])
  stored=tracker.existing_url(db,issue["url"]) or issue["url"]
  with db:
   db.execute("""INSERT INTO github_discovery
   (url,repository,issue_number,source_url,discovered_at,observed_at,source_updated_at,issue_state,advertised_reward,reward_evidence,body)
   VALUES(?,?,?,?,?,?,?,?,?,?,?)
   ON CONFLICT(url) DO UPDATE SET observed_at=excluded.observed_at,source_updated_at=excluded.source_updated_at,
   issue_state=excluded.issue_state,advertised_reward=excluded.advertised_reward,reward_evidence=excluded.reward_evidence,body=excluded.body""",
   (stored,issue["repository"],issue["issue_number"],issue["url"],now,now,issue["updated_at"],issue["state"],issue["reward"],issue["reward_evidence"],issue["body"]))
  if created:inserted+=1
  else:updated+=1
 return {"inserted":inserted,"updated":updated,"skipped":skipped}

def fetch_page(page,token=None,opener=urllib.request.urlopen):
 if not 1<=page<=10: raise ValueError("Page must be between 1 and 10")
 query=urllib.parse.urlencode({"q":"is:issue is:open label:bounty","sort":"updated","order":"desc","per_page":100,"page":page})
 headers={"Accept":"application/vnd.github+json","User-Agent":"NithinSystems-Bounty-Autopilot"}
 if token: headers["Authorization"]="Bearer "+token
 request=urllib.request.Request(API+"?"+query,headers=headers)
 try:
  with opener(request,timeout=20) as response:
   data=json.load(response)
 except urllib.error.HTTPError as exc:
  if exc.code==429 or (exc.code==403 and exc.headers.get("X-RateLimit-Remaining")=="0"):
   raise RateLimited("GitHub rate limit reached; retry after the reset time") from None
  raise DiscoveryError("GitHub HTTP error "+str(exc.code)) from None
 except (urllib.error.URLError,TimeoutError,OSError,ValueError):
  raise DiscoveryError("GitHub unavailable or returned invalid JSON") from None
 if not isinstance(data,dict) or not isinstance(data.get("items"),list):
  raise DiscoveryError("Unexpected GitHub response")
 return data["items"]

def sync(db,max_pages=1,token=None,fetcher=fetch_page):
 if not 1<=max_pages<=10: raise ValueError("max_pages must be 1–10")
 total={"inserted":0,"updated":0,"skipped":0,"pages":0}
 for page in range(1,max_pages+1):
  items=fetcher(page,token)
  stats=import_issues(db,items)
  for k in ("inserted","updated","skipped"): total[k]+=stats[k]
  total["pages"]+=1
  if len(items)<100: break
 return total

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--database",default="bounty-tracker.sqlite")
 p.add_argument("--pages",type=int,default=1)
 args=p.parse_args()
 try:
  with tracker.connect(args.database) as db: print(json.dumps(sync(db,args.pages,os.getenv("GITHUB_TOKEN"))))
 except (DiscoveryError,ValueError) as exc: p.exit(1,str(exc)+"\n")
if __name__=="__main__": main()
