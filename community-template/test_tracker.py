import sqlite3, unittest
import tracker

class TrackerTests(unittest.TestCase):
 def setUp(self): self.db=tracker.connect(":memory:")
 def tearDown(self): self.db.close()
 def test_dedup_and_status(self):
  u="https://github.com/example/repo/issues/1"
  self.assertTrue(tracker.add(self.db,u,"Fix test"))
  self.assertFalse(tracker.add(self.db,u,"Duplicate"))
  self.assertTrue(tracker.update(self.db,u,"paid","Reported received"))
  self.assertEqual(self.db.execute("select count(*),state from opportunities").fetchone(),(1,"paid"))
 def test_invalid_and_missing(self):
  with self.assertRaises(ValueError): tracker.add(self.db,"https://name:secret@example.com/","bad")
  with self.assertRaises(ValueError): tracker.add(self.db,"http://example.com/","bad")
  with self.assertRaises(ValueError): tracker.update(self.db,"x","unknown","")
  self.assertFalse(tracker.update(self.db,"https://example.com/x","accepted",""))
if __name__=="__main__":unittest.main()
