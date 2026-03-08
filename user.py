"""
BDO Audit Pro — User Management CLI
Run this from your Codespace terminal:

  python manage_users.py                  # interactive menu
  python manage_users.py list             # list all users
  python manage_users.py add              # add a user
  python manage_users.py delete <user>    # delete a user
  python manage_users.py password <user>  # reset a password
"""

import sqlite3
import hashlib
import sys
from datetime import datetime

DB_FILE = "audit_storage.db"

def hash_pw(p): return hashlib.sha256(p.strip().encode()).hexdigest()

def get_conn(): return sqlite3.connect(DB_FILE)

def ensure_table():
    with get_conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY, password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 0, created TEXT)""")
        c.commit()

def list_users():
    with get_conn() as c:
        rows = c.execute("SELECT username, is_admin, created FROM users ORDER BY username").fetchall()
    if not rows:
        print("No users found.")
        return
    print(f"\n{'USERNAME':<20} {'ROLE':<10} {'CREATED'}")
    print("-" * 45)
    for r in rows:
        role = "Admin" if r[1] else "Auditor"
        print(f"{r[0]:<20} {role:<10} {r[2] or '—'}")
    print()

def add_user():
    print("\n── Add New User ──")
    username = input("Username: ").strip().lower()
    if not username:
        print("Username cannot be empty."); return
    password = input("Password: ").strip()
    if not password:
        print("Password cannot be empty."); return
    is_admin = input("Grant admin access? (y/N): ").strip().lower() == "y"
    try:
        with get_conn() as c:
            c.execute("INSERT INTO users VALUES (?,?,?,?)",
                      (username, hash_pw(password), int(is_admin), datetime.now().strftime("%Y-%m-%d")))
            c.commit()
        print(f"✅  User '{username}' created as {'Admin' if is_admin else 'Auditor'}.")
    except sqlite3.IntegrityError:
        print(f"❌  Username '{username}' already exists.")

def delete_user(username=None):
    if not username:
        username = input("Username to delete: ").strip().lower()
    confirm = input(f"Delete '{username}'? This cannot be undone. (y/N): ").strip().lower()
    if confirm == "y":
        with get_conn() as c:
            c.execute("DELETE FROM users WHERE username=?", (username,))
            c.commit()
        print(f"✅  User '{username}' deleted.")
    else:
        print("Cancelled.")

def reset_password(username=None):
    if not username:
        username = input("Username: ").strip().lower()
    new_pw = input("New password: ").strip()
    if not new_pw:
        print("Password cannot be empty."); return
    with get_conn() as c:
        c.execute("UPDATE users SET password_hash=? WHERE username=?", (hash_pw(new_pw), username))
        c.commit()
    print(f"✅  Password updated for '{username}'.")

def interactive_menu():
    print("\n🔷  BDO Audit Pro — User Management")
    print("=" * 38)
    while True:
        print("\n1. List users\n2. Add user\n3. Delete user\n4. Reset password\n5. Exit")
        choice = input("Choice: ").strip()
        if   choice == "1": list_users()
        elif choice == "2": add_user()
        elif choice == "3": delete_user()
        elif choice == "4": reset_password()
        elif choice == "5": print("Bye!"); break
        else: print("Invalid choice.")

if __name__ == "__main__":
    ensure_table()
    args = sys.argv[1:]
    if   not args:               interactive_menu()
    elif args[0] == "list":      list_users()
    elif args[0] == "add":       add_user()
    elif args[0] == "delete":    delete_user(args[1] if len(args) > 1 else None)
    elif args[0] == "password":  reset_password(args[1] if len(args) > 1 else None)
    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: python manage_users.py [list|add|delete|password]")
        