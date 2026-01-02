import os
import logging
from app import app, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database on startup (for production deployment)
try:
    logger.info("Starting database initialization...")
    init_db()
    logger.info("Database initialization complete!")
except Exception as e:
    logger.error(f"Database initialization failed: {e}")
    # Continue anyway - the app might still work

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
