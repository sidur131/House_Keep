"""
Database module for Household Management App.
Handles all SQLite database operations.
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
    """Initialize the database with all required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Shopping Items table (with quantity)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS shopping_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity TEXT DEFAULT '1',
            bought INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add quantity column if not exists (for existing databases)
    try:
        cursor.execute("ALTER TABLE shopping_items ADD COLUMN quantity TEXT DEFAULT '1'")
    except sqlite3.OperationalError:
        pass  # Column already exists

    # Expenses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            payer TEXT NOT NULL,
            split_type TEXT NOT NULL,
            talor_share REAL NOT NULL,
            romi_share REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Events table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT,
            description TEXT,
            reminder_sent INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add reminder_sent column if not exists
    try:
        cursor.execute("ALTER TABLE events ADD COLUMN reminder_sent INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    # Chores table - enhanced with urgency and due date
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS chores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            urgency TEXT DEFAULT 'רגיל',
            due_date TEXT,
            done INTEGER DEFAULT 0,
            done_by TEXT,
            done_at TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Add new columns if not exists
    try:
        cursor.execute("ALTER TABLE chores ADD COLUMN urgency TEXT DEFAULT 'רגיל'")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE chores ADD COLUMN due_date TEXT")
    except sqlite3.OperationalError:
        pass
    try:
        cursor.execute("ALTER TABLE chores ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP")
    except sqlite3.OperationalError:
        pass
    
    # Remove old default chores
    cursor.execute("DELETE FROM chores WHERE name IN ('כלים', 'כביסה', 'זבל', 'שואב אבק', 'אמבטיה', 'מטבח', 'Dishes', 'Laundry', 'Trash', 'Vacuuming', 'Bathroom', 'Kitchen')")

    # Cat Care table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS cat_care (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task_name TEXT NOT NULL UNIQUE,
            frequency_hours INTEGER NOT NULL,
            last_done_at TIMESTAMP,
            done_by TEXT
        )
    """)

    # Insert default cat care tasks in Hebrew if not exist
    cat_tasks = [
        ("מים", 24),
        ("אוכל", 12),
        ("ארגז חול", 48)
    ]
    for task_name, frequency in cat_tasks:
        cursor.execute(
            "INSERT OR IGNORE INTO cat_care (task_name, frequency_hours) VALUES (?, ?)",
            (task_name, frequency)
        )
    
    # ============== ARCHIVE TABLES ==============
    
    # Archive for shopping items
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive_shopping (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id INTEGER,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            quantity TEXT,
            action TEXT NOT NULL,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Archive for expenses
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id INTEGER,
            amount REAL NOT NULL,
            description TEXT NOT NULL,
            payer TEXT NOT NULL,
            split_type TEXT NOT NULL,
            action TEXT NOT NULL,
            original_date TEXT,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Archive for events
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id INTEGER,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT,
            description TEXT,
            action TEXT NOT NULL,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Archive for chores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS archive_chores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_id INTEGER,
            name TEXT NOT NULL,
            urgency TEXT,
            due_date TEXT,
            done_by TEXT,
            done_at TEXT,
            action TEXT NOT NULL,
            archived_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


# ============== SHOPPING LIST FUNCTIONS ==============

def get_all_shopping_items():
    """Get all shopping items."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM shopping_items ORDER BY category, name")
    items = cursor.fetchall()
    conn.close()
    return items


def add_shopping_item(name: str, category: str, quantity: str = "1"):
    """Add a new shopping item."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO shopping_items (name, category, quantity) VALUES (?, ?, ?)",
        (name, category, quantity)
    )
    conn.commit()
    conn.close()


def update_shopping_item(item_id: int, name: str = None, category: str = None, quantity: str = None, bought: bool = None):
    """Update a shopping item."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if name is not None:
        cursor.execute("UPDATE shopping_items SET name = ? WHERE id = ?", (name, item_id))
    if category is not None:
        cursor.execute("UPDATE shopping_items SET category = ? WHERE id = ?", (category, item_id))
    if quantity is not None:
        cursor.execute("UPDATE shopping_items SET quantity = ? WHERE id = ?", (quantity, item_id))
    if bought is not None:
        cursor.execute("UPDATE shopping_items SET bought = ? WHERE id = ?", (1 if bought else 0, item_id))
    
    conn.commit()
    conn.close()


def delete_shopping_item(item_id: int):
    """Delete a shopping item and archive it."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get item details first
    cursor.execute("SELECT * FROM shopping_items WHERE id = ?", (item_id,))
    item = cursor.fetchone()
    
    if item:
        # Archive it
        cursor.execute(
            "INSERT INTO archive_shopping (original_id, name, category, quantity, action) VALUES (?, ?, ?, ?, ?)",
            (item['id'], item['name'], item['category'], item['quantity'], 'נמחק')
        )
        # Delete original
        cursor.execute("DELETE FROM shopping_items WHERE id = ?", (item_id,))
    
    conn.commit()
    conn.close()


def clear_bought_items():
    """Clear all bought items and archive them."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get all bought items
    cursor.execute("SELECT * FROM shopping_items WHERE bought = 1")
    items = cursor.fetchall()
    
    # Archive each
    for item in items:
        cursor.execute(
            "INSERT INTO archive_shopping (original_id, name, category, quantity, action) VALUES (?, ?, ?, ?, ?)",
            (item['id'], item['name'], item['category'], item['quantity'], 'נקנה')
        )
    
    # Delete bought items
    cursor.execute("DELETE FROM shopping_items WHERE bought = 1")
    conn.commit()
    conn.close()


def get_archive_shopping():
    """Get archived shopping items."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM archive_shopping ORDER BY archived_at DESC LIMIT 50")
    items = cursor.fetchall()
    conn.close()
    return items


# ============== EXPENSES FUNCTIONS ==============

def get_all_expenses():
    """Get all expenses."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM expenses ORDER BY created_at DESC")
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def add_expense(amount: float, description: str, payer: str, split_type: str, talor_share: float, romi_share: float):
    """Add a new expense."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO expenses (amount, description, payer, split_type, talor_share, romi_share)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (amount, description, payer, split_type, talor_share, romi_share)
    )
    conn.commit()
    conn.close()


def update_expense(expense_id: int, amount: float = None, description: str = None):
    """Update an expense's amount and/or description."""
    conn = get_connection()
    cursor = conn.cursor()
    
    if amount is not None:
        talor_share = amount / 2
        romi_share = amount / 2
        cursor.execute(
            "UPDATE expenses SET amount = ?, talor_share = ?, romi_share = ? WHERE id = ?",
            (amount, talor_share, romi_share, expense_id)
        )
    if description is not None:
        cursor.execute("UPDATE expenses SET description = ? WHERE id = ?", (description, expense_id))
    
    conn.commit()
    conn.close()


def delete_expense(expense_id: int):
    """Delete an expense and archive it."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get expense details first
    cursor.execute("SELECT * FROM expenses WHERE id = ?", (expense_id,))
    expense = cursor.fetchone()
    
    if expense:
        # Archive it
        cursor.execute(
            """INSERT INTO archive_expenses (original_id, amount, description, payer, split_type, action, original_date)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (expense['id'], expense['amount'], expense['description'], expense['payer'], 
             expense['split_type'], 'נמחק', expense['created_at'])
        )
        # Delete original
        cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    
    conn.commit()
    conn.close()


def get_archive_expenses():
    """Get archived expenses."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM archive_expenses ORDER BY archived_at DESC LIMIT 50")
    expenses = cursor.fetchall()
    conn.close()
    return expenses


def calculate_balance():
    """Calculate the balance between Talor and Romi."""
    expenses = get_all_expenses()
    
    talor_owes = 0
    romi_owes = 0
    
    for expense in expenses:
        if expense['payer'] == 'טלאור':
            romi_owes += expense['romi_share']
        else:
            talor_owes += expense['talor_share']
    
    balance = talor_owes - romi_owes
    return balance


# ============== EVENTS FUNCTIONS ==============

# Event emoji mapping
EVENT_EMOJI_KEYWORDS = {
    'מסעדה': '🍽️', 'אוכל': '🍽️', 'ארוחה': '🍽️', 'סושי': '🍣', 'פיצה': '🍕',
    'חברים': '👥', 'מפגש': '👥', 'מסיבה': '🎉', 'יום הולדת': '🎂',
    'עבודה': '💼', 'פגישה': '💼', 'משרד': '🏢',
    'רופא': '🏥', 'בדיקה': '🏥', 'טיפול': '💊',
    'טיסה': '✈️', 'חופשה': '🏖️', 'נסיעה': '🚗', 'טיול': '🥾',
    'קניות': '🛒', 'קניון': '🛍️',
    'ספורט': '⚽', 'חדר כושר': '💪', 'ריצה': '🏃',
    'סרט': '🎬', 'קולנוע': '🎬', 'הופעה': '🎤', 'הצגה': '🎭',
    'לימודים': '📚', 'קורס': '📖', 'שיעור': '✏️',
    'חתונה': '💒', 'אירוסין': '💍',
    'ווטרינר': '🐱', 'חתול': '🐱',
}

def get_event_emoji(title: str, description: str = "") -> str:
    """Get appropriate emoji for an event based on keywords."""
    text = (title + " " + (description or "")).lower()
    for keyword, emoji in EVENT_EMOJI_KEYWORDS.items():
        if keyword in text:
            return emoji
    return "📅"  # Default calendar emoji


def get_all_events():
    """Get all events sorted by date and time."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM events ORDER BY date, time")
    events = cursor.fetchall()
    conn.close()
    return events


def add_event(title: str, date: str, time: str, description: str):
    """Add a new event."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO events (title, date, time, description) VALUES (?, ?, ?, ?)",
        (title, date, time, description)
    )
    conn.commit()
    conn.close()


def delete_event(event_id: int):
    """Delete an event and archive it."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Get event details first
    cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
    event = cursor.fetchone()
    
    if event:
        # Archive it
        cursor.execute(
            """INSERT INTO archive_events (original_id, title, date, time, description, action)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (event['id'], event['title'], event['date'], event['time'], event['description'], 'נמחק/הושלם')
        )
        # Delete original
        cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
    
    conn.commit()
    conn.close()


def get_archive_events():
    """Get archived events."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM archive_events ORDER BY archived_at DESC LIMIT 50")
    events = cursor.fetchall()
    conn.close()
    return events


def get_events_needing_reminder():
    """Get events that need a reminder (1 day before, not yet sent)."""
    conn = get_connection()
    cursor = conn.cursor()
    tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
    cursor.execute(
        "SELECT * FROM events WHERE date = ? AND reminder_sent = 0",
        (tomorrow,)
    )
    events = cursor.fetchall()
    conn.close()
    return events


def mark_reminder_sent(event_id: int):
    """Mark an event's reminder as sent."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE events SET reminder_sent = 1 WHERE id = ?", (event_id,))
    conn.commit()
    conn.close()


def get_urgent_events_count():
    """Get count of events happening today or tomorrow."""
    conn = get_connection()
    cursor = conn.cursor()
    today = datetime.now().date().isoformat()
    tomorrow = (datetime.now().date() + timedelta(days=1)).isoformat()
    cursor.execute(
        "SELECT COUNT(*) FROM events WHERE date IN (?, ?)",
        (today, tomorrow)
    )
    count = cursor.fetchone()[0]
    conn.close()
    return count


# ============== CHORES FUNCTIONS ==============

def get_all_chores():
    """Get all chores."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM chores WHERE done = 0 ORDER BY CASE urgency WHEN 'דחוף' THEN 1 WHEN 'גבוה' THEN 2 WHEN 'רגיל' THEN 3 WHEN 'נמוך' THEN 4 END, due_date")
    chores = cursor.fetchall()
    conn.close()
    return chores


def add_chore(name: str, urgency: str = "רגיל", due_date: str = None):
    """Add a new chore."""
    conn = get_connection()
    cursor = conn.cursor()
    # Allow duplicate names - each chore is unique by ID, not name
    cursor.execute(
        "INSERT INTO chores (name, urgency, due_date) VALUES (?, ?, ?)",
        (name, urgency, due_date)
    )
    conn.commit()
    conn.close()


def mark_chore_done(chore_id: int, user: str):
    """Mark a chore as done and archive it."""
    conn = get_connection()
    cursor = conn.cursor()
    
    done_at = datetime.now().isoformat()
    
    # Get chore details
    cursor.execute("SELECT * FROM chores WHERE id = ?", (chore_id,))
    chore = cursor.fetchone()
    
    if chore:
        # Archive it
        cursor.execute(
            """INSERT INTO archive_chores (original_id, name, urgency, due_date, done_by, done_at, action)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (chore['id'], chore['name'], chore['urgency'], chore['due_date'], user, done_at, 'הושלם')
        )
        # Delete original
        cursor.execute("DELETE FROM chores WHERE id = ?", (chore_id,))
    
    conn.commit()
    conn.close()


def delete_chore(chore_id: int):
    """Delete a chore and archive it."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM chores WHERE id = ?", (chore_id,))
    chore = cursor.fetchone()
    
    if chore:
        cursor.execute(
            """INSERT INTO archive_chores (original_id, name, urgency, due_date, done_by, done_at, action)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (chore['id'], chore['name'], chore['urgency'], chore['due_date'], None, None, 'נמחק')
        )
        cursor.execute("DELETE FROM chores WHERE id = ?", (chore_id,))
    
    conn.commit()
    conn.close()


def get_archive_chores():
    """Get archived chores."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM archive_chores ORDER BY archived_at DESC LIMIT 50")
    chores = cursor.fetchall()
    conn.close()
    return chores


# ============== CAT CARE FUNCTIONS ==============

def get_all_cat_tasks():
    """Get all cat care tasks."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM cat_care ORDER BY id")
    tasks = cursor.fetchall()
    conn.close()
    return tasks


def update_cat_task(task_id: int, user: str):
    """Update cat care task as done now."""
    conn = get_connection()
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
