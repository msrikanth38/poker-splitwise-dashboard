# 🎰 Poker Splitwise Dashboard - Deployment Guide

## Features
- ✅ Real-time leaderboard with rankings
- ✅ Point-to-dollar conversion (1000 pts = $5)
- ✅ Complete transaction history with timestamps
- ✅ Player statistics (Winners, Losers, Even)
- ✅ Add/remove players dynamically
- ✅ Responsive design for mobile & desktop
- ✅ Auto-refresh every 5 seconds

## Local Testing

1. Navigate to project folder:
```bash
cd c:\Users\srika\poker
```

2. Activate virtual environment:
```bash
.venv\Scripts\activate
```

3. Run the app:
```bash
python app.py
```

4. Open browser and go to: `http://localhost:5000`

---

## Deploy to FREE Hosting (Render.com)

### Step 1: Create GitHub Repository
1. Go to https://github.com/new
2. Create repository named `poker-dashboard`
3. Clone locally and push your code

```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/poker-dashboard.git
git branch -M main
git push -u origin main
```

### Step 2: Deploy on Render
1. Go to https://render.com (Sign up with GitHub)
2. Click **New** → **Web Service**
3. Connect your GitHub repository
4. Fill in details:
   - **Name:** `poker-dashboard`
   - **Runtime:** Python 3
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn wsgi:app`
   - **Instance Type:** Free (0.5 CPU)

5. Click **Create Web Service**
6. Wait 2-3 minutes for deployment
7. Your URL will be: `https://poker-dashboard.onrender.com`

**Note:** Free tier sleeps after 15 min of inactivity. First request takes 30 sec to wake up.

---

## Alternative: Deploy to Railway.app

1. Go to https://railway.app (Sign up with GitHub)
2. Click **New Project** → **Deploy from GitHub**
3. Select `poker-dashboard` repository
4. Railway auto-detects Python and deploys
5. Your URL will be assigned automatically

---

## Alternative: Deploy to Vercel + Serverless Backend

If you prefer Vercel (even better for free tier):

1. Install Vercel CLI:
```bash
npm i -g vercel
```

2. Deploy:
```bash
vercel
```

Follow prompts and your app will be live in seconds!

---

## Share with Friends

After deployment, share the URL:
- **Example:** `https://poker-dashboard.onrender.com`
- Friends can access from any device, any browser
- No installation needed!

---

## Database

The app uses SQLite (`poker_tracker.db`) which is:
- Created automatically
- Stored on the server
- Persistent across deployments (on Render, Railway)

---

## Usage Tips

1. **Add Players:** Enter name and click "Add Player"
2. **Record Points:** Enter points value and click "+Add"
3. **View History:** See all transactions in real-time
4. **Filter History:** Click player name to see their transactions
5. **Delete Player:** Click "Del" to remove (also removes history)

---

## Troubleshooting

**Issue: App not starting**
- Check `requirements.txt` has all dependencies
- Ensure `wsgi.py` and `Procfile` exist

**Issue: Database not persisting**
- For persistent DB, consider upgrading to paid tier OR
- Use PostgreSQL addon (available on free tier)

**Issue: Slow performance**
- Free tier has limitations
- Upgrade to paid tier for better performance

---

## Customization

### Change Conversion Rate
Edit in `app.py`:
```python
def points_to_dollars(points):
    return round((points / 1000) * 5, 2)  # Change values here
```

### Change Port
In `wsgi.py`:
```python
port = int(os.environ.get('PORT', 5000))
```

### Add More Features
- Export to Excel/CSV
- Email notifications
- Telegram bot integration
- Player statistics graphs

---

## Support

For issues or questions about deployment, check:
- Render Docs: https://render.com/docs
- Railway Docs: https://docs.railway.app
- Flask Docs: https://flask.palletsprojects.com

Enjoy your poker game! 🎰💰
