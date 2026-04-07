import sqlite3

def upgrade_database():
    conn = sqlite3.connect('backend/construction_monitor.db')
    cursor = conn.cursor()

    print("Upgrading database schema for Financial Ledger...")

    try:
        # Add new columns to the existing Updates table
        cursor.execute("ALTER TABLE Updates ADD COLUMN bill_image_path TEXT")
        cursor.execute("ALTER TABLE Updates ADD COLUMN bill_verification_status TEXT DEFAULT 'Pending'")
        conn.commit()
        print("✅ Database upgraded successfully! Financial tracking enabled.")
    except Exception as e:
        print(f"⚠️ Notice: {e} (The columns might already exist!)")
    
    conn.close()

if __name__ == '__main__':
    upgrade_database()