"""Local manual opportunity tracker. Does not contact external platforms."""
import argparse, json, sqlite3
from pathlib import Path
from urllib.parse import urlsplit

STATES = ("discovered", "reviewing", "building", "ready_for_review", "submitted", "accepted", "rejected", "paid")

def connect(path):
    db=sqlite3.connect(path)
    db.execute("""CREATE TABLE IF NOT EXISTS opportunities
      (url TEXT PRIMARY KEY, title TEXT NOT NULL, state TEXT NOT NULL,
       reward_note TEXT NOT NULL DEFAULT '', updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)""")
    return db

def add(db, url, title):
    u=urlsplit(url)
    if u.scheme != "https" or not u.hostname or u.username or u.password:
        raise ValueError("Use a public HTTPS opportunity URL without credentials")
    if not title.strip():
        raise ValueError("Title is required")
    result=db.execute("INSERT OR IGNORE INTO opportunities(url,title,state) VALUES(?,?,?)",(url,title.strip(),"discovered"))
    db.commit()
    return bool(result.rowcount)

def update(db, url, state, note):
    if state not in STATES:
        raise ValueError("Unknown state")
    result=db.execute("UPDATE opportunities SET state=?, reward_note=?, updated_at=CURRENT_TIMESTAMP WHERE url=?",(state,note,url))
    db.commit()
    return bool(result.rowcount)

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", default="bounty-tracker.sqlite")
    commands=parser.add_subparsers(dest="command",required=True)
    a=commands.add_parser("add");a.add_argument("url");a.add_argument("title")
    u=commands.add_parser("update");u.add_argument("url");u.add_argument("state",choices=STATES);u.add_argument("--note",default="")
    commands.add_parser("list")
    args=parser.parse_args()
    with connect(args.database) as db:
        if args.command=="add": print("Added" if add(db,args.url,args.title) else "Already tracked")
        elif args.command=="update":
            if not update(db,args.url,args.state,args.note): parser.error("Opportunity not found")
            print("Updated locally; status is user-reported and not verified.")
        else:
            for url,title,state,note,updated in db.execute("SELECT url,title,state,reward_note,updated_at FROM opportunities ORDER BY updated_at DESC"):
                print(json.dumps({"url":url,"title":title,"state":state,"note":note,"updated_at":updated},ensure_ascii=False))
if __name__=="__main__": main()
