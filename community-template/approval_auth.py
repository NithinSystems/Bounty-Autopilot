"""Local passphrase-gated decision recording; not a remote authorization service."""
import getpass, hashlib, hmac, os
import assessment, tracker

def init(db):
 db.execute("""CREATE TABLE IF NOT EXISTS local_approval_credentials
 (id INTEGER PRIMARY KEY CHECK(id=1), salt BLOB NOT NULL, verifier BLOB NOT NULL)""")
 db.commit()

def derive(secret,salt):
 return hashlib.scrypt(secret.encode("utf-8"),salt=salt,n=16384,r=8,p=1,dklen=32)

def setup(db,secret):
 init(db)
 if not isinstance(secret,str) or len(secret)<16:raise ValueError("Passphrase must contain at least 16 characters")
 if db.execute("SELECT 1 FROM local_approval_credentials WHERE id=1").fetchone():
  raise ValueError("A passphrase is already configured")
 salt=os.urandom(16)
 with db:db.execute("INSERT INTO local_approval_credentials(id,salt,verifier) VALUES(1,?,?)",(salt,derive(secret,salt)))

def authenticate(db,secret):
 init(db)
 row=db.execute("SELECT salt,verifier FROM local_approval_credentials WHERE id=1").fetchone()
 if not row or not isinstance(secret,str):return False
 return hmac.compare_digest(derive(secret,row[0]),row[1])

def decide(db,secret,url,event_id,action,decision,approver,evidence):
 if not authenticate(db,secret):raise PermissionError("Authentication failed")
 return assessment.decide(db,url,event_id,action,decision,approver,evidence)

def main():
 import argparse
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument("--database",default="bounty-tracker.sqlite")
 sub=p.add_subparsers(dest="command",required=True)
 sub.add_parser("setup")
 a=sub.add_parser("decide")
 for name in ("url","event_id","action","decision","approver","evidence"):a.add_argument(name)
 args=p.parse_args()
 with tracker.connect(args.database) as db:
  secret=getpass.getpass("Local approval passphrase: ")
  if args.command=="setup":
   confirm=getpass.getpass("Repeat passphrase: ")
   if not hmac.compare_digest(secret,confirm):p.error("Passphrases do not match")
   setup(db,secret);print("Local passphrase configured.")
  else:
   decide(db,secret,args.url,args.event_id,args.action,args.decision,args.approver,args.evidence)
   print("Decision recorded locally. No external action was performed.")
if __name__=="__main__":main()
