import unittest
import approval_auth as a, tracker, github_sync, assessment
from test_github_sync import issue

class AuthenticationTests(unittest.TestCase):
 def setUp(self):
  self.db=tracker.connect(":memory:")
  github_sync.import_issues(self.db,[issue()])
  assessment.initialize(self.db)
 def tearDown(self): self.db.close()
 def test_setup_and_authenticated_decision(self):
  with self.assertRaises(ValueError):a.setup(self.db,"short")
  a.setup(self.db,"example-passphrase-long-enough")
  self.assertFalse(a.authenticate(self.db,"wrong"))
  self.assertTrue(a.authenticate(self.db,"example-passphrase-long-enough"))
  with self.assertRaises(PermissionError):
   a.decide(self.db,"wrong",issue()["html_url"],"event","send","approved","owner","reviewed")
  self.assertEqual(self.db.execute("select count(*) from approval_decisions").fetchone()[0],0)
  self.assertTrue(a.decide(self.db,"example-passphrase-long-enough",issue()["html_url"],"event","send","rejected","owner","reviewed"))
  self.assertEqual(self.db.execute("select decision from approval_decisions").fetchone()[0],"rejected")
  with self.assertRaises(ValueError):a.setup(self.db,"another-long-enough-passphrase")
 def test_credential_not_stored_plaintext(self):
  a.setup(self.db,"example-passphrase-long-enough")
  salt,verifier=self.db.execute("select salt,verifier from local_approval_credentials").fetchone()
  self.assertNotIn(b"example-passphrase",salt+verifier)
if __name__=="__main__":unittest.main()
