import sqlite3
import random

def fix_city_mall():
    conn = sqlite3.connect('backend/construction_monitor.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    print("Analyzing your actual database schema...")

    # 1. Get the exact columns YOUR database uses
    cursor.execute("PRAGMA table_info(Projects)")
    columns = [col['name'] for col in cursor.fetchall()]

    # 2. Check if Project 2 exists
    cursor.execute("SELECT * FROM Projects WHERE project_id = 2")
    if not cursor.fetchone():
        
        # Build a dynamic insert based ONLY on the columns you actually have
        insert_cols = []
        insert_vals = []
        
        if 'project_id' in columns:
            insert_cols.append('project_id'); insert_vals.append(2)
        if 'project_name' in columns:
            insert_cols.append('project_name'); insert_vals.append('City Mall Renovation')
        if 'client_name' in columns:
            insert_cols.append('client_name'); insert_vals.append('City Corp')
        if 'client_id' in columns:
            insert_cols.append('client_id'); insert_vals.append(1)
        if 'contractor_name' in columns:
            insert_cols.append('contractor_name'); insert_vals.append('Prime Builders')
        if 'contractor_id' in columns:
            insert_cols.append('contractor_id'); insert_vals.append(2)
        if 'estimated_budget' in columns:
            insert_cols.append('estimated_budget'); insert_vals.append(8500000)
        if 'actual_spent' in columns:
            insert_cols.append('actual_spent'); insert_vals.append(0)
        if 'health_score' in columns:
            insert_cols.append('health_score'); insert_vals.append(0)

        placeholders = ', '.join(['?'] * len(insert_vals))
        cols_str = ', '.join(insert_cols)
        
        query = f"INSERT INTO Projects ({cols_str}) VALUES ({placeholders})"
        cursor.execute(query, tuple(insert_vals))
        print("✅ Master file for 'City Mall Renovation' officially created!")

    # 3. Clear orphaned data
    cursor.execute("DELETE FROM Updates WHERE project_id = 2")

    # 4. Inject the perfect presentation data
    cumulative_progress = 0
    total_spent = 0
    
    for i in range(1, 26):
        progress_step = random.randint(2, 5)
        cumulative_progress += progress_step
        if cumulative_progress > 100: 
            cumulative_progress = 100
            
        cost_today = random.uniform(75000, 95000) * progress_step
        total_spent += cost_today
        
        cursor.execute('''
            INSERT INTO Updates (project_id, stage_id, uploaded_by, image_file_path, claimed_progress, cost_incurred_today, ai_verification_status)
            VALUES (2, 1, 2, 'uploads/simulated_image.jpg', ?, ?, 'Verified')
        ''', (cumulative_progress, round(cost_today, 2)))
        
        if cumulative_progress == 100: 
            break

    # 5. Update the master project totals
    cursor.execute("UPDATE Projects SET health_score = ?, actual_spent = ? WHERE project_id = 2", (cumulative_progress, round(total_spent, 2)))
    
    conn.commit()
    conn.close()
    print("✅ Data successfully linked! City Mall is ready for the presentation.")

if __name__ == '__main__':
    fix_city_mall()