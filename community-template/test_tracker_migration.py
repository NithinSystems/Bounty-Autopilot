import sqlite3, tempfile, unittest
from pathlib import Path
import tracker

class MigrationTests(unittest.TestCase):
 def test_old_database_preserved_and_history(self):
  with tempfile.TemporaryDirectory() as td:
   path=str(Path(td)/"old.sqlite")
   db=sqlite3.connect(path)
   db.execute("CREATE TABLE opportunities (url TEXT PRIMARY KEY,title TEXT NOT NULL,state TEXT NOT NULL,reward_note TEXT NOT NULL DEFAULT '',updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)")
   old="https://github.com/Example/Repo/issues/1?ref=old"
   db.execute("INSERT INTO opportunities(url,title,state) VALUES(?,?,?)",(old,"Old task","reviewing"))
   db.commit();db.close()
   db=tracker.connect(path)
   self.assertFalse(tracker.add(db,"https://github.com/example/repo/issues/1","Duplicate"))
   self.assertTrue(tracker.update(db,"https://github.com/example/repo/issues/1","awaiting_approval","Needs review"))
   self.assertEqual(db.execute("select url,state from opportunities").fetchone(),(old,"awaiting_approval"))
   self.assertEqual(db.execute("select old_state,new_state,source from tracker_events").fetchone(),("reviewing","awaiting_approval","user"))
   db.close()
 def test_history_on_add_and_repeat(self):
  db=tracker.connect(":memory:")
  url="https://github.com/a/b/issues/3"
  self.assertTrue(tracker.add(db,url,"Title"))
  self.assertFalse(tracker.add(db,url+"?source=x","Title"))
  self.assertEqual(db.execute("select count(*) from tracker_events").fetchone()[0],1)
  db.close()
if __name__=="__main__":unittest.main()
