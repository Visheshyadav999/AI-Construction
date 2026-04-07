import numpy as np
from sklearn.linear_model import LinearRegression
import sqlite3
import math

def get_db_connection():
    conn = sqlite3.connect('backend/construction_monitor.db')
    conn.row_factory = sqlite3.Row
    return conn

def predict_final_cost(project_id):
    """
    Uses Scikit-Learn Linear Regression to predict the final cost of a project 
    when it reaches 100% completion, based on historical progress and spending.
    """
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Fetch all updates for this specific project
        cursor.execute('''
            SELECT claimed_progress, cost_incurred_today 
            FROM Updates 
            WHERE project_id = ? AND ai_verification_status = 'Verified'
            ORDER BY upload_timestamp ASC
        ''', (project_id,))
        
        updates = cursor.fetchall()
        conn.close()

        # If we have less than 2 verified updates, ML can't draw a line
        if len(updates) < 2:
            return {"status": "insufficient_data", "message": "Need at least 2 verified updates to run ML prediction."}

        # Prepare data for Scikit-Learn
        cumulative_progress = []
        cumulative_cost = []
        
        current_prog = 0
        current_cost = 0

        # We must calculate the cumulative totals to map the trend
        for row in updates:
            current_prog += row['claimed_progress']
            current_cost += row['cost_incurred_today']
            
            # Cap progress at 100 for safety
            safe_prog = min(current_prog, 100) 
            cumulative_progress.append([safe_prog]) # X must be a 2D array for sklearn
            cumulative_cost.append(current_cost)    # y is a 1D array

        # Initialize and train the Machine Learning Model
        model = LinearRegression()
        
        # X = Progress (%), y = Money Spent
        model.fit(cumulative_progress, cumulative_cost)

        # Predict the cost at 100% progress
        predicted_cost = model.predict([[100]])[0]

        return {
            "status": "success",
            "predicted_final_cost": math.ceil(predicted_cost),
            "data_points_analyzed": len(updates)
        }

    except Exception as e:
        print(f"[ML ERROR] {str(e)}")
        return {"status": "error", "message": "ML Engine failed."}