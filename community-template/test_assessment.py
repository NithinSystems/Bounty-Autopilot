import datetime as dt, json, unittest
import tracker, github_sync, assessment
from test_github_sync import issue

class AssessmentTests(unittest.TestCase):
 def setUp(self):
  self.db=tracker.connect(":memory:")
  self.now=dt.datetime(2026,1,1,tzinfo=dt.timezone.utc)
 def tearDown(self):self.db.close()
 def add(self,item):github_sync.import_issues(self.db,[item],observed_at="2026-01-01T00:00:00+00:00")
 def test_idempotency_unknown_and_minimal_payload(self):
  item=issue();self.add(item)
  a=assessment.assess(self.db,item["html_url"],self.now)
  b=assessment.assess(self.db,item["html_url"],self.now)
  self.assertEqual(a["assessment_id"],b["assessment_id"])
  self.assertEqual(self.db.execute("select state from opportunities").fetchone()[0],"scored")
  self.assertEqual(self.db.execute("select count(*) from tracker_events where source='assessment'").fetchone()[0],1)
  self.assertEqual(self.db.execute("select count(*) from notification_outbox").fetchone()[0],1)
  payload=json.loads(self.db.execute("select payload_json from notification_outbox").fetchone()[0])
  self.assertEqual(set(payload),{"url","score","confidence","reasons"})
  self.assertIn("unknown",str(payload).lower())
 def test_missing_reward_and_bad_candidates_not_queued(self):
  for i,body in enumerate(("No reward mentioned","Deadline: 2025-12-31","Please share your private key"),1):
   item=issue(i,body=body);self.add(item);result=assessment.assess(self.db,item["html_url"],self.now)
   self.assertLess(result["score"],60)
  self.assertEqual(self.db.execute("select count(*) from notification_outbox").fetchone()[0],0)
 def test_decision_is_audit_only_and_idempotent(self):
  item=issue();self.add(item);args=(self.db,item["html_url"],"evt-1","execute","rejected","local-user","Reviewed issue")
  self.assertTrue(assessment.decide(*args))
  self.assertFalse(assessment.decide(*args))
  with self.assertRaises(ValueError):assessment.decide(self.db,item["html_url"],"evt-1","execute","approved","local-user","Reviewed issue")
  self.assertEqual(self.db.execute("select decision from approval_decisions").fetchone()[0],"rejected")
 def test_failed_delivery_cannot_be_marked_sent_without_retry_protocol(self):
  item=issue();self.add(item);assessment.assess(self.db,item["html_url"],self.now)
  eid=self.db.execute("select event_id from notification_outbox").fetchone()[0]
  self.assertTrue(assessment.record_delivery(self.db,eid,"failed"))
  self.assertFalse(assessment.record_delivery(self.db,eid,"sent"))
  self.assertEqual(self.db.execute("select state,attempts from notification_outbox").fetchone(),("failed",1))
if __name__=="__main__":unittest.main()
