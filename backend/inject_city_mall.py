import sqlite3
import random

def inject_city_mall_data():
    conn = sqlite3.connect('backend/construction_monitor.db')
    cursor = conn.cursor()

    print("Generating presentation data for City Mall Renovation (Project ID: 2)...")

    cumulative_progress = 0
    
    # Generate 25 steady updates
    for i in range(1, 26):
        # Progress goes up by 2% to 5% each update
        progress_step = random.randint(2, 5)
        cumulative_progress += progress_step
        if cumulative_progress > 100:
            cumulative_progress = 100
            
        # The budget is ₹8,500,000. 1% is roughly ₹85,000. 
        # We simulate them spending money matching their progress.
        cost_today = random.uniform(75000, 95000) * progress_step
        
        # Insert into database
        cursor.execute('''
            INSERT INTO Updates (project_id, stage_id, uploaded_by, image_file_path, claimed_progress, cost_incurred_today, ai_verification_status)
            VALUES (2, 1, 2, 'uploads/simulated_image.jpg', ?, ?, 'Verified')
        ''', (cumulative_progress, round(cost_today, 2)))

        if cumulative_progress == 100:
            break

    # Update the master Projects table to reflect the total spent and current progress
    cursor.execute("UPDATE Projects SET health_score = ? WHERE project_id = 2", (cumulative_progress,))
    
    conn.commit()
    conn.close()
    print("✅ High-quality presentation data injected for City Mall!")

if __name__ == '__main__':
    inject_city_mall_data()