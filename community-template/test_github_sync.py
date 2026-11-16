import io, sqlite3, unittest, urllib.error
from email.message import Message
import tracker, github_sync as g

def issue(n=1,**extra):
 d={"html_url":f"https://github.com/Example/Repo/issues/{n}","title":"Fix thing","state":"open","body":"Bounty: $100. Fix the test.","updated_at":"2026-01-01T00:00:00Z"};d.update(extra);return d

class SyncTests(unittest.TestCase):
 def setUp(self):self.db=tracker.connect(":memory:")
 def tearDown(self):self.db.close()
 def test_dedup_metadata_and_update(self):
  self.assertEqual(g.import_issues(self.db,[issue()])["inserted"],1)
  self.assertEqual(g.import_issues(self.db,[issue(body="Reward: $200")])["updated"],1)
  row=self.db.execute("select repository,issue_number,advertised_reward,source_url from github_discovery").fetchone()
  self.assertEqual(row,("example/repo",1,"$200","https://github.com/example/repo/issues/1"))
  self.assertEqual(self.db.execute("select count(*) from opportunities").fetchone()[0],1)
 def test_missing_and_pull_requests(self):
  x=issue();del x["title"]
  self.assertEqual(g.import_issues(self.db,[x,issue(pull_request={}),{},issue(2,body=None)])["skipped"],3)
 def test_pagination(self):
  calls=[]
  def fetch(p,t):
   calls.append(p);return [issue(n+1) for n in range(100)] if p==1 else [issue(101)]
  self.assertEqual(g.sync(self.db,3,fetcher=fetch)["inserted"],101)
  self.assertEqual(calls,[1,2])
 def test_rate_limit(self):
  headers=Message();headers["X-RateLimit-Remaining"]="0"
  def fail(*a,**k):raise urllib.error.HTTPError("https://api.github.com",403,"limited",headers,None)
  with self.assertRaises(g.RateLimited):g.fetch_page(1,opener=fail)
 def test_network_error(self):
  def fail(*a,**k):raise urllib.error.URLError("offline")
  with self.assertRaises(g.DiscoveryError):g.fetch_page(1,opener=fail)
if __name__=="__main__":unittest.main()
