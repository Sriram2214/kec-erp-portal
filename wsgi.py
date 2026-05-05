import os
import logging
from waitress import serve
from app import create_app, db

# ── Logging setup ─────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler('logs/erp_production.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ── App + DB init ─────────────────────────────────────────────────────────────
app = create_app()

with app.app_context():
    db.create_all()
    # Enable SQLite WAL mode for concurrent reads (handles 1000+ users)
    try:
        db.session.execute(db.text('PRAGMA journal_mode=WAL'))
        db.session.execute(db.text('PRAGMA synchronous=NORMAL'))
        db.session.execute(db.text('PRAGMA cache_size=-64000'))  # 64MB cache
        db.session.execute(db.text('PRAGMA temp_store=MEMORY'))
        db.session.commit()
        log.info('SQLite WAL mode enabled (concurrent-safe)')
    except Exception as e:
        log.warning(f'PRAGMA setup skipped: {e}')

if __name__ == '__main__':
    PORT    = int(os.environ.get('PORT', 5000))
    THREADS = int(os.environ.get('THREADS', 32))  # handles 1000+ concurrent

    print('=' * 60)
    print('  KEC ERP — Production Server')
    print(f'  URL     : http://0.0.0.0:{PORT}')
    print(f'  Threads : {THREADS}  (concurrent users: ~{THREADS * 30})')
    print(f'  DB      : SQLite WAL (concurrent read-safe)')
    print('=' * 60)

    serve(
        app,
        host='0.0.0.0',
        port=PORT,
        threads=THREADS,
        channel_timeout=60,        # 60s request timeout
        cleanup_interval=30,
        connection_limit=1000,     # max open connections
        asyncore_use_poll=True,
    )
