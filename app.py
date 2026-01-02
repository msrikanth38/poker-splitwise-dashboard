from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import sqlite3
import json
from datetime import datetime
import os
import hashlib

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'poker-splitwise-secret-key-2026')
CORS(app, supports_credentials=True)

# Admin credentials (hashed password)
ADMIN_USERNAME = 'sri'
ADMIN_PASSWORD_HASH = hashlib.sha256('srii'.encode()).hexdigest()

# Database setup
DB_FILE = 'poker_tracker.db'

def init_db():
    """Initialize database with tables and sample data"""
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    
    # Players table
    c.execute('''CREATE TABLE IF NOT EXISTS players
                 (id INTEGER PRIMARY KEY, name TEXT UNIQUE, base_total INTEGER DEFAULT 0)''')
    
    # History table
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (id INTEGER PRIMARY KEY, player_id INTEGER, points_added INTEGER, 
                  total_after INTEGER, timestamp TEXT, FOREIGN KEY(player_id) REFERENCES players(id))''')
    
    # Add sample players if database is empty
    c.execute('SELECT COUNT(*) FROM players')
    if c.fetchone()[0] == 0:
        sample_players = [
            ('Chaitu', 0),
            ('Ekku', 0),
            ('Ravi', 0),
            ('Amani', 0),
            ('Hindu', 0),
            ('Shanu', 0),
            ('Jaya', 0),
            ('Vijji', 0),
            ('Kanthu', 0),
            ('Aswini', 0),
            ('Pavani', 0)
        ]
        for name, points in sample_players:
            c.execute('INSERT INTO players (name, base_total) VALUES (?, ?)', (name, points))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def points_to_dollars(points):
    """Convert points to dollars (1000 points = $5)"""
    return round((points / 1000) * 5, 2)

def is_admin():
    """Check if current user is admin"""
    return session.get('is_admin', False)

@app.route('/')
def index():
    """Render main dashboard"""
    return render_template('index.html')

@app.route('/api/auth/login', methods=['POST'])
def login():
    """Admin login"""
    data = request.json
    username = data.get('username', '')
    password = data.get('password', '')
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    if username == ADMIN_USERNAME and password_hash == ADMIN_PASSWORD_HASH:
        session['is_admin'] = True
        session['username'] = username
        return jsonify({'success': True, 'message': 'Login successful', 'isAdmin': True})
    else:
        return jsonify({'success': False, 'message': 'Invalid credentials'}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    """Admin logout"""
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/auth/status', methods=['GET'])
def auth_status():
    """Check authentication status"""
    return jsonify({
        'isAdmin': is_admin(),
        'username': session.get('username', None)
    })

@app.route('/api/players', methods=['GET'])
def get_players():
    """Get all players with current totals"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT id, name, base_total FROM players ORDER BY base_total DESC')
    players = c.fetchall()
    
    players_list = []
    for player in players:
        dollar_amount = points_to_dollars(player['base_total'])
        status = 'WON' if player['base_total'] > 0 else 'LOST' if player['base_total'] < 0 else 'EVEN'
        
        players_list.append({
            'id': player['id'],
            'name': player['name'],
            'base_total': player['base_total'],
            'dollar_amount': dollar_amount,
            'status': status
        })
    
    conn.close()
    return jsonify(players_list)

@app.route('/api/players', methods=['POST'])
def add_player():
    """Add new player (Admin only)"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    name = data.get('name', '').strip()
    
    if not name:
        return jsonify({'error': 'Player name required'}), 400
    
    conn = get_db_connection()
    c = conn.cursor()
    
    try:
        c.execute('INSERT INTO players (name, base_total) VALUES (?, ?)', (name, 0))
        conn.commit()
        player_id = c.lastrowid
        conn.close()
        
        return jsonify({
            'id': player_id,
            'name': name,
            'base_total': 0,
            'dollar_amount': 0,
            'status': 'EVEN'
        }), 201
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'error': 'Player already exists'}), 400

@app.route('/api/players/<int:player_id>/points', methods=['POST'])
def add_points(player_id):
    """Add points to a player (Admin only)"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    data = request.json
    points_added = data.get('points', 0)
    
    if points_added == 0:
        return jsonify({'error': 'Points cannot be 0'}), 400
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get current total
    c.execute('SELECT base_total FROM players WHERE id = ?', (player_id,))
    player = c.fetchone()
    
    if not player:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404
    
    new_total = player['base_total'] + points_added
    timestamp = datetime.now().isoformat()
    
    # Update player total
    c.execute('UPDATE players SET base_total = ? WHERE id = ?', (new_total, player_id))
    
    # Record in history
    c.execute('INSERT INTO history (player_id, points_added, total_after, timestamp) VALUES (?, ?, ?, ?)',
              (player_id, points_added, new_total, timestamp))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'points_added': points_added,
        'new_total': new_total,
        'dollar_amount': points_to_dollars(new_total),
        'timestamp': timestamp
    }), 201

@app.route('/api/history', methods=['GET'])
def get_history():
    """Get complete history for all players"""
    player_name = request.args.get('player_name')
    
    conn = get_db_connection()
    c = conn.cursor()
    
    if player_name:
        query = '''SELECT h.id, p.name, h.points_added, h.total_after, h.timestamp
                   FROM history h
                   JOIN players p ON h.player_id = p.id
                   WHERE p.name = ?
                   ORDER BY h.timestamp DESC'''
        c.execute(query, (player_name,))
    else:
        query = '''SELECT h.id, p.name, h.points_added, h.total_after, h.timestamp
                   FROM history h
                   JOIN players p ON h.player_id = p.id
                   ORDER BY h.timestamp DESC'''
        c.execute(query)
    
    history = c.fetchall()
    conn.close()
    
    history_list = []
    for record in history:
        history_list.append({
            'id': record['id'],
            'player_name': record['name'],
            'points_added': record['points_added'],
            'total_after': record['total_after'],
            'dollar_after': points_to_dollars(record['total_after']),
            'timestamp': record['timestamp']
        })
    
    return jsonify(history_list)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get game statistics"""
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('SELECT COUNT(*) as total_players FROM players')
    total_players = c.fetchone()['total_players']
    
    c.execute('SELECT COUNT(*) as total_transactions FROM history')
    total_transactions = c.fetchone()['total_transactions']
    
    c.execute('SELECT SUM(base_total) as total_points FROM players')
    total_points = c.fetchone()['total_points'] or 0
    
    c.execute('SELECT base_total FROM players WHERE base_total > 0')
    winners = len(c.fetchall())
    
    c.execute('SELECT base_total FROM players WHERE base_total < 0')
    losers = len(c.fetchall())
    
    conn.close()
    
    return jsonify({
        'total_players': total_players,
        'total_transactions': total_transactions,
        'total_points': total_points,
        'total_dollars': points_to_dollars(total_points),
        'winners': winners,
        'losers': losers,
        'even': total_players - winners - losers
    })

@app.route('/api/players/<int:player_id>', methods=['DELETE'])
def delete_player(player_id):
    """Delete a player and their history (Admin only)"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = get_db_connection()
    c = conn.cursor()
    
    c.execute('DELETE FROM history WHERE player_id = ?', (player_id,))
    c.execute('DELETE FROM players WHERE id = ?', (player_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/api/history/<int:history_id>', methods=['DELETE'])
def delete_history_entry(history_id):
    """Delete a single history entry and update player total (Admin only)"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get the history entry details
    c.execute('SELECT player_id, points_added FROM history WHERE id = ?', (history_id,))
    history = c.fetchone()
    
    if not history:
        conn.close()
        return jsonify({'error': 'History entry not found'}), 404
    
    player_id = history['player_id']
    points_to_reverse = history['points_added']
    
    # Update player total (reverse the points)
    c.execute('UPDATE players SET base_total = base_total - ? WHERE id = ?', 
              (points_to_reverse, player_id))
    
    # Delete the history entry
    c.execute('DELETE FROM history WHERE id = ?', (history_id,))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'reversed_points': points_to_reverse}), 200

@app.route('/api/history/clear', methods=['DELETE'])
def clear_all_history():
    """Clear all history (Admin only)"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM history')
    conn.commit()
    conn.close()
    return jsonify({'success': True}), 200

@app.route('/api/players/<int:player_id>/details', methods=['GET'])
def get_player_details(player_id):
    """Get complete player details with all history"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get player info
    c.execute('SELECT id, name, base_total FROM players WHERE id = ?', (player_id,))
    player = c.fetchone()
    
    if not player:
        conn.close()
        return jsonify({'error': 'Player not found'}), 404
    
    # Get all history for this player (including id for deletion)
    c.execute('''SELECT id, points_added, total_after, timestamp 
                 FROM history WHERE player_id = ? 
                 ORDER BY timestamp DESC''', (player_id,))
    history = c.fetchall()
    
    # Calculate stats
    total_wins = sum(1 for h in history if h['points_added'] > 0)
    total_losses = sum(1 for h in history if h['points_added'] < 0)
    biggest_win = max([h['points_added'] for h in history] + [0])
    biggest_loss = min([h['points_added'] for h in history] + [0])
    total_games = len(history)
    
    conn.close()
    
    return jsonify({
        'id': player['id'],
        'name': player['name'],
        'base_total': player['base_total'],
        'dollar_amount': points_to_dollars(player['base_total']),
        'status': 'WON' if player['base_total'] > 0 else 'LOST' if player['base_total'] < 0 else 'EVEN',
        'stats': {
            'total_games': total_games,
            'total_wins': total_wins,
            'total_losses': total_losses,
            'biggest_win': biggest_win,
            'biggest_loss': biggest_loss,
            'win_rate': round((total_wins / total_games * 100), 1) if total_games > 0 else 0
        },
        'history': [{
            'id': h['id'],
            'points_added': h['points_added'],
            'total_after': h['total_after'],
            'dollar_after': points_to_dollars(h['total_after']),
            'timestamp': h['timestamp']
        } for h in history]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
