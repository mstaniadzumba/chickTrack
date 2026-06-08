import config
import sqlite3
from datetime import datetime


def log_audit(batch_id, record_type, record_id, action, changes, user_name):
    """Add one permanent history entry. Never updated or removed afterwards."""
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()

    cursor.execute("""INSERT INTO audit_log (batch_id, record_type, record_id, action, changes, user_name, created_at)
                   VALUES (?,?,?,?,?,?,?)""",
                   (batch_id, record_type, record_id, action, changes, user_name, created_at))

    conn.commit()
    conn.close()


def get_audit_by_batch(batch_id=None):
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    if batch_id:
        cursor.execute("SELECT * FROM audit_log WHERE batch_id = ? ORDER BY id DESC", (batch_id,))
    else:
        cursor.execute("SELECT * FROM audit_log ORDER BY id DESC")

    entries = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return entries


def diff_changes(fields):
    """Build a readable 'old -> new' summary for fields that actually changed.

    `fields` is a list of (label, old_value, new_value) tuples.
    Returns e.g. "Amount paid: 0 → 2000; Chickens: 5 → 8" or "No changes".
    """
    parts = []
    for label, old, new in fields:
        # Compare as strings so 5 and "5" don't look like a change.
        if str(old) != str(new):
            parts.append(f"{label}: {old} → {new}")
    return "; ".join(parts) if parts else "No changes"
