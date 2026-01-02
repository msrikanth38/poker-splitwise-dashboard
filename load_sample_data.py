"""
Sample data loader for testing the poker dashboard
Run this to populate the database with test players and transactions
"""

import sqlite3
from app import init_db, points_to_dollars
from datetime import datetime, timedelta

def load_sample_data():
    """Load sample data matching your poker table screenshot"""
    
    init_db()
    conn = sqlite3.connect('poker_tracker.db')
    c = conn.cursor()
    
    # Clear existing data
    c.execute('DELETE FROM history')
    c.execute('DELETE FROM players')
    
    # Sample players with their point totals from your screenshot
    players_data = [
        ('chaitu', 5140),
        ('ekku', 1500),
        ('Ravi', 700),
        ('amani', 0),
        ('hindu', 0),
        ('shanu', 0),
        ('jaya', -430),
        ('vijji', -750),
        ('kanthu', -1000),
        ('aswini', -1200),
        ('pavani', -4000),
    ]
    
    # Insert players
    for name, points in players_data:
        c.execute('INSERT INTO players (name, base_total) VALUES (?, ?)', (name, points))
        player_id = c.lastrowid
        
        # Add sample history transactions
        base_time = datetime.now() - timedelta(hours=2)
        
        # Generate sample transaction for each player
        if points != 0:
            # Add transaction that led to this total
            transaction_points = points if points > 0 else points
            c.execute('''INSERT INTO history 
                        (player_id, points_added, total_after, timestamp) 
                        VALUES (?, ?, ?, ?)''',
                     (player_id, transaction_points, points, base_time.isoformat()))
    
    conn.commit()
    conn.close()
    print("✅ Sample data loaded successfully!")
    print("\nPlayers added:")
    print(f"  Winners: chaitu (5140), ekku (1500), Ravi (700)")
    print(f"  Even: amani, hindu, shanu")
    print(f"  Losers: jaya (-430), vijji (-750), kanthu (-1000), aswini (-1200), pavani (-4000)")
    print("\nTotal: 3340 points = $16.70")
    print("\nYour dashboard is ready to test!")
    print("Run: python app.py")
    print("Visit: http://localhost:5000")

if __name__ == '__main__':
    load_sample_data()
