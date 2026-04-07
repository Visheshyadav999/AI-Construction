import sqlite3

def seed_database():
    # Connect to the database we just made
    conn = sqlite3.connect('backend/construction_monitor.db')
    cursor = conn.cursor()

    print("Seeding database with dummy data...")

    try:
        # 1. Insert Dummy Users (Assuming fresh database, these will be ID 1 and 2)
        cursor.execute('''
        INSERT INTO Users (name, email, password_hash, role)
        VALUES 
        ('Apex Clients Ltd', 'client@apexltd.com', 'hashed_pass_123', 'Client'),
        ('Prime Builders', 'builder@prime.com', 'hashed_pass_456', 'Contractor')
        ''')

        # 2. Insert a Dummy Project (Links Client ID 1 and Contractor ID 2)
        cursor.execute('''
        INSERT INTO Projects (client_id, contractor_id, project_name, site_gps_coordinates, estimated_budget, actual_spent, planned_end_date, health_score)
        VALUES 
        (1, 2, 'Tech Park Block A', '28.5355, 77.3910', 5000000.00, 150000.00, '2026-11-30', 95)
        ''')

        # 3. Insert Dummy Stages for the Project (Project ID 1)
        cursor.execute('''
        INSERT INTO Stages (project_id, stage_name, weightage_percentage, status)
        VALUES 
        (1, 'Excavation & Foundation', 25, 'In Progress'),
        (1, 'Structural Framing', 40, 'Pending'),
        (1, 'Roofing & Exterior', 20, 'Pending'),
        (1, 'Interior Finishing', 15, 'Pending')
        ''')

        # 4. Insert a Dummy Update (Contractor ID 2 updating Foundation Stage ID 1)
        cursor.execute('''
        INSERT INTO Updates (project_id, stage_id, uploaded_by, image_file_path, claimed_progress, cost_incurred_today, ai_verification_status)
        VALUES 
        (1, 1, 2, 'uploads/dummy_foundation_pic.jpg', 50, 25000.00, 'Verified')
        ''')

        # Save the changes
        conn.commit()
        print("Dummy data inserted successfully!")

    except sqlite3.IntegrityError:
        print("Error: It looks like this dummy data is already in the database. (Emails must be unique!)")
    
    finally:
        conn.close()

if __name__ == '__main__':
    seed_database()