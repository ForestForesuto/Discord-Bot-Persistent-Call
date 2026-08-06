from flask import Flask
import threading
import os

def keep_alive():
    """Starts a minimal Flask web server in a background thread."""
    app = Flask(__name__)

    @app.route('/')
    def index():
        return "Bot is alive!"

    @app.route('/health')
    def health():
        return "OK", 200

    def run():
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)

    thread = threading.Thread(target=run, daemon=True)
    thread.start()