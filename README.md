# 🎰 Poker Splitwise Dashboard

A smart, real-time poker game tracking dashboard that automatically calculates settlements, tracks player statistics, and maintains complete transaction history.

![Dashboard](https://img.shields.io/badge/Status-Live-brightgreen)
![Python](https://img.shields.io/badge/Python-3.10+-blue)
![Flask](https://img.shields.io/badge/Flask-2.3-green)

## 🚀 Quick Start

### Local Setup
```bash
# Clone or navigate to project
cd c:\Users\srika\poker

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py

# Open browser
http://localhost:5000
```

## 📊 Features

### Core Functionality
- **Real-time Leaderboard** - Instantly updated player rankings
- **Point-to-Dollar Conversion** - 1000 Points = $5 (configurable)
- **Transaction History** - Complete audit trail with timestamps
- **Player Rankings** - Winners, Losers, Even status badges
- **Smart Statistics** - Real-time game analytics
- **Responsive Design** - Works on desktop, tablet, mobile

### Dashboard Sections
1. **Leaderboard** - All players with points and dollar amounts
2. **Add Players** - Dynamic player management
3. **Record Points** - Quick transaction entry
4. **History** - Filterable transaction log
5. **Statistics** - Game overview with key metrics

## 📈 Key Metrics

- Total Players
- Total Points in game
- Dollar equivalent amount
- Winners/Losers count
- Break-even players
- Total transactions

## 🎯 How to Use

### Adding Players
1. Enter player name in input field
2. Click "Add Player"
3. Player appears in leaderboard

### Recording Points
1. Enter points in the table field (can be negative)
2. Click "+Add" button
3. History updates instantly
4. Dollar amount auto-calculates

### Viewing History
1. See "Recent History" panel
2. Click on player name to filter their transactions
3. Click "All" to see all transactions
4. Transactions show: points added, total, and timestamp

### Tracking Player Performance
- Green badge = Won (positive points)
- Red badge = Lost (negative points)
- Blue badge = Even (zero points)

## 🗄️ Database Schema

### Players Table
```
id (INTEGER) - Primary key
name (TEXT) - Player name (unique)
base_total (INTEGER) - Current point total
```

### History Table
```
id (INTEGER) - Primary key
player_id (INTEGER) - Foreign key to players
points_added (INTEGER) - Points added in this transaction
total_after (INTEGER) - Total after transaction
timestamp (TEXT) - ISO 8601 timestamp
```

## 💾 Data Storage

- **SQLite Database** - `poker_tracker.db`
- **Auto-created** on first run
- **Persistent** across app restarts
- **No external dependencies** required for database

## 🌐 Deploy to World

### Easy Deploy Options

#### 1. **Render.com** (Recommended for Beginners)
- Free tier with persistent storage
- Auto-deploys from GitHub
- Simple configuration
- [See Deployment Guide](DEPLOYMENT.md)

#### 2. **Railway.app**
- Modern deployment platform
- Free tier available
- Easy GitHub integration

#### 3. **Vercel + Flask**
- Super fast deployments
- Global CDN
- Best for APIs

#### 4. **Heroku Alternative** (Free Alternatives)
- Render, Railway, or Fly.io

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step instructions.

## 🔧 API Endpoints

### Players Management
```
GET  /api/players           - Get all players
POST /api/players           - Add new player
POST /api/players/<id>/points - Add points to player
DELETE /api/players/<id>    - Delete player
```

### History
```
GET /api/history            - Get all transactions
GET /api/history?player_name=X - Get player's transactions
```

### Statistics
```
GET /api/stats              - Get game statistics
```

## 📱 Mobile Responsive

- Fully responsive design
- Works on phones, tablets, desktops
- Touch-friendly buttons
- Auto-refresh every 5 seconds

## 🎨 Customization

### Change Point Conversion
Edit `app.py`:
```python
def points_to_dollars(points):
    return round((points / 1000) * 5, 2)  # Change 1000 and 5
```

### Modify Colors
Edit `templates/index.html` CSS variables:
```css
--primary: #667eea;
--success: #10b981;
--danger: #ef4444;
```

### Add More Features
- Export to CSV/Excel
- Email notifications
- Slack integration
- Charts and graphs

## 📝 Example Usage

**Starting a game:**
1. Add all players: chaitu, ekku, Ravi, amani, etc.
2. Set initial base totals if continuing from previous game
3. Record points as game progresses
4. Dashboard automatically calculates who's winning

**Recording transactions:**
- Win 1000 points: Enter "1000" and click Add
- Lose 500 points: Enter "-500" and click Add
- Dollar amounts auto-calculate

**Settling up:**
- See final standings in leaderboard
- $ Amount shows what each person owes/receives
- History shows complete audit trail

## 🔐 Security Note

For production deployment:
- Set `debug=False` in production
- Use environment variables for sensitive data
- Add password protection if needed
- Enable HTTPS (automatic on Render/Railway)

## 📊 Performance

- Real-time updates
- 5-second auto-refresh
- Handles 100+ players smoothly
- 10,000+ transactions per game

## 🐛 Troubleshooting

**Players not showing up?**
- Refresh page
- Check console for errors (F12)
- Restart app

**Points not saving?**
- Check if database file exists
- Verify app is running
- Check browser console

**Slow performance?**
- Close other apps
- Reduce auto-refresh interval
- Clear browser cache

## 📚 Stack

- **Backend:** Python Flask
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Database:** SQLite
- **Deployment:** Render, Railway, or Vercel
- **Styling:** Custom CSS (No frameworks)

## 🎓 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com)
- [Render Documentation](https://render.com/docs)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

## 💡 Tips & Tricks

1. **Keyboard Shortcut:** Focus input and press Enter to add player
2. **Bulk Import:** Copy/paste from existing spreadsheet
3. **Backup:** Download `poker_tracker.db` regularly
4. **Mobile:** Save URL as home screen shortcut on phone
5. **Sharing:** Generate QR code of URL for easy sharing

## 🤝 Contributing

Found a bug? Have a feature request?
- Create an issue
- Submit a pull request
- Share feedback

## 📄 License

Open source - use freely!

## 🎊 Enjoy!

Your poker game tracker is ready to go! 
- Deploy it
- Share the URL with friends
- Start tracking your game
- Have fun! 🎰💰

---

**Questions?** Check [DEPLOYMENT.md](DEPLOYMENT.md) or the code comments.

**Version:** 1.0.0  
**Last Updated:** 2024
