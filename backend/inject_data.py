import sqlite3
import random

def inject_realistic_data():
    conn = sqlite3.connect('backend/construction_monitor.db')
    cursor = conn.cursor()

    print("Injecting 50 realistic project updates for ML training...")

    # We will generate 50 historical updates for Project ID 1
    for i in range(50):
        # The contractor completes between 1% and 3% of work per update
        claimed_progress = random.randint(1, 3)
        
        # The work costs between ₹80,000 and ₹110,000 per update
        # This simulates a steady burn rate towards the ₹5,000,000 budget
        cost_today = random.uniform(80000, 110000)
        
        # Insert into the database (Must be 'Verified' so the ML uses it!)
        cursor.execute('''
            INSERT INTO Updates (project_id, stage_id, uploaded_by, image_file_path, claimed_progress, cost_incurred_today, ai_verification_status)
            VALUES (1, 1, 2, 'uploads/simulated_image.jpg', ?, ?, 'Verified')
        ''', (claimed_progress, round(cost_today, 2)))

    conn.commit()
    conn.close()
    print("✅ 50 realistic updates injected successfully! Your ML model is now fully fed.")

if __name__ == '__main__':
    inject_realistic_data()