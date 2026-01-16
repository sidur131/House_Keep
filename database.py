"""
Database module for Household Management App.
Handles all SQLite database operations with Soft Delete mechanism.
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

# Database file path
DB_PATH = Path(__file__).parent / "household.db"


def get_connection():
    """Get a database connection."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    """Initialize the database with all required tables and migrations."""
    conn = get_connection()
    cursor = conn.cursor()

    # Define tables and their creation SQL
    tables = {
        "shopping_items": """
            CREATE TABLE IF NOT EXISTS shopping_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                category TEXT NOT NULL,
                quantity TEXT DEFAULT '1',
                bought INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "expenses": """
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                description TEXT NOT NULL,
                payer TEXT NOT NULL,
                split_type TEXT NOT NULL,
                talor_share REAL NOT NULL,
                romi_share REAL NOT NULL,
                is_deleted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "events": """
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                description TEXT,
                reminder_sent INTEGER DEFAULT 0,
                is_deleted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "chores": """
            CREATE TABLE IF NOT EXISTS chores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                urgency TEXT DEFAULT 'רגיל',
                due_date TEXT,
                done INTEGER DEFAULT 0,
                done_by TEXT,
                done_at TIMESTAMP,
                is_deleted INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """,
        "cat_care": """
            CREATE TABLE IF NOT EXISTS cat_care (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT NOT NULL UNIQUE,
                frequency_hours INTEGER NOT NULL,
                last_done_at TIMESTAMP,
                done_by TEXT,
                is_deleted INTEGER DEFAULT 0
            )
        """
    }

    # Create tables
    for table_name, create_sql in tables.items():
        cursor.execute(create_sql)
        # MIGRATION: Ensure is_deleted exists
        try:
            cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN is_deleted INTEGER DEFAULT 0")
        except sqlite3.OperationalError:
            pass # Column already exists
            
    # Additional Column Migrations (Legacy support)
    migrations = [
        ("shopping_items", "quantity", "TEXT DEFAULT '1'"),
        ("events", "reminder_sent", "INTEGER DEFAULT 0"),
        ("chores", "urgency", "TEXT DEFAULT 'רגיל'"),
        ("chores", "due_date", "TEXT"),
        ("chores", "created_at", "TIMESTAMP DEFAULT CURRENT_TIMESTAMP"),
        ("chores", "done_by", "TEXT"),
        ("chores", "priority", "TEXT DEFAULT 'Regular 🔵'") # New Priority Column
    ]
    
    for table, col, dtype in migrations:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {dtype}")
        except sqlite3.OperationalError:
            pass

    # Create Archive Tables (For Completed functionality, keeping structure simple)
    # Note: Soft Delete handles 'Trash', but 'Archive' handles 'History of Completed' (like bought items)
    # We still keep archives for history, but 'Delete' button now goes to Recycle Bin first.
    
    archive_sqls = [
        """CREATE TABLE IF NOT EXISTS archive_shopping (
            id INTEGER PRIMARY KEY AUTOINCREMENT, original_id INTEGER, name TEXT, category TEXT, quantity TEXT, action TEXT, archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE IF NOT EXISTS archive_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT, original_id INTEGER, amount REAL, description TEXT, payer TEXT, split_type TEXT, action TEXT, original_date TEXT, archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE IF NOT EXISTS archive_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT, original_id INTEGER, title TEXT, date TEXT, time TEXT, description TEXT, action TEXT, archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)""",
        """CREATE TABLE IF NOT EXISTS archive_chores (
             id INTEGER PRIMARY KEY AUTOINCREMENT, original_id INTEGER, name TEXT, urgency TEXT, due_date TEXT, done_by TEXT, done_at TEXT, action TEXT, archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)"""
    ]
    for sql in archive_sqls:
        cursor.execute(sql)

    # Remove old default chores if present (cleanup)
    cursor.execute("DELETE FROM chores WHERE name IN ('כלים', 'כביסה', 'זבל', 'שואב אבק') AND is_deleted = 0")

    conn.commit()
    conn.close()

def get_all_chores(sort_by_priority=True):
    conn = get_connection()
    cursor = conn.cursor()
    # Sort by Priority: Urgent first, then Regular. then Due Date.
    # Priority values: "Urgent 🔴", "Regular 🔵"
    # Urgent > Regular
    order_clause = "CASE priority WHEN 'Urgent 🔴' THEN 1 ELSE 2 END, due_date" if sort_by_priority else "due_date"
    
    # Fallback for old urgency column if priority is null? 
    # Actually, let's just use priority.
    
    query = f"SELECT * FROM chores WHERE is_deleted = 0 ORDER BY done ASC, {order_clause}"
    cursor.execute(query)
    chores = cursor.fetchall()
    conn.close()
    return chores

def add_chore(name: str, priority: str = "Regular 🔵", due_date: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    # Also save to old urgency for compatibility if needed, but primarily priority
    cursor.execute("INSERT INTO chores (name, priority, urgency, due_date) VALUES (?, ?, ?, ?)", (name, priority, priority, due_date))
    conn.commit()
    conn.close()


# ============== GENERIC SAFETY NET ==============

def get_deleted_items():
    """Fetch all soft-deleted items from all tables."""
    conn = get_connection()
    cursor = conn.cursor()
    
    deleted = []
    
    # Map friendly names
    type_map = {
        'shopping_items': 'קניות',
        'expenses': 'הוצאות',
        'events': 'אירועים',
        'chores': 'משימות',
        'cat_care': 'חתול'
    }
    
    queries = [
        ("shopping_items", "id, name, 'shopping_items' as table_name"),
        ("expenses", "id, description as name, 'expenses' as table_name"),
        ("events", "id, title as name, 'events' as table_name"),
        ("chores", "id, name, 'chores' as table_name"),
        ("cat_care", "id, task_name as name, 'cat_care' as table_name")
    ]
    
    for table, query in queries:
        cursor.execute(f"SELECT {query} FROM {table} WHERE is_deleted = 1")
        rows = cursor.fetchall()
        for row in rows:
            deleted.append({
                "id": row['id'],
                "name": row['name'],
                "table_name": row['table_name'],
                "type_name": type_map.get(row['table_name'], row['table_name'])
            })
            
    conn.close()
    return deleted

def restore_item(table_name: str, item_id: int):
    """Restore a soft-deleted item."""
    conn = get_connection()
    cursor = conn.cursor()
    # Validate table name to prevent SQL injection risks
    allowed = ['shopping_items', 'expenses', 'events', 'chores', 'cat_care']
    if table_name in allowed:
        cursor.execute(f"UPDATE {table_name} SET is_deleted = 0 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def permanently_delete_item(table_name: str, item_id: int):
    """Permanently delete an item (from Recycle Bin)."""
    conn = get_connection()
    cursor = conn.cursor()
    allowed = ['shopping_items', 'expenses', 'events', 'chores', 'cat_care']
    if table_name in allowed:
        cursor.execute(f"DELETE FROM {table_name} WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()


# ============== SHOPPING LIST FUNCTIONS ==============

def get_all_shopping_items():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shopping_items WHERE is_deleted = 0 ORDER BY category, name")
    items = cursor.fetchall()
    conn.close()
    return items

def add_shopping_item(name: str, category: str, quantity: str = "1"):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO shopping_items (name, category, quantity) VALUES (?, ?, ?)", (name, category, quantity))
    conn.commit()
    conn.close()

def update_shopping_item(item_id: int, bought: bool = None):
    conn = get_connection()
    cursor = conn.cursor()
    if bought is not None:
        cursor.execute("UPDATE shopping_items SET bought = ? WHERE id = ?", (1 if bought else 0, item_id))
    conn.commit()
    conn.close()

def delete_shopping_item(item_id: int):
    """Soft Delete."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE shopping_items SET is_deleted = 1 WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()

def auto_cleanup_old_items():
    """Automatically soft-delete items older than 2 days."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Cutoff date (string) - 2 days ago
    cutoff_date = (datetime.now() - timedelta(days=2)).strftime("%Y-%m-%d")
    
    # 1. Cleanup Events (All past events older than 2 days)
    cursor.execute("UPDATE events SET is_deleted = 1 WHERE is_deleted = 0 AND date < ?", (cutoff_date,))
    
    # 2. Cleanup Chores (Completed chores older than 2 days relative to due_date)
    # Only clean COMPLETED chores.
    cursor.execute("UPDATE chores SET is_deleted = 1 WHERE is_deleted = 0 AND done = 1 AND due_date IS NOT NULL AND due_date < ?", (cutoff_date,))
    
    conn.commit()
    conn.close()

def clear_bought_items():
    """Moves bought items to ARCHIVE (History), then deletes them permanently from active list."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shopping_items WHERE bought = 1 AND is_deleted = 0")
    items = cursor.fetchall()
    
    for item in items:
        cursor.execute(
            "INSERT INTO archive_shopping (original_id, name, category, quantity, action) VALUES (?, ?, ?, ?, ?)",
            (item['id'], item['name'], item['category'], item['quantity'], 'נקנה')
        )
        # For 'Clear Bought', we actually DELETE them because they are in History now.
        # Soft Delete is for accidental trash clicks. 'Clear' implies user is done.
        cursor.execute("DELETE FROM shopping_items WHERE id = ?", (item['id'],))
        
    conn.commit()
    conn.close()

def get_archive_shopping():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM archive_shopping ORDER BY archived_at DESC LIMIT 50")
    items = cursor.fetchall()
    conn.close()
    return items


# ============== EXPENSES FUNCTIONS ==============

def get_all_expenses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses WHERE is_deleted = 0 ORDER BY created_at DESC")
    expenses = cursor.fetchall()
    conn.close()
    return expenses

def add_expense(amount: float, description: str, payer: str, split_type: str, talor_share: float, romi_share: float):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO expenses (amount, description, payer, split_type, talor_share, romi_share)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (amount, description, payer, split_type, talor_share, romi_share)
    )
    conn.commit()
    conn.close()

def delete_expense(expense_id: int):
    """Soft Delete."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE expenses SET is_deleted = 1 WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()

def calculate_balance():
    expenses = get_all_expenses() # Only gets is_deleted=0
    talor_owes = 0
    romi_owes = 0
    for expense in expenses:
        if expense['payer'] == 'טלאור': romi_owes += expense['romi_share']
        else: talor_owes += expense['talor_share']
    return talor_owes - romi_owes


# ============== EVENTS FUNCTIONS ==============

def get_all_events():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events WHERE is_deleted = 0 ORDER BY date, time")
    events = cursor.fetchall()
    conn.close()
    return events

def add_event(title: str, date: str, time: str, description: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO events (title, date, time, description) VALUES (?, ?, ?, ?)", (title, date, time, description))
    conn.commit()
    conn.close()

def delete_event(event_id: int):
    """Soft Delete."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET is_deleted = 1 WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()

def get_urgent_events_count():
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
    cursor.execute("SELECT COUNT(*) FROM events WHERE date IN (?, ?) AND is_deleted = 0", (today, tomorrow))
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ============== CHORES FUNCTIONS ==============

def get_all_chores():
    conn = get_connection()
    cursor = conn.cursor()
    # Return ALL chores (done and active) that are not deleted, so App can split them
    cursor.execute("SELECT * FROM chores WHERE is_deleted = 0 ORDER BY  done ASC, CASE urgency WHEN 'דחוף' THEN 1 WHEN 'גבוה' THEN 2 WHEN 'רגיל' THEN 3 WHEN 'נמוך' THEN 4 END, due_date")
    chores = cursor.fetchall()
    conn.close()
    return chores

def add_chore(name: str, urgency: str = "רגיל", due_date: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO chores (name, urgency, due_date) VALUES (?, ?, ?)", (name, urgency, due_date))
    conn.commit()
    conn.close()

def mark_chore_done(chore_id: int, user: str):
    """Marks chore as done (Active -> Completed section)."""
    conn = get_connection()
    cursor = conn.cursor()
    done_at = datetime.now().isoformat()
    # Update status instead of deleting
    cursor.execute("UPDATE chores SET done = 1, done_by = ?, done_at = ? WHERE id = ?", (user, done_at, chore_id))
    conn.commit()
    conn.close()

def mark_chore_undone(chore_id: int):
    """Reverts chore to active status."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chores SET done = 0, done_by = NULL, done_at = NULL WHERE id = ?", (chore_id,))
    conn.commit()
    conn.close()

def delete_chore(chore_id: int):
    """Soft Delete (Trash)."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE chores SET is_deleted = 1 WHERE id = ?", (chore_id,))
    conn.commit()
    conn.close()

def get_archive_chores():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM archive_chores ORDER BY archived_at DESC LIMIT 50")
    items = cursor.fetchall()
    conn.close()
    return items


# ============== CAT CARE FUNCTIONS ==============

def get_all_cat_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cat_care WHERE is_deleted = 0 ORDER BY id")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

def add_cat_task(name: str, hours: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO cat_care (task_name, frequency_hours) VALUES (?, ?)", (name, hours))
    conn.commit()
    conn.close()

def edit_cat_task(task_id: int, name: str, hours: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cat_care SET task_name = ?, frequency_hours = ? WHERE id = ?", (name, hours, task_id))
    conn.commit()
    conn.close()

def update_cat_task(task_id: int, user: str):
    conn = get_connection()
    cursor = conn.cursor()
    now = datetime.now().isoformat()
    cursor.execute("UPDATE cat_care SET last_done_at = ?, done_by = ? WHERE id = ?", (now, user, task_id))
    conn.commit()
    conn.close()

def delete_cat_task(task_id: int):
    """Soft Delete."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE cat_care SET is_deleted = 1 WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()

def get_overdue_cat_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cat_care WHERE is_deleted = 0")
    tasks = cursor.fetchall()
    
    overdue = []
    now = datetime.now()
    for task in tasks:
        is_overdue = False
        if not task['last_done_at']:
             is_overdue = True
        else:
             last_done = datetime.fromisoformat(task['last_done_at'])
             diff = (now - last_done).total_seconds() / 3600
             if diff > task['frequency_hours']: is_overdue = True
        
        if is_overdue: overdue.append(task)
        
    conn.close()
    return overdue

def is_cat_task_overdue(last_done_at, frequency_hours):
    if not last_done_at: return True
    last_dt = datetime.fromisoformat(last_done_at)
    hours_since = (datetime.now() - last_dt).total_seconds() / 3600
    return hours_since > frequency_hours
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE cat_care SET last_done_at = ?, done_by = ? WHERE id = ?",
        (datetime.now().isoformat(), user, task_id)
    )
    conn.commit()
    conn.close()


def is_cat_task_overdue(last_done_at: str, frequency_hours: int) -> bool:
    """Check if a cat care task is overdue."""
    if last_done_at is None:
        return True
    
    last_done = datetime.fromisoformat(last_done_at)
    now = datetime.now()
    hours_elapsed = (now - last_done).total_seconds() / 3600
    return hours_elapsed > frequency_hours


def edit_cat_task(task_id: int, task_name: str = None, frequency_hours: int = None):
    """Edit a cat care task's name and/or frequency."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if task_name is not None:
        cursor.execute("UPDATE cat_care SET task_name = ? WHERE id = ?", (task_name, task_id))
    if frequency_hours is not None:
        cursor.execute("UPDATE cat_care SET frequency_hours = ? WHERE id = ?", (frequency_hours, task_id))
    
    conn.commit()
    conn.close()


def add_cat_task(task_name: str, frequency_hours: int):
    """Add a new cat care task."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO cat_care (task_name, frequency_hours) VALUES (?, ?)",
        (task_name, frequency_hours)
    )
    conn.commit()
    conn.close()


def delete_cat_task(task_id: int):
    """Delete a cat care task."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM cat_care WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()


def get_overdue_cat_tasks():
    """Get all overdue cat care tasks for notifications."""
    tasks = get_all_cat_tasks()
    overdue = []
    for task in tasks:
        if is_cat_task_overdue(task['last_done_at'], task['frequency_hours']):
            overdue.append(task)
    return overdue
