from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import json
from datetime import datetime
import os
import hashlib

# Try to import psycopg2 for PostgreSQL, fallback to sqlite3
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    HAS_POSTGRES = True
except ImportError:
    HAS_POSTGRES = False

import sqlite3

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'poker-splitwise-secret-key-2026')
CORS(app, supports_credentials=True)

# Admin credentials (hashed password)
ADMIN_USERNAME = 'sri'
ADMIN_PASSWORD_HASH = hashlib.sha256('srii'.encode()).hexdigest()

# Database setup - Use PostgreSQL if DATABASE_URL is set, otherwise SQLite
DATABASE_URL = os.environ.get('DATABASE_URL')
DB_FILE = 'poker_tracker.db'

def get_db_connection():
    """Get database connection - PostgreSQL in production, SQLite locally"""
    if DATABASE_URL and HAS_POSTGRES:
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    else:
        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        return conn

def execute_query(query, params=(), fetch=False, fetchone=False, commit=False):
    """Execute a query with proper database handling"""
    conn = get_db_connection()
    is_postgres = DATABASE_URL and HAS_POSTGRES
    
    if is_postgres:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Convert ? placeholders to %s for PostgreSQL
        query = query.replace('?', '%s')
    else:
        cur = conn.cursor()
    
    try:
        cur.execute(query, params)
        
        if fetch:
            result = cur.fetchall()
            if not is_postgres:
                # Convert sqlite3.Row to dict
                result = [dict(row) for row in result]
            conn.close()
            return result
        elif fetchone:
            result = cur.fetchone()
            if result and not is_postgres:
                result = dict(result)
            conn.close()
            return result
        elif commit:
            conn.commit()
            lastrowid = cur.lastrowid if not is_postgres else None
            if is_postgres:
                # For PostgreSQL, we need to get the last inserted ID differently
                try:
                    cur.execute("SELECT lastval()")
                    lastrowid = cur.fetchone()['lastval']
                except:
                    lastrowid = None
            conn.close()
            return lastrowid
        else:
            conn.close()
            return None
    except Exception as e:
        conn.close()
        raise e

def init_db():
    """Initialize database with tables and sample data"""
    is_postgres = DATABASE_URL and HAS_POSTGRES
    conn = get_db_connection()
    
    if is_postgres:
        cur = conn.cursor()
        # PostgreSQL syntax
        cur.execute('''CREATE TABLE IF NOT EXISTS players
                     (id SERIAL PRIMARY KEY, name TEXT UNIQUE, base_total INTEGER DEFAULT 0)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS history
                     (id SERIAL PRIMARY KEY, player_id INTEGER REFERENCES players(id), 
                      points_added INTEGER, total_after INTEGER, timestamp TEXT)''')
    else:
        cur = conn.cursor()
        # SQLite syntax
        cur.execute('''CREATE TABLE IF NOT EXISTS players
                     (id INTEGER PRIMARY KEY, name TEXT UNIQUE, base_total INTEGER DEFAULT 0)''')
        cur.execute('''CREATE TABLE IF NOT EXISTS history
                     (id INTEGER PRIMARY KEY, player_id INTEGER, points_added INTEGER, 
                      total_after INTEGER, timestamp TEXT, FOREIGN KEY(player_id) REFERENCES players(id))''')
    
    # Add sample players if database is empty
    cur.execute('SELECT COUNT(*) as count FROM players')
    result = cur.fetchone()
    count = result[0] if isinstance(result, tuple) else result.get('count', result[0])
    
    if count == 0:
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
            if is_postgres:
                cur.execute('INSERT INTO players (name, base_total) VALUES (%s, %s)', (name, points))
            else:
                cur.execute('INSERT INTO players (name, base_total) VALUES (?, ?)', (name, points))
    
    conn.commit()
    conn.close()

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
    players = execute_query('SELECT id, name, base_total FROM players ORDER BY base_total DESC', fetch=True)
    
    players_list = []
    for player in players:
        base_total = player['base_total'] or 0
        dollar_amount = points_to_dollars(base_total)
        status = 'WON' if base_total > 0 else 'LOST' if base_total < 0 else 'EVEN'
        
        players_list.append({
            'id': player['id'],
            'name': player['name'],
            'base_total': base_total,
            'dollar_amount': dollar_amount,
            'status': status
        })
    
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
    
    try:
        is_postgres = DATABASE_URL and HAS_POSTGRES
        if is_postgres:
            conn = get_db_connection()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            cur.execute('INSERT INTO players (name, base_total) VALUES (%s, %s) RETURNING id', (name, 0))
            result = cur.fetchone()
            player_id = result['id']
            conn.commit()
            conn.close()
        else:
            player_id = execute_query('INSERT INTO players (name, base_total) VALUES (?, ?)', (name, 0), commit=True)
        
        return jsonify({
            'id': player_id,
            'name': name,
            'base_total': 0,
            'dollar_amount': 0,
            'status': 'EVEN'
        }), 201
    except Exception as e:
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
    
    # Get current total
    player = execute_query('SELECT base_total FROM players WHERE id = ?', (player_id,), fetchone=True)
    
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    new_total = (player['base_total'] or 0) + points_added
    timestamp = datetime.now().isoformat()
    
    # Update player total
    execute_query('UPDATE players SET base_total = ? WHERE id = ?', (new_total, player_id), commit=True)
    
    # Record in history
    execute_query('INSERT INTO history (player_id, points_added, total_after, timestamp) VALUES (?, ?, ?, ?)',
              (player_id, points_added, new_total, timestamp), commit=True)
    
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
    
    if player_name:
        history = execute_query('''SELECT h.id, p.name, h.points_added, h.total_after, h.timestamp
                   FROM history h
                   JOIN players p ON h.player_id = p.id
                   WHERE p.name = ?
                   ORDER BY h.timestamp DESC''', (player_name,), fetch=True)
    else:
        history = execute_query('''SELECT h.id, p.name, h.points_added, h.total_after, h.timestamp
                   FROM history h
                   JOIN players p ON h.player_id = p.id
                   ORDER BY h.timestamp DESC''', fetch=True)
    
    history_list = []
    for record in history:
        history_list.append({
            'id': record['id'],
            'player_name': record['name'],
            'points_added': record['points_added'],
            'total_after': record['total_after'],
            'dollar_after': points_to_dollars(record['total_after'] or 0),
            'timestamp': record['timestamp']
        })
    
    return jsonify(history_list)

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get game statistics"""
    total_players_result = execute_query('SELECT COUNT(*) as total_players FROM players', fetchone=True)
    total_players = total_players_result['total_players'] if total_players_result else 0
    
    total_trans_result = execute_query('SELECT COUNT(*) as total_transactions FROM history', fetchone=True)
    total_transactions = total_trans_result['total_transactions'] if total_trans_result else 0
    
    total_points_result = execute_query('SELECT SUM(base_total) as total_points FROM players', fetchone=True)
    total_points = (total_points_result['total_points'] or 0) if total_points_result else 0
    
    winners_result = execute_query('SELECT COUNT(*) as count FROM players WHERE base_total > 0', fetchone=True)
    winners = winners_result['count'] if winners_result else 0
    
    losers_result = execute_query('SELECT COUNT(*) as count FROM players WHERE base_total < 0', fetchone=True)
    losers = losers_result['count'] if losers_result else 0
    
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
    
    execute_query('DELETE FROM history WHERE player_id = ?', (player_id,), commit=True)
    execute_query('DELETE FROM players WHERE id = ?', (player_id,), commit=True)
    
    return jsonify({'success': True}), 200

@app.route('/api/history/<int:history_id>', methods=['DELETE'])
def delete_history_entry(history_id):
    """Delete a single history entry and update player total (Admin only)"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    # Get the history entry details
    history = execute_query('SELECT player_id, points_added FROM history WHERE id = ?', (history_id,), fetchone=True)
    
    if not history:
        return jsonify({'error': 'History entry not found'}), 404
    
    player_id = history['player_id']
    points_to_reverse = history['points_added']
    
    # Update player total (reverse the points)
    execute_query('UPDATE players SET base_total = base_total - ? WHERE id = ?', 
              (points_to_reverse, player_id), commit=True)
    
    # Delete the history entry
    execute_query('DELETE FROM history WHERE id = ?', (history_id,), commit=True)
    
    return jsonify({'success': True, 'reversed_points': points_to_reverse}), 200

@app.route('/api/history/clear', methods=['DELETE'])
def clear_all_history():
    """Clear all history (Admin only)"""
    if not is_admin():
        return jsonify({'error': 'Admin access required'}), 403
    
    execute_query('DELETE FROM history', commit=True)
    return jsonify({'success': True}), 200

@app.route('/api/players/<int:player_id>/details', methods=['GET'])
def get_player_details(player_id):
    """Get complete player details with all history"""
    # Get player info
    player = execute_query('SELECT id, name, base_total FROM players WHERE id = ?', (player_id,), fetchone=True)
    
    if not player:
        return jsonify({'error': 'Player not found'}), 404
    
    # Get all history for this player (including id for deletion)
    history = execute_query('''SELECT id, points_added, total_after, timestamp 
                 FROM history WHERE player_id = ? 
                 ORDER BY timestamp DESC''', (player_id,), fetch=True)
    
    # Calculate stats
    total_wins = sum(1 for h in history if h['points_added'] > 0)
    total_losses = sum(1 for h in history if h['points_added'] < 0)
    biggest_win = max([h['points_added'] for h in history] + [0])
    biggest_loss = min([h['points_added'] for h in history] + [0])
    total_games = len(history)
    
    base_total = player['base_total'] or 0
    
    return jsonify({
        'id': player['id'],
        'name': player['name'],
        'base_total': base_total,
        'dollar_amount': points_to_dollars(base_total),
        'status': 'WON' if base_total > 0 else 'LOST' if base_total < 0 else 'EVEN',
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
            'dollar_after': points_to_dollars(h['total_after'] or 0),
            'timestamp': h['timestamp']
        } for h in history]
    })

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5000)
