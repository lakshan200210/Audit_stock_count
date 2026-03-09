"""
cleanup.py
──────────
Runs daily via GitHub Actions.
Does two things:
  1. Removes audit sessions that have no counted products
     (user started a session but never saved anything — or deleted their data)
  2. Removes user accounts that have had no activity for 7+ days
     (no sessions updated in the last 7 days)

Zero changes needed to app.py.
Requires DATABASE_URL in GitHub Actions secrets (same value as Streamlit secrets).
"""

import os
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta

DATABASE_URL = os.environ["DATABASE_URL"]

def get_db():
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=15)
    conn.autocommit = True
    return conn

def run(conn, sql, params=()):
    cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cur.execute(sql, params)
    return cur

def main():
    conn   = get_db()
    now    = datetime.utcnow()
    cutoff = now - timedelta(days=7)
    cutoff_str = cutoff.strftime("%Y-%m-%d")

    print(f"[{now.strftime('%Y-%m-%d %H:%M')} UTC] Starting cleanup…")

    # ── 1. Remove empty sessions ──────────────────────────────────
    # These are sessions where data is NULL or the stored pickle is
    # tiny (less than 100 bytes = no real product data saved).
    # This catches sessions the user abandoned without ever saving a count.
    result = run(conn, """
        DELETE FROM audit_sessions
        WHERE data IS NULL
           OR length(data) < 100
        RETURNING sid, username
    """)
    empty_deleted = result.fetchall()
    for row in empty_deleted:
        print(f"  🗑  Removed empty session: {row['sid']} (user: {row['username']})")

    # ── 2. Remove inactive user accounts ─────────────────────────
    # A user is considered inactive if:
    #   - They have no sessions at all, OR
    #   - Their most recent session was last updated more than 7 days ago
    # Admins are never auto-deleted.
    result = run(conn, """
        DELETE FROM users
        WHERE is_admin = FALSE
          AND username NOT IN (
              SELECT DISTINCT username
              FROM audit_sessions
              WHERE updated >= %s
          )
          AND created < %s
        RETURNING username
    """, (cutoff_str, cutoff_str))
    inactive_deleted = result.fetchall()
    for row in inactive_deleted:
        print(f"  👤 Removed inactive account: {row['username']} (no activity in 7 days)")

    # ── 3. Cascade: remove sessions belonging to deleted users ────
    # After deleting users, clean up any orphaned sessions they owned.
    result = run(conn, """
        DELETE FROM audit_sessions
        WHERE username NOT IN (SELECT username FROM users)
        RETURNING sid, username
    """)
    orphan_deleted = result.fetchall()
    for row in orphan_deleted:
        print(f"  🗑  Removed orphaned session: {row['sid']} (user no longer exists)")

    # ── Summary ───────────────────────────────────────────────────
    print(f"\n✅ Cleanup complete:")
    print(f"   Empty sessions removed:    {len(empty_deleted)}")
    print(f"   Inactive accounts removed: {len(inactive_deleted)}")
    print(f"   Orphaned sessions removed: {len(orphan_deleted)}")

if __name__ == "__main__":
    main()
