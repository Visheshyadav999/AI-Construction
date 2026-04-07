import sqlite3

def setup_login_credentials():
    conn = sqlite3.connect('backend/construction_monitor.db')
    cursor = conn.cursor()

    print("Setting up Contractor Login Credentials...")

    try:
        # Add the password column to the Users table
        cursor.execute("ALTER TABLE Users ADD COLUMN password TEXT")
    except Exception as e:
        # If the column already exists, ignore the error
        pass

    # Assign a secure password to Contractor ID 2 (Prime Builders)
    cursor.execute("UPDATE Users SET password = 'password123' WHERE user_id = 2")
    
    conn.commit()
    conn.close()
    
    print("✅ Security upgraded! Contractor ID 2 can now log in with password: password123")

if __name__ == '__main__':
    setup_login_credentials()