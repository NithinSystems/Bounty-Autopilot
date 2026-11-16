"""Local opportunity tracker. Statuses are user-reported, not platform verification."""
import argparse, json, sqlite3
from urllib.parse import urlsplit, urlunsplit

STATES = ("discovered","verification_pending","verified","eligibility_approved","selected",
          "in_progress","testing","evidence_ready","awaiting_approval","submitted","under_review",
          "accepted","rejected","payment_pending","paid","cancelled",
          "reviewing","building","ready_for_review","scored","reviewed","approved",
          "rejected_after_submission","payment_confirmed")

def canonical_url(url):
    u=urlsplit(url.strip())
    if u.scheme.lower()!="https" or not u.hostname or u.username or u.password or u.port not in (None,443):
        raise ValueError("Use a public HTTPS opportunity URL without credentials")
    host=u.hostname.lower()
    path=u.path.rstrip("/") or "/"
    if host=="github.com":
        path=path.lower()
    return urlunsplit(("https",host,path,"",""))

def connect(path):
    db=sqlite3.connect(path)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("""CREATE TABLE IF NOT EXISTS opportunities
      (url TEXT PRIMARY KEY, title TEXT NOT NULL, state TEXT NOT NULL,
       reward_note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    db.execute("""CREATE TABLE IF NOT EXISTS tracker_events
      (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT NOT NULL REFERENCES opportunities(url),
       old_state TEXT, new_state TEXT NOT NULL, note TEXT NOT NULL,
       source TEXT NOT NULL DEFAULT 'user', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    db.commit()
    return db

def existing_url(db, canonical):
    # Preserve keys from older databases, including URLs with query strings.
    for (old,) in db.execute("SELECT url FROM opportunities"):
        try:
            if canonical_url(old)==canonical: return old
        except ValueError:
            continue
    return None

def add(db, url, title):
    url=canonical_url(url)
    if not title.strip(): raise ValueError("Title is required")
    with db:
        if existing_url(db,url): return False
        result=db.execute("INSERT OR IGNORE INTO opportunities(url,title,state) VALUES(?,?,?)",(url,title.strip(),"discovered"))
        if result.rowcount:
            db.execute("INSERT INTO tracker_events(url,old_state,new_state,note) VALUES(?,NULL,?,?)",(url,"discovered",""))
    return bool(result.rowcount)

def update(db, url, state, note):
    if state not in STATES: raise ValueError("Unknown state")
    url=canonical_url(url)
    with db:
        url=existing_url(db,url) or url
        existing=db.execute("SELECT state FROM opportunities WHERE url=?",(url,)).fetchone()
        if not existing:return False
        db.execute("UPDATE opportunities SET state=?,reward_note=?,updated_at=CURRENT_TIMESTAMP WHERE url=?",(state,note,url))
        db.execute("INSERT INTO tracker_events(url,old_state,new_state,note) VALUES(?,?,?,?)",(url,existing[0],state,note))
    return True

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database",default="bounty-tracker.sqlite")
    commands=parser.add_subparsers(dest="command",required=True)
    a=commands.add_parser("add");a.add_argument("url");a.add_argument("title")
    u=commands.add_parser("update");u.add_argument("url");u.add_argument("state",choices=STATES);u.add_argument("--note",default="")
    commands.add_parser("list")
    h=commands.add_parser("history");h.add_argument("url")
    args=parser.parse_args()
    with connect(args.database) as db:
        if args.command=="add":print("Added" if add(db,args.url,args.title) else "Already tracked")
        elif args.command=="update":
            if not update(db,args.url,args.state,args.note):parser.error("Opportunity not found")
            print("Updated locally; status is user-reported and not verified.")
        elif args.command=="history":
            for row in db.execute("SELECT old_state,new_state,note,source,created_at FROM tracker_events WHERE url=? ORDER BY id",(existing_url(db,canonical_url(args.url)) or canonical_url(args.url),)):
                print(json.dumps(dict(zip(("old_state","new_state","note","source","created_at"),row)),ensure_ascii=False))
        else:
            for row in db.execute("SELECT url,title,state,reward_note,updated_at FROM opportunities ORDER BY updated_at DESC"):
                print(json.dumps(dict(zip(("url","title","state","note","updated_at"),row)),ensure_ascii=False))
if __name__=="__main__":main()
