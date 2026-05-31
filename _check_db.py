import sqlite3, os
db_path = 'audit_diary.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cur = conn.execute("PRAGMA table_info(users)")
    cols = [r[1] for r in cur.fetchall()]
    print('Current columns:', cols)
    conn.close()
else:
    print('DB does not exist')