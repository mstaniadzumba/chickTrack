import config
import sqlite3
from datetime import datetime

def add_batch(start_date, chickens_bought, dead_chicken=0, created_by=None):
    # Extract month-year from start_date for batch naming
    date_obj = datetime.strptime(start_date, '%Y-%m-%d')
    month = date_obj.strftime('%B %Y')  # e.g., "September 2025"
    
    live_chicken = chickens_bought - dead_chicken
    created_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()
    
    cursor.execute("""INSERT INTO batch (month, start_date, chickens_bought, dead_chicken, live_chicken, current_week, created_by, created_at)
                   VALUES (?,?,?,?,?,?,?,?)""", 
                   (month, start_date, chickens_bought, dead_chicken, live_chicken, 1, created_by, created_at))
    
    batch_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return batch_id

def get_all_batches():
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM batch ORDER BY start_date DESC")
    batches = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return batches

def get_batch_by_id(batch_id):
    conn = sqlite3.connect(config.DB_URL)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM batch WHERE id = ?", (batch_id,))
    batch = cursor.fetchone()
    
    if batch:
        # Calculate current week based on days since start
        from datetime import datetime
        start_date = datetime.strptime(batch['start_date'], '%Y-%m-%d')
        current_date = datetime.now()
        days_diff = (current_date - start_date).days
        current_week = (days_diff // 7) + 1
        
        # Update the batch with calculated week
        cursor.execute("UPDATE batch SET current_week = ? WHERE id = ?", (current_week, batch_id))
        conn.commit()
        
        # Return updated batch data
        batch_dict = dict(batch)
        batch_dict['current_week'] = current_week
        conn.close()
        return batch_dict
    
    conn.close()
    return None

def update_batch_stats(batch_id, dead_chicken=None, current_week=None):
    conn = sqlite3.connect(config.DB_URL)
    cursor = conn.cursor()
    
    # Get current batch data
    cursor.execute("SELECT * FROM batch WHERE id = ?", (batch_id,))
    batch = cursor.fetchone()
    
    if batch:
        new_dead = dead_chicken if dead_chicken is not None else batch[4]
        new_week = current_week if current_week is not None else batch[6]
        new_live = batch[3] - new_dead  # chickens_bought - dead_chicken
        
        cursor.execute("""UPDATE batch SET dead_chicken = ?, live_chicken = ?, current_week = ?
                       WHERE id = ?""", (new_dead, new_live, new_week, batch_id))
    
    conn.commit()
    conn.close()
