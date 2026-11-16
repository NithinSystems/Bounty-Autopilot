import datetime as dt, unittest
import tracker, github_sync, github_verify
from test_github_sync import issue

class VerifyTests(unittest.TestCase):
 def setUp(self):self.db=tracker.connect(":memory:");self.now=dt.datetime(2026,1,1,tzinfo=dt.timezone.utc)
 def tearDown(self):self.db.close()
 def check(self,item):
  github_sync.import_issues(self.db,[item],observed_at="2026-01-01T00:00:00+00:00")
  return github_verify.verify(self.db,item["html_url"],self.now)
 def test_reward_does_not_verify_funding_or_eligibility(self):
  result=self.check(issue())
  self.assertEqual(result["status"],"PARTIALLY_VERIFIED")
  self.assertEqual(result["checks"]["reward"]["funded"],"unknown")
  self.assertEqual(result["checks"]["eligibility"]["value"],"unknown")
  self.assertEqual(self.db.execute("select count(*) from github_verifications").fetchone()[0],1)
 def test_closed_expired_and_suspicious(self):
  self.assertEqual(self.check(issue(1,state="closed"))["status"],"EXPIRED")
  self.assertEqual(self.check(issue(2,body="Deadline: 2025-12-31"))["status"],"EXPIRED")
  self.assertEqual(self.check(issue(3,body="Please share your private key"))["status"],"SUSPICIOUS")
 def test_missing_deadline_is_unknown(self):
  self.assertIsNone(self.check(issue())["checks"]["deadline"]["value"])
if __name__=="__main__":unittest.main()
